"""
Converts a run to Ian's preferred output style.
"""

import yaml
import numpy as np

with open("data.yml", "r") as handle:
    input_data = yaml.load(handle)

smf_output_name = "GSMF.txt"
sizes_output_name = "GalaxySizes.txt"

smf = input_data["stellar_mass_function_100"]["lines"]["mass_function"]
galaxy_size = input_data["stellar_mass_galaxy_size_100"]["lines"]["median"]

n_bins = 25
mass = np.linspace(7.1, 11.9, n_bins)

smf_out = np.zeros((n_bins, 7))
galaxy_size_out = np.zeros((n_bins, 14))

smf_out[:, 0] = mass[:]
smf_out[0 : len(smf["values"])][:, 3] = smf["values"][:]
galaxy_size_out[:, 0] = mass[:]
galaxy_size_out[0 : len(galaxy_size["values"])][:, 10] = galaxy_size["values"][:]

np.savetxt(smf_output_name, smf_out, delimiter=",")
np.savetxt(sizes_output_name, galaxy_size_out, delimiter=",")
