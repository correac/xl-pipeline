"""
Code from Folkert Nobels to load observational SNIa rate data.
"""

from numpy import *

h = 0.68


class ObservationalData(object):
    """
    Holds observational data.
    """

    def __init__(self, scale_factor, SNIa_rate, error, description):
        """
        Store stuff in me!
        """
        self.scale_factor = scale_factor
        self.SNIa_rate = SNIa_rate
        self.error = error
        self.description = description

        if self.error is None:
            self.fitting_formula = True
        else:
            self.fitting_formula = False


def read_obs_data(path="observational_data"):
    """
    Reads the observational data
    """

    output = []

    hcorr = log10(h) - log10(0.7)  # h^-2 for SFR, h^-3 for volume

    z, ratenu, sys_err_p, sys_err_m, stat = loadtxt(
        f"{path}/SNIa_rate_frohmaier.dat", unpack=True
    )
    obs1_a = 1.0 / (1.0 + z)
    err_p = (sys_err_p ** 2 + stat ** 2) ** 0.5 * (h / 0.7) ** 3
    err_m = (sys_err_m ** 2 + stat ** 2) ** 0.5 * (h / 0.7) ** 3
    obs1_rnu = ratenu * 1e-5 * (h / 0.7) ** 3
    obs1_err = zeros((2, 1))
    obs1_err[0] = err_m * 1e-5
    obs1_err[1] = err_p * 1e-5

    output.append(
        ObservationalData(obs1_a, obs1_rnu, obs1_err, "Frohmaier et al. (2019) [PTF]")
    )

    z, ratenu, sys_err_p, sys_err_m, stat_p, stat_m = loadtxt(
        f"{path}/SNIa_rate_dilday.dat", unpack=True
    )
    obs2_a = 1.0 / (1.0 + z)
    err_p = (sys_err_p ** 2 + stat_p ** 2) ** 0.5 * (h / 0.7) ** 3
    err_m = (sys_err_m ** 2 + stat_m ** 2) ** 0.5 * (h / 0.7) ** 3
    obs2_rnu = ratenu * 1e-5 * (h / 0.7) ** 3
    obs2_err = zeros((2, len(obs2_rnu)))
    obs2_err[0] = err_m * 1e-5
    obs2_err[1] = err_p * 1e-5

    output.append(
        ObservationalData(obs2_a, obs2_rnu, obs2_err, "Dilday et al. (2010) [SDSS]")
    )

    z, ratenu, sys_err_p, sys_err_m, stat_p, stat_m = loadtxt(
        f"{path}/SNIa_rate_perrett.dat", unpack=True
    )
    obs3_a = 1.0 / (1.0 + z)
    err_p = (sys_err_p ** 2 + stat_p ** 2) ** 0.5 * (h / 0.7) ** 3
    err_m = (sys_err_m ** 2 + stat_m ** 2) ** 0.5 * (h / 0.7) ** 3
    obs3_rnu = ratenu * 1e-5 * (h / 0.7) ** 3
    obs3_err = zeros((2, len(obs3_rnu)))
    obs3_err[0] = err_m * 1e-5
    obs3_err[1] = err_p * 1e-5

    output.append(
        ObservationalData(obs3_a, obs3_rnu, obs3_err, "Perrett et al. (2013) [SNLS]")
    )

    z, ratenu, sys_err_p, sys_err_m = loadtxt(
        f"{path}/SNIa_rate_graur.dat", unpack=True
    )
    obs4_a = 1.0 / (1.0 + z)
    err_p = sys_err_p * (h / 0.7) ** 3
    err_m = -sys_err_m * (h / 0.7) ** 3
    obs4_rnu = ratenu * 1e-5 * (h / 0.7) ** 3
    obs4_err = zeros((2, len(obs4_rnu)))
    obs4_err[0] = err_m * 1e-5
    obs4_err[1] = err_p * 1e-5

    output.append(
        ObservationalData(obs4_a, obs4_rnu, obs4_err, "Graur et al. (2011) [SDF]")
    )

    z, ratenu, sys_err_p, sys_err_m, stat_p, stat_m = loadtxt(
        f"{path}/SNIa_rate_rodney.dat", unpack=True
    )
    obs5_a = 1.0 / (1.0 + z)
    err_p = (sys_err_p ** 2 + stat_p ** 2) ** 0.5 * (h / 0.7) ** 3
    err_m = (sys_err_m ** 2 + stat_m ** 2) ** 0.5 * (h / 0.7) ** 3
    obs5_rnu = ratenu * 1e-5 * (h / 0.7) ** 3
    obs5_err = zeros((2, len(obs5_rnu)))
    obs5_err[0] = err_m * 1e-5
    obs5_err[1] = err_p * 1e-5

    output.append(
        ObservationalData(obs5_a, obs5_rnu, obs5_err, "Rodney et al. (2014) [CANDELS]")
    )

    return output
