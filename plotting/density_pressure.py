"""
Makes a rho-P plot. Uses the swiftsimio library.
"""

import matplotlib.pyplot as plt
import numpy as np

from swiftsimio import load

from unyt import mh, cm, kb, K
from matplotlib.colors import LogNorm
from matplotlib.animation import FuncAnimation

# Constants; these could be put in the parameter file but are rarely changed.
density_bounds = [10 ** (-9.5), 1e6]  # in nh/cm^3
pressure_bounds = [10 ** (-4), 10 ** (10)]  # in K/cm^3
bins = 256

# Plotting controls
plt.style.use("mnras.mplstyle")


def get_data(filename):
    """
    Grabs the data (P in Kelvin / cm^3 and density in mh / cm^3).
    """

    data = load(filename)

    pressure_factor = float(data.gas.pressures.cosmo_factor.a_factor)

    number_density = (data.gas.densities.to_physical() / mh).to(cm ** -3)
    pressure = (data.gas.pressures * (pressure_factor / kb)).to(K * cm ** -3)

    return number_density.value, pressure.value


def make_hist(filename, density_bounds, pressure_bounds, bins):
    """
    Makes the histogram for filename with bounds as lower, higher
    for the bins and "bins" the number of bins along each dimension.

    Also returns the edges for pcolormesh to use.
    """

    density_bins = np.logspace(
        np.log10(density_bounds[0]), np.log10(density_bounds[1]), bins
    )
    pressure_bins = np.logspace(
        np.log10(pressure_bounds[0]), np.log10(pressure_bounds[1]), bins
    )

    H, density_edges, pressure_edges = np.histogram2d(
        *get_data(filename), bins=[density_bins, pressure_bins]
    )

    return H.T, density_edges, pressure_edges


def setup_axes():
    """
    Creates the figure and axis object.
    """
    fig, ax = plt.subplots(1)

    ax.set_xlabel("Density [$n_H$ cm$^{-3}$]")
    ax.set_ylabel("Pressure $P / k_B$ [K cm$^{-3}$]")

    ax.loglog()

    return fig, ax


def make_single_image(filename, density_bounds, pressure_bounds, bins, output_path):
    """
    Makes a single plot of rho-P
    """

    fig, ax = setup_axes()
    hist, d, P = make_hist(filename, density_bounds, pressure_bounds, bins)

    mappable = ax.pcolormesh(d, P, hist, norm=LogNorm(vmin=1))
    fig.colorbar(mappable, label="Number of particles", pad=0)

    fig.tight_layout()

    fig.savefig(f"{output_path}/density_pressure.png")

    return


if __name__ == "__main__":
    import sys

    run_name = sys.argv[1]
    run_directory = sys.argv[2]
    snapshot_name = sys.argv[3]
    output_path = sys.argv[4]

    snapshot_filename = f"{run_directory}/{snapshot_name}"

    make_single_image(
        snapshot_filename, density_bounds, pressure_bounds, bins, output_path
    )
