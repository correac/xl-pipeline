"""
Creates a plot of birth density (horizontal) against f_E. The
scatter in f_E comes from the dependence on metallicity.
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

snapshot_filename = f"{run_directory}/{snapshot_name}"

plt.style.use("mnras.mplstyle")

data = load(snapshot_filename)

number_of_bins = 128

birth_density_bins = unyt.unyt_array(
    np.logspace(-3, 5, number_of_bins), units=1 / cm ** 3
)
feedback_energy_fraction_bins = unyt.unyt_array(
    np.logspace(-1, 1, number_of_bins), units="dimensionless"
)

H, density_edges, f_E_edges  = np.histogram2d(
    (data.stars.birth_densities / mh).to(1 / cm**3).value,
    data.stars.feedback_energy_fractions.value,
    bins=[birth_density_bins, feedback_energy_fraction_bins],
)

# Begin plotting

fig, ax = plt.subplots()

ax.loglog()

mappable = ax.pcolormesh(
    density_edges,
    f_E_edges,
    H.T,
    norm=LogNorm()
)
fig.colorbar(mappable, label="Number of particles", pad=0)

ax.set_xlabel("Stellar Birth Density [$n_H$ cm$^{-3}$]")
ax.set_ylabel("Feedback energy fraction $f_E$ []")

ax.text(
    0.025,
    0.025,
    "\n".join([
        "$f_E values:",
        f"Min: {np.min(data.stars.feedback_energy_fractions.value):3.3f}",
        f"Max: {np.max(data.stars.feedback_energy_fractions.value):3.3f}",
        f"Mean: {np.mean(data.stars.feedback_energy_fractions.value):3.3f}",
        f"Median: {np.median(data.stars.feedback_energy_fractions.value):3.3f}",
    ])
    transform=ax.transAxes,
    ha="left",
    va="bottom",
    fontsize=6,
)

fig.savefig(f"{output_path}/birth_density_f_E.png")
