"""
Creates the plot of metallicity against birth density, with
the background coloured by f_E.
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
used_parameters = data.metadata.parameters

try:  # COLIBRE Parameters
    parameters = {
        k: float(used_parameters[v])
        for k, v in {
            "f_E,min": "COLIBREFeedback:SNII_energy_fraction_min",
            "f_E,max": "COLIBREFeedback:SNII_energy_fraction_max",
            "n_Z": "COLIBREFeedback:SNII_energy_fraction_n_Z",
            "n_n": "COLIBREFeedback:SNII_energy_fraction_n_n",
            "Z_pivot": "COLIBREFeedback:SNII_energy_fraction_Z_0",
            "n_pivot": "COLIBREFeedback:SNII_energy_fraction_n_0_H_p_cm3",
            "ener": "COLIBREFeedback:SNII_energy_erg",
        }.items()
    }
except:  # EAGLE
    parameters = {
        k: float(used_parameters[v])
        for k, v in {
            "f_E,min": "EAGLEFeedback:SNII_energy_fraction_min",
            "f_E,max": "EAGLEFeedback:SNII_energy_fraction_max",
            "n_Z": "EAGLEFeedback:SNII_energy_fraction_n_Z",
            "n_n": "EAGLEFeedback:SNII_energy_fraction_n_n",
            "Z_pivot": "EAGLEFeedback:SNII_energy_fraction_Z_0",
            "n_pivot": "EAGLEFeedback:SNII_energy_fraction_n_0_H_p_cm3",
        }.items()
    }
    star_formation_parameters = {
        k: float(used_parameters[v])
        for k, v in {
            "threshold_Z0": "EAGLEStarFormation:threshold_Z0",
            "threshold_n0": "EAGLEStarFormation:threshold_norm_H_p_cm3",
            "slope": "EAGLEStarFormation:threshold_slope",
        }.items()
    }


number_of_bins = 128

# Constants; these could be put in the parameter file but are rarely changed.
birth_density_bins = unyt.unyt_array(
    np.logspace(-3, 5, number_of_bins), units=1 / cm ** 3
)
metal_mass_fraction_bins = unyt.unyt_array(
    np.logspace(-6, 0, number_of_bins), units="dimensionless"
)

# Now need to make background grid of f_E.
birth_density_grid, metal_mass_fraction_grid = np.meshgrid(
    0.5 * (birth_density_bins.value[1:] + birth_density_bins.value[:-1]),
    0.5 * (metal_mass_fraction_bins.value[1:] + metal_mass_fraction_bins.value[:-1]),
)

f_E_grid = parameters["f_E,min"] + (parameters["f_E,max"] - parameters["f_E,min"]) / (
    1.0
    + (metal_mass_fraction_grid / parameters["Z_pivot"]) ** parameters["n_Z"]
    * (birth_density_grid / parameters["n_pivot"]) ** (-parameters["n_n"])
)

# Begin plotting

fig, ax = plt.subplots()

ax.loglog()

mappable = ax.pcolormesh(
    birth_density_bins.value,
    metal_mass_fraction_bins.value,
    f_E_grid,
    norm=LogNorm(1e-2, 1e1),
)
fig.colorbar(mappable, label="Feedback energy fraction $f_E$", pad=0)

try:
    metal_mass_fractions = data.stars.smoothed_metal_mass_fractions.value
except AttributeError:
    metal_mass_fractions = data.stars.metal_mass_fractions.value

H, _, _ = np.histogram2d(
    (data.stars.birth_densities / mh).to(1 / cm ** 3).value,
    metal_mass_fractions,
    bins=[birth_density_bins.value, metal_mass_fraction_bins.value],
)

ax.contour(birth_density_grid, metal_mass_fraction_grid, H.T, levels=6, cmap="Pastel1")

# Add line showing SF law
try:
    sf_threshold_density = star_formation_parameters["threshold_n0"] * (
        metal_mass_fraction_bins.value / star_formation_parameters["threshold_Z0"]
    ) ** (star_formation_parameters["slope"])
    ax.plot(
        sf_threshold_density,
        metal_mass_fraction_bins,
        linestyle="dashed",
        label="SF threshold",
    )
except:
    pass

legend = ax.legend(markerfirst=True, loc="lower left")
plt.setp(legend.get_texts(), color="white")

ax.set_xlabel("Stellar Birth Density [$n_H$ cm$^{-3}$]")
ax.set_ylabel("Smoothed Metal Mass Fraction $Z$ []")

ax.text(
    0.975,
    0.025,
    "\n".join(
        [f"${k.replace('_', '_{') + '}'}$: ${v:.4g}$" for k, v in parameters.items()]
    ),
    color="white",
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    fontsize=legend.get_texts()[0].get_fontsize(),
)

ax.text(
    0.975,
    0.975,
    "Contour lines linearly spaced",
    color="white",
    transform=ax.transAxes,
    ha="right",
    va="top",
    fontsize=legend.get_texts()[0].get_fontsize(),
)

fig.savefig(f"{output_path}/birth_density_metallicity.png")
