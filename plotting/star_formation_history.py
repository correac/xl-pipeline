"""
Plots the star formation history. Modified version of the script in the
github.com/swiftsim/swiftsimio-examples repository.
"""
import matplotlib

matplotlib.use("Agg")

import unyt

import matplotlib.pyplot as plt
import numpy as np
import sys

from swiftsimio import load

from load_sfh_data import read_obs_data

sfr_output_units = unyt.msun / (unyt.year * unyt.Mpc ** 3)

plt.style.use("mnras.mplstyle")

run_name = sys.argv[1]
run_directory = sys.argv[2]
snapshot_name = sys.argv[3]
output_path = sys.argv[4]

sfr_filename = f"{run_directory}/SFR.txt"
snapshot_filename = f"{run_directory}/{snapshot_name}"

data = np.genfromtxt(sfr_filename).T

snapshot = load(snapshot_filename)
units = snapshot.units
boxsize = snapshot.metadata.boxsize
box_volume = boxsize[0] * boxsize[1] * boxsize[2]

sfr_units = snapshot.gas.star_formation_rates.units

# a, Redshift, SFR
scale_factor = data[2]
redshift = data[3]
star_formation_rate = (data[7] * sfr_units / box_volume).to(sfr_output_units)

observational_data = read_obs_data("plotting/sfr_data")

fig, ax = plt.subplots()

ax.loglog()


# High z-order as we always want these to be on top of the observations
ax.plot(scale_factor, star_formation_rate.value, zorder=10000)[0]

# Observational data plotting

observation_lines = []
observation_labels = []

for index, observation in enumerate(observational_data):
    if observation.fitting_formula:
        if observation.description == "EAGLE NoAGN":
            observation_lines.append(
                ax.plot(
                    observation.scale_factor,
                    observation.sfr,
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
                    observation.sfr,
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
                observation.sfr,
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
ax.set_ylabel(r"SFR Density $\dot{\rho}_*$ [M$_\odot$ yr$^{-1}$ Mpc$^{-3}$]")


redshift_ticks = np.array([0.0, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0, 50.0, 100.0])
redshift_labels = [
    "$0$",
    "$0.2$",
    "$0.5$",
    "$1$",
    "$2$",
    "$3$",
    "$5$",
    "$10$",
    "$20$",
    "$50$",
    "$100$",
]
a_ticks = 1.0 / (redshift_ticks + 1.0)

ax.set_xticks(a_ticks)
ax.set_xticklabels(redshift_labels)
ax.tick_params(axis="x", which="minor", bottom=False)

ax.set_xlim(1.02, 0.07)
ax.set_ylim(1.8e-4, 1.7)

observation_legend = ax.legend(
    observation_lines, observation_labels, markerfirst=True, loc=3, fontsize=4, ncol=2
)

fig.tight_layout()

fig.savefig(f"{output_path}/star_formation_history.png")
