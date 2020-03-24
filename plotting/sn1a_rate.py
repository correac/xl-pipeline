"""
Plots the star formation history.
"""
import matplotlib

matplotlib.use("Agg")

import unyt

import matplotlib.pyplot as plt
import numpy as np

from swiftsimio import load

from load_sn1a_data import read_obs_data

sfr_output_units = unyt.msun / (unyt.year * unyt.Mpc ** 3)

plt.style.use("mnras.mplstyle")

import sys

run_name = sys.argv[1]
run_directory = sys.argv[2]
snapshot_name = sys.argv[3]
output_path = sys.argv[4]

sn1a_filename = f"{run_directory}/SNIa.txt"
snapshot_filename = f"{run_directory}/{snapshot_name}"

data = np.genfromtxt(sn1a_filename).T

default_SNIa_rate_conversion = 1.022_690e-12

scale_factor = (data[4] + data[5]) / 2.0
redshift = (data[6] + data[7]) / 2.0
SNIa_rate = data[11] * default_SNIa_rate_conversion

observational_data = read_obs_data()

fig, ax = plt.subplots()

ax.loglog()

# Simulation data plotting

# High z-order as we always want these to be on top of the observations
ax.plot(scale_factor, SNIa_rate, label=name, zorder=10000)

# Observational data plotting

observation_lines = []
observation_labels = []

for index, observation in enumerate(observational_data):
    if observation.fitting_formula:
        if observation.description == "EAGLE NoAGN":
            observation_lines.append(
                ax.plot(
                    observation.scale_factor,
                    observation.SNIa_rate,
                    label=observation.description,
                    color="aquamarine",
                    zorder=-10000,
                    linewidth=1,
                    alpha=0.5,
                )[0]
            )
        else:
            observation_lines.append(
                ax.plot(
                    observation.scale_factor,
                    observation.SNIa_rate,
                    label=observation.description,
                    color="grey",
                    linewidth=1,
                    zorder=-1000,
                )[0]
            )
    else:
        observation_lines.append(
            ax.errorbar(
                observation.scale_factor,
                observation.SNIa_rate,
                observation.error,
                label=observation.description,
                linestyle="none",
                marker="o",
                elinewidth=0.5,
                markeredgecolor="none",
                markersize=2,
                zorder=index,  # Required to have line and blob at same zodrer
            )
        )
    observation_labels.append(observation.description)


ax.set_xlabel("Redshift $z$")
ax.set_ylabel(r"SNIa rate $[\rm yr^{-1} \cdot Mpc^{-3}]$")


redshift_ticks = np.array(
    [0.0, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 50.0, 100.0]
)
redshift_labels = [
    "$0$",
    "$0.2$",
    "$0.5$",
    "$1$",
    "$2$",
    "$3$",
    "$5$",
    "$7$",
    "$10$",
    "$20$",
    "$50$",
    "$100$",
]
a_ticks = 1.0 / (redshift_ticks + 1.0)

ax.set_xticks(a_ticks)
ax.set_xticklabels(redshift_labels)
ax.tick_params(axis="x", which="minor", bottom=False)

ax.set_xlim(1.02, 0.10)
ax.set_ylim(1e-5, 2e-4)

observation_legend = ax.legend(
    observation_lines, observation_labels, markerfirst=True, loc=3, fontsize=6, ncol=2
)

fig.tight_layout()

fig.savefig(f"{output_path}/sn1a_rate.png")
