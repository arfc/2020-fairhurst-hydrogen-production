import numpy as np
import sys


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


def delta_H(Tout, Tin):
    """
    Calculates H(Tout)-H(Tin) of water at P=3.5 MPa.
    Parameters:
    -----------
    Tout: outlet temperature [C]
    Tin: inlet temperature [C]
    Returns:
    --------
    dH: enthalpy difference h(Tout)-h(Tin)
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


def lte_prod_rate(P, eta):
    """
    Low temperature electrolysis energy requirements and production rate.
    Parameters:
    -----------
    P: thermal power [MW]
    eta: themal-to-electric conversion efficiency
    Returns:
    --------
    pr: production rate [kg/h]
    see: sepecific energy [kWh(th)/kg-H2]
    """
    see = 60  # kWh(e)/kg-H2
    see /= eta
    pr = P/see*1e3
    return pr, see


def hte_req(P, Te):
    """
    Calculates electrical and thermal requirements to carry out the
    electrolysis process.
    Values from 'Efficiency of hydrogen production systems using alternative
    nuclear energy technologies', Yildiz et al., May 2005.
    Parameters:
    -----------
    P: pressure [atm]
    Te: electrolysis temperature [C]
    Returns:
    --------
    dg: electrial requirement [kJ/mol]
    tds: thermal requirement [kJ/mol]
    """
    R = 8.314  # [J/mol/K]

    dg_T = [225, 165]  # [kJ/mol]
    tds_T = [17, 99]  # [kJ/mol]
    temp = [100, 1200]  # [C]

    # dh variation with P is negligible
    dh = np.interp(Te, temp, dg_T) + np.interp(Te, temp, tds_T)
    tds = np.interp(Te, temp, tds_T) - R*(Te+273)*np.log(P)/1e3
    dg = dh - tds  # [kJ/mol]

    return dg, tds


def hte_power_req(P, To):
    """"
    Calculates energy requirements for HTE case.
    Parameters:
    -----------
    P: pressure [atm]
    To: reactor outlet temperature [C]
    Returns:
    --------
    Pth: reactor thermal power requirement [kWh/kgH2]
    gamma: Pe/Pth
    """
    ef = 0.97
    Te = ef * To  # Electrolysis temperature
    eta = efficiency(Te)

    etagammaPth, gammacPth = hte_req(P, Te)
    gammacPth += delta_H(243, 242)  # vaporization energy
    gammaPth = etagammaPth/eta
    Pth = gammaPth + gammacPth  # total power [kJ/mol]
    gamma = gammaPth/Pth  # \gamma
    Pth = Pth/(2*1.008*3.6)  # [kWh/kg-H2]
    return Pth, gamma


def hte_prod_rate(Pt, p, To):
    """
    High temperature electrolysis energy requirement and production rate.
    Parameters:
    -----------
    Pt: thermal power [MWth]
    p: pressure [atm]
    To: reactor outlet temperature [C]
    Returns:
    --------
    pr: production rate [kg/h]
    pth: sepecific energy [kWh(th)/kg-H2]
    """
    if Pt != 0:
        pth, gamma = hte_power_req(p, To)
        pr = Pt/pth*1e3
    else:
        pth = 0
        pr = 0
    return pr, pth, gamma


def hte2_power_req(P, To, Te):
    """"
    Calculates energy requirements for HTE case with steam temperature
    boosting.
    Parameters:
    -----------
    P: pressure [atm]
    To: reactor outlet temperature [C]
    Te: electrolysis temperature [C]
    Returns:
    --------
    Pth: reactor thermal power requirement [kWh/kgH2]
    gamma: Pe/Pth
    """
    ef = 0.97
    Tr = ef * To
    eta = efficiency(Tr)

    etagammaPth = hte_req(P, Te)[0]
    dH = hte_req(P, Te)[1] - hte_req(P, Tr)[1]
    etef = 0.95  # electrical-to-thermal conversion efficiency
    etagammaPth += etef * dH

    gammacPth = hte_req(P, Tr)[1]
    gammacPth += delta_H(243, 242)  # vaporization energy

    gammaPth = etagammaPth/eta
    Pth = gammaPth + gammacPth  # total power [kJ/mol]
    gamma = gammaPth/Pth  # \gamma
    Pth = Pth/(2*1.008*3.6)  # [kWh/kg-H2]
    return Pth, gamma


def hte2_prod_rate(Pt, p, To, Te):
    """
    High temperature electrolysis energy requirement and production rate.
    Parameters:
    -----------
    Pt: thermal power [MWth]
    p: pressure [atm]
    To: reactor outlet temperature [C]
    Returns:
    --------
    pr: production rate [kg/h]
    pth: sepecific energy [kWh(th)/kg-H2]
    """
    if Pt != 0:
        pth, gamma = hte2_power_req(p, To, Te)
        pr = Pt/pth*1e3
    else:
        pth = 0
        pr = 0
    return pr, pth, gamma


def si_prod_rate(P, To):
    """
    Sulfur-Iodine energy requirements and production rate.
    Values from 'Efficiency of hydrogen production systems using alternative
    nuclear energy technologies', Yildiz et al., May 2005.
    Parameters:
    -----------
    P: thermal power [MW]
    To: reactor outlet temperature [C]
    Returns:
    --------
    pr: production rate [kg/h]
    pth: sepecific energy [kWh(th)/kg-H2]
    """
    Ts = 0.97*To
    if Ts >= 750:
        temp = [750, 800, 850, 900, 950, 1000]
        sel = [600, 400, 300, 265, 245, 230]  # specfic energy [MJ/kg-H2]
        se = 1e3/3600 * np.array(sel)  # [kWh/kg-H2]
        pth = np.interp(Ts, temp, se)
        pr = P/pth*1e3
    else:
        print('Error Tout has to be above 773 C.')
        sys.exit()
    return pr, pth


def si2_power_req(eta, To, Ts):
    """"
    Calculates energy requirements for S-I 2 case.
    Values from 'Efficiency of hydrogen production systems using alternative
    nuclear energy technologies', Yildiz et al., May 2005.
    Parameters:
    -----------
    eta: thermal-to-electrical conversion efficiency
    To: reactor outlet temperature [C]
    Ts: SI process temperature [C]
    Returns:
    --------
    Pth: reactor thermal power requirement [kWh/kg-H2]
    gamma: Pe/Pth
    """
    ef = 0.97
    Tr = ef * To

    if Ts >= 750:
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
    else:
        print('Error Ts has to be above 750 C.')
        sys.exit()
    return Pth, gamma


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
    pr: production rate [kg/h]
    pth: sepecific energy [kWh(th)/kg-H2]
    """
    eta = efficiency(To)
    pth, gamma = si2_power_req(eta, To, Ts)
    pr = P/pth*1e3
    return pr, pth, gamma
