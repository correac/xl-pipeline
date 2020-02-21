"""
Creates detailed images of the first 100 haloes in dark
matter, stars, and gas column density. This doesn't do any rotation,
just makes projected images of them in the x, y plane.

Give it the snapshot path as the first arugment, and the
velociraptor catalogue path as the second. As the final argument
it takes the output directory.
"""

from velociraptor.swift.swift import to_swiftsimio_dataset
from velociraptor.particles import load_groups
from velociraptor import load

from swiftsimio.visualisation.projection import project_pixel_grid
from swiftsimio.visualisation.slice import kernel_gamma
from swiftsimio.visualisation.smoothing_length_generation import (
    generate_smoothing_lengths,
)

import sys
import unyt

snapshot_path = sys.argv[1]
velociraptor_base_name = sys.argv[2]
output_path = sys.argv[3]

halo_ids = range(0, 100)

velociraptor_properties = velociraptor_base_name
velociraptor_groups = velociraptor_base_name.replace("properties", "catalog_groups")

filenames = {
    "parttypes_filename": velociraptor_base_name.replace(
        "properties", "catalog_partypes"
    ),
    "particles_filename": velociraptor_base_name.replace(
        "properties", "catalog_particles"
    ),
    "unbound_parttypes_filename": velociraptor_base_name.replace(
        "properties", "catalog_partypes.unbound"
    ),
    "unbound_particles_filename": velociraptor_base_name.replace(
        "properties", "catalog_particles.unbound"
    ),
}

catalogue = load(velociraptor_properties)
groups = load_groups(velociraptor_groups, catalogue)

# Let's make an image of those particles!
import matplotlib.pyplot as plt
import numpy as np

from swiftsimio.visualisation.sphviewer import SPHViewerWrapper
from matplotlib.colors import LogNorm

particle_type_cmap = {
    "gas": "inferno",
    "stars": "bone",
    "dark_matter": "plasma",
}


def latex_float(f):
    float_str = "{0:.2g}".format(f)
    if "e" in float_str:
        base, exponent = float_str.split("e")
        return r"{0} \times 10^{{{1}}}".format(base, int(exponent))
    else:
        return float_str


for halo_id in halo_ids:
    particles, unbound_particles = groups.extract_halo(halo_id, filenames=filenames)

    halo_mass = catalogue.masses.mass_200mean[halo_id].to("Solar_Mass")
    stellar_mass = catalogue.apertures.mass_star_30_kpc[halo_id].to("Solar_Mass")

    # This reads particles using the cell metadata that are around our halo
    data = to_swiftsimio_dataset(particles, snapshot_path, generate_extra_mask=False)

    for particle_type, cmap in particle_type_cmap.items():
        particle_data = getattr(data, particle_type)

        x = particles.x / data.metadata.a
        y = particles.y / data.metadata.a
        z = particles.z / data.metadata.a
        r_size = particles.r_size * 0.5 / data.metadata.a

        if particle_type in ["stars", "dark_matter"]:
            particle_data.smoothing_lengths = generate_smoothing_lengths(
                coordinates=particle_data.coordinates,
                boxsize=data.metadata.boxsize,
                kernel_gamma=kernel_gamma,
                neighbours=57,
                speedup_fac=1,
                dimension=3,
            )

        pixel_grid = project_pixel_grid(
            particle_data,
            boxsize=data.metadata.boxsize,
            resolution=1024,
            region=[x - r_size, x + r_size, y - r_size, y + r_size],
        )

        if particle_type == "stars":
            # Need to clip.
            nonzero = pixel_grid >= 1e-2
            min_nonzero = np.min(pixel_grid[nonzero])
            pixel_grid[~nonzero] = min_nonzero

        fig, ax = plt.subplots(figsize=(8, 8), dpi=1024 // 8)
        fig.subplots_adjust(0, 0, 1, 1)
        ax.axis("off")

        ax.imshow(pixel_grid, norm=LogNorm(), cmap=cmap, origin="lower")
        ax.text(
            0.975,
            0.975,
            f"$z={data.metadata.z:3.3f}$",
            color="white",
            ha="right",
            va="top",
            transform=ax.transAxes,
        )
        ax.text(
            0.975,
            0.025,
            (
                f"$M_H={latex_float(halo_mass.value)}$ ${halo_mass.units.latex_repr}$\n"
                f"$M_*={latex_float(stellar_mass.value)}$ ${stellar_mass.units.latex_repr}$"
            ),
            color="white",
            ha="right",
            va="bottom",
            transform=ax.transAxes,
        )

        fig.savefig(f"{output_path}/{particle_type}_halo_image_{halo_id}.png")

        plt.close(fig)
