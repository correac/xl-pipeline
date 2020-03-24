"""
Makes a rho-T plot. Uses the swiftsimio library.
"""

import matplotlib.pyplot as plt
import numpy as np

from swiftsimio import load

from unyt import mh, cm, Gyr
from matplotlib.colors import Normalize
from matplotlib.animation import FuncAnimation

# Constants; these could be put in the parameter file but are rarely changed.
density_bounds = [10 ** (-9.5), 1e6]  # in nh/cm^3
temperature_bounds = [10 ** (0), 10 ** (9.5)]  # in K
metallicity_bounds = [-6, -1]  # In metal mass fraction
min_metallicity = 1e-8
bins = 256

# Plotting controls
plt.style.use("mnras.mplstyle")


def get_data(filename):
    """
    Grabs the data (T in Kelvin and density in mh / cm^3, and log10 metallicity).
    """

    data = load(filename)

    density_factor = float(data.gas.densities.cosmo_factor.a_factor)
    temperature_factor = float(data.gas.temperatures.cosmo_factor.a_factor)

    number_density = (data.gas.densities * (density_factor / mh)).to(cm ** -3)
    temperature = (data.gas.temperatures * temperature_factor).to("K")
    metallicity = data.gas.metal_mass_fractions
    metallicity[metallicity < min_metallicity] = min_metallicity

    return number_density.value, temperature.value, np.log10(metallicity.value)


def make_hist(filename, density_bounds, temperature_bounds, bins):
    """
    Makes the histogram for filename with bounds as lower, higher
    for the bins and "bins" the number of bins along each dimension.

    Also returns the edges for pcolormesh to use.
    """

    density_bins = np.logspace(
        np.log10(density_bounds[0]), np.log10(density_bounds[1]), bins
    )
    temperature_bins = np.logspace(
        np.log10(temperature_bounds[0]), np.log10(temperature_bounds[1]), bins
    )

    dens, temps, metals = get_data(filename)

    H, density_edges, temperature_edges = np.histogram2d(
        dens, temps, bins=[density_bins, temperature_bins], weights=metals
    )

    H_norm, _, _ = np.histogram2d(dens, temps, bins=[density_bins, temperature_bins])

    # Avoid div/0
    mask = H_norm == 0.0
    H[mask] = -25
    H_norm[mask] = 1.0

    return np.ma.array((H / H_norm).T, mask=mask.T), density_edges, temperature_edges


def setup_axes():
    """
    Creates the figure and axis object.
    """
    fig, ax = plt.subplots(1)

    ax.set_xlabel("Density [$n_H$ cm$^{-3}$]")
    ax.set_ylabel("Temperature [K]")

    ax.loglog()

    return fig, ax


def make_single_image(
    filename, density_bounds, temperature_bounds, metallicity_bounds, bins, output_path
):
    """
    Makes a single plot of rho-T
    """

    fig, ax = setup_axes()
    hist, d, T = make_hist(filename, density_bounds, temperature_bounds, bins)

    mappable = ax.pcolormesh(
        d, T, hist, norm=Normalize(vmin=metallicity_bounds[0], vmax=metallicity_bounds[1])
    )
    fig.colorbar(mappable, label="Mean (Logarithmic) Metallicity $\log_{10} Z$ (min. $Z=10^{-8}$)", pad=0)

    fig.tight_layout()

    fig.savefig(f"{output_path}/density_temperature_metals.png")

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
        temperature_bounds,
        metallicity_bounds,
        bins,
        output_path,
    )

