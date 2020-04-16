"""
Pretty-prints the emulate-able parameters to a file.
"""

import yaml
import numpy as np
import sys

with open(sys.argv[1], "r") as handle:
    input_data = yaml.load(handle, Loader=yaml.Loader)

parameter_output_filename = "parameters.txt"

try:
    agn_parameters = {
        "dT": f"{float(input_data['EAGLEAGN']['AGN_delta_T_K']):10.3e}",
        "Ceff": f"{input_data['EAGLEAGN']['coupling_efficiency']:3.3f}",
        "Va": f"{float(input_data['EAGLEAGN']['viscous_alpha']):10.3e}",
    }
except KeyError:
    agn_parameters = {}

try:
    SNII_parameters = {
        "min": f"{input_data['COLIBREFeedback']['SNII_energy_fraction_min']:3.3f}",
        "max": f"{input_data['COLIBREFeedback']['SNII_energy_fraction_max']:3.3f}",
        "n_0": f"{input_data['COLIBREFeedback']['SNII_energy_fraction_n_0_H_p_cm3']:3.3f}",
        "n_Z": f"{input_data['COLIBREFeedback']['SNII_energy_fraction_n_Z']:3.3f}",
        "n_n": f"{input_data['COLIBREFeedback']['SNII_energy_fraction_n_n']:3.3f}",
        "ene": f"{float(input_data['COLIBREFeedback']['SNII_energy_erg']):10.3e}",
    }
except KeyError:
    SNII_parameters = {
        "min": f"{input_data['EAGLEFeedback']['SNII_energy_fraction_min']:3.3f}",
        "max": f"{input_data['EAGLEFeedback']['SNII_energy_fraction_max']:3.3f}",
        "n_0": f"{input_data['EAGLEFeedback']['SNII_energy_fraction_n_0_H_p_cm3']:3.3f}",
        "n_Z": f"{input_data['EAGLEFeedback']['SNII_energy_fraction_n_Z']:3.3f}",
        "n_n": f"{input_data['EAGLEFeedback']['SNII_energy_fraction_n_n']:3.3f}",
    }


output = ""

output += "AGN: "

for name, value in agn_parameters.items():
    output += f"{name}: {value}   "

output += "|   SNII: "

for name, value in SNII_parameters.items():
    output += f"{name}: {value}   "

with open(parameter_output_filename, "w") as handle:
    handle.write(output)
