"""
Plots the metal mass fraction distribution for stars and gas.
"""

import matplotlib.pyplot as plt
import numpy as np
import unyt

from swiftsimio import load

from unyt import mh, cm, Gyr
from matplotlib.colors import LogNorm, Normalize
from matplotlib.animation import FuncAnimation

import sys

run_name = sys.argv[1]
run_directory = sys.argv[2]
snapshot_name = sys.argv[3]
output_path = sys.argv[4]
ptype = sys.argv[5]

snapshot_filename = f"{run_directory}/{snapshot_name}"

plt.style.use("mnras.mplstyle")

data = load(snapshot_filename)
number_of_bins = 256

metallicity_bins = np.logspace(-10, 0, number_of_bins)
metallicity_bin_centers = 0.5 * (metallicity_bins[1:] + metallicity_bins[:-1])
log_metallicity_bin_width = np.log10(metallicity_bins[1]) - np.log10(
    metallicity_bins[0]
)

try:
    metallicities = {
        "Gas": data.gas.smoothed_metal_mass_fractions.value,
        "Stars": data.stars.smoothed_metal_mass_fractions.value,
    }
    smoothed = True
except AttributeError:
    metallicities = {
        "Gas": data.gas.metal_mass_fractions.value,
        "Stars": data.stars.metal_mass_fractions.value,
    }
    smoothed = False

# Begin plotting

fig, ax = plt.subplots()

ax.loglog()

for label, data in metallicities.items():
    H, _ = np.histogram(data, bins=metallicity_bins)
    ax.plot(metallicity_bin_centers, H / log_metallicity_bin_width, label=label)


ax.legend(loc="upper right")
ax.set_xlabel(f"{'Smoothed ' if smoothed else ''}Metal Mass Fractions $Z$ []"))
ax.set_ylabel("Number of Particles / d$\\log Z$")

fig.savefig(f"{output_path}/metallicity_distribution.png")
