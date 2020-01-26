""" This script analyses fuel consumption in a year.
The input data to analyze has to have 'uiuc-fuel-consumption.txt' format.
The outputs of the script are:
- Total fuel consumed in a year.
- Average fuel consumed (total fuel consumed/365).
- Plot of the fuel consumed throughout the year.
"""

import numpy as np
import matplotlib.pyplot as plt


def plotfuel(fuel):
    """ Plots 'fuel'.

    Parameters:
    -----------
    fuel: list
        list of values to be plotted. First value corresponds to the
        beginning of the year.

    Returns:
    --------

    """
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.plot(fuel)
    ax.set_title('Fuel Consumption')
    ax.grid()
    ax.set(xlim=(0, 364), ylim=(0, 850))
    ax.set_xlabel("Days", fontsize=14)
    ax.set_ylabel("Quantity (Gallons)", fontsize=14)
    handles, labels = ax.get_legend_handles_labels()
    plt.savefig('uiuc-unleaded', dpi=300, bbox_inches="tight")
    plt.close()


def main():
    inFile = 'uiuc-fuel-consumption.txt'
    with open(inFile, 'r') as i:
        data = i.readlines()
    lines = list()
    for line in data:
        lines.append(line.split())

    lmonth = []
    lday = []
    lunleaded = []
    ldiesel = []
    le85 = []

    for info in lines[1:]:
        lmonth.append(int(info[0]))
        lday.append(int(info[1]))
        lunleaded.append(float(info[2]))
        ldiesel.append(float(info[3]))
        le85.append(float(info[4]))

    unleaded = []
    diesel = []
    e85 = []

    for mo in range(1, 13):
        if mo == 4 or mo == 6 or mo == 9 or mo == 11:
            end = 31  # Months with 30 days
        elif mo == 2:
            end = 29  # In 2019 February had 28 days
        else:
            end = 32  # Months with 31 days

        for da in range(1, end):
            sumu = 0
            sumd = 0
            sume = 0
            for i in range(len(lmonth)):
                if lday[i] == da and lmonth[i] == mo:
                    sumu += lunleaded[i]
                    sumd += ldiesel[i]
                    sume += le85[i]
            unleaded.append(round(sumu, 2))
            diesel.append(round(sumd, 2))
            e85.append(round(sume, 2))

    print('Total unleaded: ', round(sum(unleaded), 2))
    print('Total diesel: ', round(sum(diesel), 2))
    print('Total e85: ', round(sum(e85), 2))

    print('avg per day unleaded: ', round(sum(unleaded)/len(unleaded), 2))
    print('avg per day diesel: ', round(sum(diesel)/len(diesel), 2))
    print('avg per day e85: ', round(sum(e85)/len(e85), 2))

    plotfuel(unleaded)


if __name__ == "__main__":
    main()
