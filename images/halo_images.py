"""
Creates images of the background of a given run in several views,

+ Mass density
+ Diffusion parameters
+ Viscosity parameters
+ Temperature map
+ Metal mass fractions

Takes as the first argument the snapshot filename, and as the second
the resoltion. As the final argument it takes the output path.
"""

from swiftsimio import load
from swiftsimio.visualisation import project_gas_pixel_grid
from matplotlib.colors import LogNorm
from cmocean import cm

import numpy as np
import matplotlib.pyplot as plt
import sys
import unyt

from unyt import Mpc

units = Mpc

data = load(sys.argv[1])
output_path = sys.argv[3]

res = 2048


def make_image(image, cmap, filename, vmin=None, vmax=None):
    fig, ax = plt.subplots(figsize=(4, 4), dpi=res // 4)
    fig.subplots_adjust(0, 0, 1, 1)
    ax.axis("off")

    ax.imshow(
        LogNorm(vmin=vmin, vmax=vmax)(image),
        cmap=cmap,
        extent=[
            0 * units,
            data.metadata.boxsize[0].to(units),
            0 * units,
            data.metadata.boxsize[0].to(units),
        ],
        origin="lower",
    )

    fig.savefig(f"{output_path}/{filename}.png")
    plt.close(fig)

    return


common_parameters = dict(data=data, resolution=res, parallel=True)
norm = project_gas_pixel_grid(**common_parameters, project=None).T
mass = project_gas_pixel_grid(**common_parameters).T

normed = (
    lambda project: project_gas_pixel_grid(**common_parameters, project=project).T
    / norm
)

diff = normed("diffusion_parameters")
visc = normed("viscosity_parameters")
temp = normed("temperatures")
mmf = normed("metal_mass_fractions")

make_image(mass, "inferno", "projected_gas_density")
make_image(diff, cm.ice, "diffusion_parameters", 0.01, 1.0)
make_image(visc, cm.curl, "viscosity_parameters", 0.2, 2.0)
make_image(temp, "twilight", "temperatures", 1e2, 1e8)
make_image(mmf, "cubehelix", "metal_mass_fractions", 0.0012, 1.2)
