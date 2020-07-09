"""
Makes a rho-U plot. Uses the swiftsimio library.
"""

import matplotlib.pyplot as plt
import numpy as np

from swiftsimio import load

from unyt import mh, cm, Gyr, s, km
from matplotlib.colors import LogNorm
from matplotlib.animation import FuncAnimation

# Constants; these could be put in the parameter file but are rarely changed.
density_bounds = [10**(-9.5), 1e6]  # in nh/cm^3
internal_energy_bounds = [10 ** (-2), 10 ** (8)]  # in 
bins = 256

# Plotting controls
plt.style.use("mnras.mplstyle")

def get_data(filename):
    """
    Grabs the data (u in (cm / s)^2 and density in mh / cm^3).
    """

    data = load(filename)
    
    number_density = (data.gas.densities.to_physical() / mh).to(cm**-3)
    internal_energy = (data.gas.internal_energies.to_physical()).to(km**2 / s**2)

    return number_density.value, internal_energy.value


def make_hist(filename, density_bounds, internal_energy_bounds, bins):
    """
    Makes the histogram for filename with bounds as lower, higher
    for the bins and "bins" the number of bins along each dimension.

    Also returns the edges for pcolormesh to use.
    """

    density_bins = np.logspace(
        np.log10(density_bounds[0]), np.log10(density_bounds[1]), bins
    )
    temperature_bins = np.logspace(
        np.log10(internal_energy_bounds[0]), np.log10(internal_energy_bounds[1]), bins
    )

    H, density_edges, temperature_edges = np.histogram2d(
        *get_data(filename), bins=[density_bins, temperature_bins]
    )

    return H.T, density_edges, temperature_edges


def setup_axes():
    """
    Creates the figure and axis object.
    """
    fig, ax = plt.subplots(1)

    ax.set_xlabel("Density [$n_H$ cm$^{-3}$]")
    ax.set_ylabel("Internal Energy [km$^2$ / s$^2$]")

    ax.loglog()

    return fig, ax


def make_single_image(filename, density_bounds, internal_energy_bounds, bins, output_path):
    """
    Makes a single plot of rho-T
    """

    fig, ax = setup_axes()
    hist, d, T = make_hist(
        filename, density_bounds, internal_energy_bounds, bins
    )

    mappable = ax.pcolormesh(d, T, hist, norm=LogNorm(vmin=1))
    fig.colorbar(mappable, label="Number of particles", pad=0)

    fig.tight_layout()

    fig.savefig(f"{output_path}/density_internal_energy.png")

    return

if __name__ == "__main__":
    import sys

    run_name = sys.argv[1]
    run_directory = sys.argv[2]
    snapshot_name = sys.argv[3]
    output_path = sys.argv[4]

    snapshot_filename = f"{run_directory}/{snapshot_name}"

    make_single_image(
        snapshot_filename,
        density_bounds,
        internal_energy_bounds,
        bins,
        output_path
    )

