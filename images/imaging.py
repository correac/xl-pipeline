"""
Contains objects and functions to help with projected rendering.
"""

import attr
import cachetools
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.colors import LogNorm
from matplotlib.patches import Circle
from unyt import unyt_quantity, unyt_array

from swiftsimio.visualisation.projection import project_pixel_grid
from swiftsimio.visualisation.slice import kernel_gamma
from swiftsimio.visualisation.smoothing_length_generation import (
    generate_smoothing_lengths,
)
from swiftsimio.visualisation.rotation import rotation_matrix_from_vector

from typing import Optional


# Not threadsafe, but we're ok because this is python. We use this
# to cache the output 'mass image' from each image.
image_cache = cachetools.LRUCache(maxsize=32)


def latex_float(f):
    units = f.units

    if f < 1e3 and f > 1e-1:
        return f"${f.value:.3g}$ {units}"

    float_str = "${0:.2g}".format(f.value)
    if "e" in float_str:
        base, exponent = float_str.split("e")
        return r"{0} \times 10^{{{1}}}$ {2}".format(base, int(exponent), units)
    else:
        return float_str + f"$ {units}"


@attr.s
class ImageAttributes(object):
    """
    Image attributes - this has nothing to do with
    the actual galaxy that is being visualised.
    """

    output_filename = attr.ib()

    particle_type: str = attr.ib(default="gas")
    visualise: str = attr.ib(default="projected_density")
    decorate_scalebar: bool = attr.ib(default=True)
    decorate_position: bool = attr.ib(default=True)
    decorate_radius: bool = attr.ib(default=True)
    decorate_masses: bool = attr.ib(default=True)
    decorate_image_type: bool = attr.ib(default=True)
    projection: str = attr.ib(default="default")
    resolution: int = attr.ib(default=1024)
    cmap: str = attr.ib(default="viridis")
    norm: object = attr.ib(default=LogNorm)
    vmin: Optional[unyt_quantity] = attr.ib(default=None)
    vmax: Optional[unyt_quantity] = attr.ib(default=None)
    number_of_radii: float = attr.ib(default=1.5)
    text_color: str = attr.ib(default="white")
    fill_below: Optional[unyt_quantity] = attr.ib(default=None)
    scalebar_size: unyt_quantity = attr.ib(default=unyt_quantity(100, units="kpc"))
    plot_background_color: str = attr.ib("black")


@attr.s
class GalaxyAttributes(object):
    """
    Properties that only have things to do with the galaxy
    being visualised.
    """

    center: unyt_array = attr.ib()
    radius: unyt_array = attr.ib()
    normal_vector: unyt_array = attr.ib()
    redshift: unyt_quantity = attr.ib()
    unique_id: int = attr.ib()
    halo_mass: unyt_quantity = attr.ib(default=None)
    stellar_mass: unyt_quantity = attr.ib(default=None)


def get_rotation(
    image_attributes: ImageAttributes, galaxy_attributes: GalaxyAttributes
):
    """
    Gets the rotation matrix and center if required.
    """

    if image_attributes.projection == "faceon":
        return (
            rotation_matrix_from_vector(galaxy_attributes.normal_vector),
            galaxy_attributes.center,
        )
    elif image_attributes.projection == "edgeon":
        return (
            rotation_matrix_from_vector(galaxy_attributes.normal_vector, "y"),
            galaxy_attributes.center,
        )
    else:
        return None, None


def project(
    data, image_attributes: ImageAttributes, galaxy_attributes: GalaxyAttributes
):
    """
    Creates a projection image of `data` given attributes.
    """

    particle_data = getattr(data, image_attributes.particle_type)

    try:
        particle_data.smoothing_lengths
    except AttributeError:
        # Need to genereate smoothing lengths
        particle_data.smoothing_lengths = generate_smoothing_lengths(
            coordinates=particle_data.coordinates,
            boxsize=data.metadata.boxsize,
            kernel_gamma=kernel_gamma,
            neighbours=57,
            speedup_fac=1,
            dimension=3,
        )

    # Set up extra plot parameters
    radius_distance = galaxy_attributes.radius * image_attributes.number_of_radii
    region = [
        galaxy_attributes.center[0] - radius_distance,
        galaxy_attributes.center[0] + radius_distance,
        galaxy_attributes.center[1] - radius_distance,
        galaxy_attributes.center[1] + radius_distance,
    ]
    rotation_matrix, rotation_center = get_rotation(image_attributes, galaxy_attributes)

    common_attributes = dict(
        data=particle_data,
        boxsize=data.metadata.boxsize,
        resolution=image_attributes.resolution,
        region=region,
        mask=None,
        rotation_matrix=rotation_matrix,
        rotation_center=rotation_center,
        parallel=False,
    )

    # Swiftsimio has a nasty habit of reading these in as grams.
    particle_data.masses.convert_to_units("1e10 * Solar_Mass")
    # Have we already made the mass image?
    image_mass_hash = hash(
        f"{image_attributes.resolution}"
        f"{image_attributes.particle_type}"
        f"{image_attributes.projection}"
        f"{galaxy_attributes.unique_id}"
    )

    try:
        mass_image = image_cache[image_mass_hash]
    except KeyError:
        mass_image = project_pixel_grid(project="masses", **common_attributes)
        image_cache[image_mass_hash] = mass_image

    # Special case for mass density projection
    if image_attributes.visualise == "projected_density":
        # Units are more complex here as this is a smoothed density.
        x_range = region[1] - region[0]
        y_range = region[3] - region[2]
        units = 1.0 / (x_range * y_range)
        # Unfortunately this is required to prevent us from {over,under}flowing
        # the units...
        units.convert_to_units(1.0 / (x_range.units * y_range.units))
        units *= particle_data.masses.units

        image = unyt_array(mass_image, units=units)
    else:
        # Set mass-weighted attribute

        setattr(
            particle_data,
            f"_CACHE_MASSWEIGHTED",
            getattr(particle_data, image_attributes.visualise)
            * particle_data.masses.value,
        )

        with np.testing.suppress_warnings() as sup:
            sup.filter(RuntimeWarning)
            image = unyt_array(
                project_pixel_grid(project="_CACHE_MASSWEIGHTED", **common_attributes)
                / mass_image,
                units=getattr(particle_data, image_attributes.visualise).units,
            )

    return image


def fill_image(image: unyt_array, image_attributes=ImageAttributes):
    """
    Fills the image with fill values if required.
    """

    if image_attributes.fill_below is not None:
        same_units_fill = image_attributes.fill_below.to(image.units)
        image[np.isnan(image)] = same_units_fill
        image[image < same_units_fill] = same_units_fill

    return


def create_plot(
    image: unyt_array,
    image_attributes: ImageAttributes,
    galaxy_attributes: GalaxyAttributes,
):
    """
    Creates the figure and axes objects.
    """

    fig, ax = plt.subplots(figsize=(8, 8), dpi=image_attributes.resolution // 8)
    fig.subplots_adjust(0, 0, 1, 1)
    ax.axis("off")

    if image_attributes.vmin is not None:
        vmin = image_attributes.vmin.to(image.units).value
    else:
        vmin = None

    if image_attributes.vmax is not None:
        vmax = image_attributes.vmax.to(image.units).value
    else:
        vmax = None

    norm = image_attributes.norm(vmin=vmin, vmax=vmax)

    radius_distance = galaxy_attributes.radius * image_attributes.number_of_radii
    extent = [
        galaxy_attributes.center[0] - radius_distance,
        galaxy_attributes.center[0] + radius_distance,
        galaxy_attributes.center[1] - radius_distance,
        galaxy_attributes.center[1] + radius_distance,
    ]

    ax.set_facecolor(image_attributes.plot_background_color)

    ax.imshow(
        image.value.T,
        origin="lower",
        norm=norm,
        cmap=image_attributes.cmap,
        extent=extent,
    )

    return fig, ax


def decorate_axes(
    ax: plt.Axes, image_attributes: ImageAttributes, galaxy_attributes: GalaxyAttributes
):
    """
    Decorates the axes with the requested extra information.
    """

    if image_attributes.decorate_radius:
        # Show the radius as a dashed circle
        radius = Circle(
            galaxy_attributes.center[:2],
            radius=galaxy_attributes.radius,
            color=image_attributes.text_color,
            linestyle="dashed",
            fill=False,
        )

        x = galaxy_attributes.center[0]
        y = galaxy_attributes.center[1] + 1.025 * galaxy_attributes.radius

        ax.text(
            x,
            y,
            r"$R_{200, \rm{crit}}$",
            ha="center",
            va="bottom",
            color=image_attributes.text_color,
        )

        ax.add_artist(radius)

    if image_attributes.decorate_position:
        # Show the position (in mpc)
        x, y, z = galaxy_attributes.center.to("Mpc").value
        position = f"[{x:.3g}, {y:.3g}, {z:.3g}] Mpc"
        redshift = f"$z={galaxy_attributes.redshift:3.3f}$"

        ax.text(
            0.975,
            0.025,
            f"{redshift}\n{position}",
            ha="right",
            va="bottom",
            multialignment="right",
            transform=ax.transAxes,
            color=image_attributes.text_color,
        )

    if image_attributes.decorate_scalebar:
        x = galaxy_attributes.center[0]
        y = galaxy_attributes.center[1] - 1.025 * galaxy_attributes.radius

        ax.text(
            x,
            y,
            f"{latex_float(galaxy_attributes.radius)}",
            ha="center",
            va="top",
            color=image_attributes.text_color,
        )

        pass

    ptype_title = image_attributes.particle_type.replace("_", " ").title()
    visualise_title = image_attributes.visualise.replace("_", " ").title()

    if image_attributes.decorate_image_type:
        ax.text(
            0.025,
            0.975,
            f"{ptype_title} {visualise_title}",
            ha="left",
            va="top",
            transform=ax.transAxes,
            color=image_attributes.text_color,
        )

        ax.text(
            0.025,
            0.025,
            (
                f"Halo {galaxy_attributes.unique_id}\n"
                f"{image_attributes.projection.replace('on', ' on').title()}"
            ),
            ha="left",
            va="bottom",
            transform=ax.transAxes,
            color=image_attributes.text_color,
        )

    if image_attributes.decorate_masses:
        ax.text(
            0.975,
            0.975,
            (
                f"$M_H$={latex_float(galaxy_attributes.halo_mass.to('Solar_Mass'))}\n"
                f"$M_*$={latex_float(galaxy_attributes.stellar_mass.to('Solar_Mass'))}"
            ),
            color=image_attributes.text_color,
            ha="right",
            va="top",
            transform=ax.transAxes,
        )

    return


def render_galaxy_image(
    data, image_attributes: ImageAttributes, galaxy_attributes: GalaxyAttributes
):
    image = project(data, image_attributes, galaxy_attributes)

    fill_image(image, image_attributes)

    fig, ax = create_plot(image, image_attributes, galaxy_attributes)

    decorate_axes(ax, image_attributes, galaxy_attributes)

    fig.savefig(f"{galaxy_attributes.unique_id}_{image_attributes.output_filename}")

    plt.close(fig)

    return


if __name__ == "__main__":
    from velociraptor.swift.swift import to_swiftsimio_dataset
    from velociraptor.particles import load_groups
    from velociraptor import load
    import numpy as np
    import sys

    image_styles = [
        ImageAttributes(
            output_filename="dens.png",
            fill_below=unyt_quantity(1000, units="Solar_Mass / (kpc * kpc)"),
        ),
        ImageAttributes(
            output_filename="dens_faceon.png",
            projection="faceon",
            fill_below=unyt_quantity(1000, units="Solar_Mass / (kpc * kpc)"),
        ),
        ImageAttributes(
            output_filename="temp_faceon.png",
            visualise="temperatures",
            projection="faceon",
            fill_below=unyt_quantity(1e4, units="K"),
            cmap="twilight",
            vmin=unyt_quantity(1e3, units="K"),
            vmax=unyt_quantity(1e7, units="K"),
        ),
        ImageAttributes(
            output_filename="star_faceon.png",
            particle_type="stars",
            projection="faceon",
            fill_below=unyt_quantity(0.1, units="Solar_Mass / (pc * pc)"),
            cmap="bone",
        ),
        ImageAttributes(
            output_filename="star_edgeon.png",
            particle_type="stars",
            projection="edgeon",
            fill_below=unyt_quantity(0.1, units="Solar_Mass / (pc * pc)"),
            cmap="bone",
        ),
        ImageAttributes(
            output_filename="sfr_faceon.png",
            visualise="star_formation_rates",
            projection="faceon",
            text_color="black",
            cmap="magma",
        ),
        ImageAttributes(
            output_filename="dens_edgeon.png",
            projection="edgeon",
            fill_below=unyt_quantity(1000, units="Solar_Mass / (kpc * kpc)"),
        ),
    ]

    snapshot_path = sys.argv[1]
    velociraptor_base_name = sys.argv[2]
    output_path = sys.argv[3]

    halo_ids = range(25, 30)

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

    for halo_id in halo_ids:
        particles, unbound_particles = groups.extract_halo(halo_id, filenames=filenames)

        halo_mass = catalogue.masses.mass_200mean[halo_id].to("Solar_Mass")
        stellar_mass = catalogue.apertures.mass_star_30_kpc[halo_id].to("Solar_Mass")

        lx = catalogue.angular_momentum.lx_star[halo_id].value
        ly = catalogue.angular_momentum.ly_star[halo_id].value
        lz = catalogue.angular_momentum.lz_star[halo_id].value

        norm_vector = np.array([lx, ly, lz])

        # This reads particles using the cell metadata that are around our halo
        data = to_swiftsimio_dataset(
            particles, snapshot_path, generate_extra_mask=False
        )

        x = particles.x / data.metadata.a
        y = particles.y / data.metadata.a
        z = particles.z / data.metadata.a
        r = particles.r_200crit / data.metadata.a

        halo_center = unyt_array([x, y, z])

        galaxy_attributes = GalaxyAttributes(
            center=halo_center,
            radius=r,
            normal_vector=norm_vector,
            redshift=data.metadata.z,
            unique_id=halo_id,
            halo_mass=halo_mass,
            stellar_mass=stellar_mass,
        )

        for image_style in image_styles:
            render_galaxy_image(data, image_style, galaxy_attributes)

