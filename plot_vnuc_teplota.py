# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 13:59:41 2025

@author: rober
"""

import matplotlib.pyplot as plt
import numpy as np
import locale
locale.setlocale(locale.LC_NUMERIC, 'cs_CZ')
# Create a custom locale object with specific number formatting
locale._override_localeconv["thousands_sep"] = ""

save = 0

nm_min = [
        513.2,  513.5,          514.9, 
        512.9, 	513.3,          514.9,
        513.1, 	513.8, 	513.7, 	515.5]
nm_base = np.array([
        515.5,  515.7,          516.2, 
        515.4, 	515.4,          516.0,
        515.3, 	515.3, 	515.1, 	515.8])
nm_max = [
        517.2,  517.4,          517.3, 
        517.2, 	517.1,          517.3,
        517.0, 	516.8, 	517.1, 	516.9]
temp = np.array([
        281.3,  303.5,          318.6, 
        281.3,  303.5,          318.6, 
        281.3,  303.5,  310.7,  318.6] )
temp = np.array([
        281.4,  303.8,          318.4, 
        281.2,  303.4,          318.6, 
        281.3,  303.2,  310.7,  318.7] )
current = np.array([
        44,     44,             44, 
        40,     40,             40, 
        37,     37,     37,     37])

xerr = np.array([nm_base-nm_min, nm_max-nm_base])
yerr = np.array([[0.2]*10, [0.2]*10])
zerr = np.array([[0.1]*10, [0.1]*10])

# ax = plt.figure().add_subplot(projection='3d')
fig, ax = plt.subplots()

ax.set_xlabel('Teplota LD [K]')
ax.set_ylabel('Vlnová délka [nm]')
# ax.set_zlabel("current mA")

# ax.errorbar(nm_base, temp, current, xerr, yerr, zerr, fmt='ko', markersize=0.5, capsize=2.5, linewidth=0.2, elinewidth=0.4)


from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle


# plt.errorbar(temp[0:3], nm_base[0:3], xerr[:,0:3], yerr[:,0:3], fmt='o--', markersize=0.5, capsize=5, linewidth=0.5, elinewidth=3, label="44 mA")
# plt.errorbar(temp[3:6], nm_base[3:6], xerr[:,3:6], yerr[:,3:6], fmt='o--', markersize=0.5, capsize=5, linewidth=0.5, elinewidth=3, label="40 mA")
# plt.errorbar(temp[6:], nm_base[6:], xerr[:,6:], yerr[:,6:], fmt='o--', markersize=0.5, capsize=5, linewidth=0.5, elinewidth=3, label="37 mA")
"""
plt.plot(temp[0:3], nm_max[0:3], 'o--', label=r"Max vnucená $\lambda$ při $I$ = 44 mA", color="blue")
plt.plot(temp[0:3], nm_min[0:3], 's--', label=r"Min vnucená $\lambda$ při $I$ = 44 mA", color="blue")

plt.plot(temp[3:6], nm_max[3:6], 'o--', label=r"Max vnucená $\lambda$ při $I$ = 40 mA", color="red")
plt.plot(temp[3:6], nm_min[3:6], 's--', label=r"Min vnucená $\lambda$ při $I$ = 40 mA", color="red")

plt.plot(temp[6:], nm_max[6:], 'o--', label=r"Max vnucená $\lambda$ při $I$ = 37 mA", color="green")
plt.plot(temp[6:], nm_min[6:], 's--', label=r"Min vnucená $\lambda$ při $I$ = 37 mA", color="green")
"""
temp_err = [0.2]
nm_err = [0.1]
markersize=5
capsize=2.5
linewidth=0.8
elinewidth=0.4

plt.errorbar(temp[0:3], nm_max[0:3], nm_err*3, temp_err*3, fmt='o--', label=r"Max vnucená $\lambda$ při $I$ = 44 mA", color="blue", markersize=markersize, capsize=capsize, linewidth=linewidth, elinewidth=elinewidth)
plt.errorbar(temp[0:3], nm_min[0:3], nm_err*3, temp_err*3, fmt='s--', label=r"Min vnucená $\lambda$ při $I$ = 44 mA", color="blue", markersize=markersize, capsize=capsize, linewidth=linewidth, elinewidth=elinewidth)

plt.errorbar(temp[3:6], nm_max[3:6], nm_err*3, temp_err*3, fmt='o--', label=r"Max vnucená $\lambda$ při $I$ = 40 mA", color="green", markersize=markersize, capsize=capsize, linewidth=linewidth, elinewidth=elinewidth)
plt.errorbar(temp[3:6], nm_min[3:6], nm_err*3, temp_err*3, fmt='s--', label=r"Min vnucená $\lambda$ při $I$ = 40 mA", color="green", markersize=markersize, capsize=capsize, linewidth=linewidth, elinewidth=elinewidth)

plt.errorbar(temp[6:], nm_max[6:], nm_err*4, temp_err*4, fmt='o--', label=r"Max vnucená $\lambda$ při $I$ = 37 mA", color="red", markersize=markersize, capsize=capsize, linewidth=linewidth, elinewidth=elinewidth)
plt.errorbar(temp[6:], nm_min[6:], nm_err*4, temp_err*4, fmt='s--', label=r"Min vnucená $\lambda$ při $I$ = 37 mA", color="red", markersize=markersize, capsize=capsize, linewidth=linewidth, elinewidth=elinewidth)


plt.legend(loc="best", shadow=True)
ax.ticklabel_format(axis='both',useLocale=True)
# plt.grid(True,ls="dotted")
plt.grid(alpha=0.6, linestyle=':')

plt.minorticks_on()
plt.tight_layout()

if save:
    plt.savefig("./Bp 4. úkol/graf - vnucená na teplotě.png",dpi=300)
else:
    plt.show()

def make_error_boxes(ax, xdata, ydata, xerror, yerror,facecolor,label,
                     edgecolor='none', alpha=0.25):

    # Loop over data points; create box from errors at each point
    errorboxes = [Rectangle((x - xe[0], y - ye[0]), xe.sum(), ye.sum(), label=label)
                  for x, y, xe, ye in zip(xdata, ydata, xerror.T, yerror.T)]

    # Create patch collection with specified colour/alpha
    pc = PatchCollection(errorboxes,facecolor=facecolor, alpha=alpha, edgecolor=edgecolor)

    # Add collection to Axes
    ax.add_collection(pc)

    # Plot errorbars
    artists = ax.errorbar(xdata, ydata, xerr=xerror, yerr=yerror,
                          fmt='None', ecolor='None', label=label)

    return artists

def make_plot(ax, x, y, xerr, yerr, facecolor, label):
    # Create figure and Axes
    fig, ax = plt.subplots(1)
    
    # Call function to create error boxes
    make_error_boxes(ax, x, y, xerr, yerr, facecolor, label)
    # make_error_boxes(ax, temp[0:3], nm_base[0:3], yerr[:,0:3], xerr[:,0:3], facecolor="red", label="44 mA")
    # make_error_boxes(ax, temp[3:6], nm_base[3:6], yerr[:,3:6], xerr[:,3:6], facecolor="blue", label="40 mA")
    # make_error_boxes(ax, temp[6:], nm_base[6:], yerr[:,6:], xerr[:,6:], facecolor="green", label="37 mA")
    ax.set_xlabel('Teplota LD [K]')
    ax.set_ylabel('Vlnová délka [nm]')
    
    plt.legend(loc="best", shadow=True)
    ax.ticklabel_format(axis='both',useLocale=True)
    plt.minorticks_on()
    plt.tight_layout()
    
    plt.show()

# make_plot(ax, temp[0:3], nm_base[0:3], yerr[:,0:3], xerr[:,0:3], facecolor="red", label="44 mA")
# make_plot(ax, temp[3:6], nm_base[3:6], yerr[:,3:6], xerr[:,3:6], facecolor="blue", label="40 mA")
# make_plot(ax, temp[6:], nm_base[6:], yerr[:,6:], xerr[:,6:], facecolor="green", label="37 mA")

def make_plots():
    # Create figure and Axes
    fig, ax = plt.subplots(1)
    
    # Call function to create error boxes
    make_error_boxes(ax, temp[0:3], nm_base[0:3], yerr[:,0:3], xerr[:,0:3], facecolor="red", label="44 mA")
    make_error_boxes(ax, temp[3:6], nm_base[3:6], yerr[:,3:6], xerr[:,3:6], facecolor="blue", label="40 mA")
    make_error_boxes(ax, temp[6:], nm_base[6:], yerr[:,6:], xerr[:,6:], facecolor="green", label="37 mA")
    ax.set_xlabel('Teplota LD [K]')
    ax.set_ylabel('Vlnová délka [nm]')
    
    plt.legend(loc="best", shadow=True)
    ax.ticklabel_format(axis='both',useLocale=True)
    plt.minorticks_on()
    plt.tight_layout()
    
    plt.show()

# make_plots()