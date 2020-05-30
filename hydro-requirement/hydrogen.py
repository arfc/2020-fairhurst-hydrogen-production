import numpy as np


def lte_prod_rate(P, eta):
    """
    Low temperature electrolysis energy requirements and production rate.
    Parameters:
    -----------
    P: thermal power [MW]
    eta: themal-to-electric conversion efficiency
    Returns:
    --------
    see: sepecific energy [kWh(th)/kg-H2]
    pr: production rate [kg/h]
    """
    see = 60  # kWh(e)/kg-H2
    see /= eta
    pr = P/see*1e3
    return see, pr


def si_prod_rate(P, outT):
    """
    Sulfur-Iodine energy requirements and production rate.
    Values from 'Efficiency of hydrogen production systems using alternative
    nuclear energy technologies', Yildiz et al., May 2005.
    Parameters:
    -----------
    P: thermal power [MW]
    outT: reactor outlet temperature [C]
    Returns:
    --------
    pth: sepecific energy [kWh(th)/kg-H2]
    pr: production rate [kg/h]
    """
    temp = [750, 800, 850, 900, 950, 1000]
    sel = [600, 400, 300, 265, 245, 230]  # specfic energy [MJ/kg-H2]
    se = 1e3/3600 * np.array(sel)  # [kWh/kg-H2]
    pth = np.interp(0.97*outT, temp, se)
    pr = P/pth*1e3
    return pth, pr


def delta_H(Tout, Tin):
    """
    Calculates H(Tout)-H(Tin) of water at P=3.5 MPa
    Parameters:
    -----------
    Tout: outlet temperature [C]
    Tin: inlet temperature [C]
    """
    temp = [25, 50, 75, 100, 125, 150, 175, 200, 225, 242.56, 242.56, 250, 275,
            300, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575, 600,
            625, 650, 675, 700, 725, 750, 775, 800, 825, 850, 875, 900, 925,
            950, 975, 1000]
    ent = [1.9468, 3.8255, 5.7076, 7.5974, 9.5, 11.423, 13.374, 15.368, 17.421,
           18.912, 50.49, 50.977, 52.4, 53.657, 54.823, 55.935, 57.012, 58.066,
           59.106, 60.136, 61.16, 62.182, 63.203, 64.225, 65.249, 66.276,
           67.306, 68.341, 69.381, 70.426, 71.477, 72.534, 73.597, 74.666,
           75.742, 76.825, 77.914, 79.009, 80.112, 81.221, 82.337, 83.459]
    dH = np.interp(Tout, temp, ent) - np.interp(Tin, temp, ent)  # [kJ/mol]
    return dH


def SI2(eta, Tout, Ts):
    """"
    Calculates energy requirements for S-I 2 case.
    Values from 'Efficiency of hydrogen production systems using alternative
    nuclear energy technologies', Yildiz et al., May 2005.
    Parameters:
    -----------
    eta: thermal-to-electrical conversion efficiency
    Tout: reactor outlet temperature [C]
    Ts: SI process temperature [C]
    Returns:
    --------
    Pth: reactor thermal power requirement [kWh/kg-H2]
    gamma: Pe/Pth
    """
    ef = 0.97
    Tr = ef * Tout

    temp = [750, 800, 850, 900, 950, 1000]
    sel = [600, 400, 300, 265, 245, 230]  # specfic energy [MJ/kg-H2]
    se = 1e3/3600 * np.array(sel)  # [kWh/kg-H2]

    dHsi = np.interp(Ts, temp, se)
    mdot = np.interp(Tr, temp, se)/delta_H(Tr, 170)
    dHboost = mdot*delta_H(Ts, Tr)
    dHboost = dHboost/(2*1.008*3.6)  # [kWh/kg-H2]

    gammacPth = dHsi - dHboost
    etef = 0.95  # electrical-to-thermal conversion efficiency

    gammaPth = 1/eta*1/etef*dHboost
    Pth = gammaPth + gammacPth
    gamma = gammaPth/Pth
    return Pth, gamma


def efficiency(th):
    """
    Calculates thermal-to-electricity conversion efficiency.
    Parameters:
    -----------
    th: hot temperature [C]
    Returns:
    --------
    eta: Thermal-to-electricity conversion efficiency.
    """
    tc = 27  # C
    tc += 273  # K
    th += 273  # K
    eta = 1-tc/th
    eta *= 0.68
    return eta


def si2_prod_rate(P, To, Ts):
    """
    Sulfur-Iodine with steam temperature boosting nergy requirements and
    production rate.
    Parameters:
    -----------
    P: thermal power [MW]
    To: reactor outlet temperature [C]
    Ts: process temperature [C]
    Returns:
    --------
    pth: sepecific energy [kWh(th)/kg-H2]
    pr: production rate [kg/h]
    """
    eta = efficiency(To)
    pth, gamma = SI2(eta, To, Ts)
    pr = P/pth*1e3
    return pth, pr
