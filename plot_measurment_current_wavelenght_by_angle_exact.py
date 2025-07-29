#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 15:13:46 2025

@author: rober
"""
import locale
locale.setlocale(locale.LC_NUMERIC, 'cs_CZ')

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from log_converter_function import log_converter_function_amps
from matplotlib.colors import LogNorm

save = 0

dirpaths = './measured spectra/'
# finding all folders and dirpaths and sorting them from oldest to newest
dirpaths_sorted = sorted(next(os.walk(dirpaths))[1], key = lambda x: os.path.getmtime(os.path.join(dirpaths, x)))
# getting the newest measurment folder
# dirpath = dirpaths + dirpaths_sorted[-1] + '/'

dirpath='./measured spectra/BP úkol 1 - prahová podmínka/'
# dirpath='./measured spectra/BP úkol 3.2 - prahová podmínka - různé úhly/'

listoffiles = next(os.walk(dirpath))[2]
listoffiles = [x for x in listoffiles if 'txt' in x]
listoffiles = [x for x in listoffiles if x[-5].isnumeric()]
# listoffiles = [x for x in listoffiles if '291' in x]
# listoffiles = sorted(listoffiles)
listoffiles = sorted(listoffiles, key = lambda x: os.path.getmtime(os.path.join(dirpath, x)))

#%% plots only measurment with highest last number (i.e. oldest and probably from finest step)
# Otherwise nonreproducibility of measurment will make artefacts in final plot
for val in reversed(listoffiles):
    for i in reversed(listoffiles):
        if (i[:-6] in val) and (i[-6:-4] < val[-6:-4]):
            listoffiles.remove(i)

#%%
current = list()
angle = list()
wavelenght = list()
intensity_arb_u = list()


def convertcommas_bitwise(x):
    #funkce k prepisovani desetinnych carek na tecky
    # return float(x.replace(b',',b'.'))
    return float(x.replace(',','.'))

for file in listoffiles:
    filepath = dirpath + file
    # number=np.genfromtxt(fname=filepath,dtype=str,delimiter='\t')[:,0]
    header_rows_num = 11
    header=np.genfromtxt(fname=filepath,dtype=str,max_rows=header_rows_num,delimiter='\t')

    # if not "Measurment project:" in header:
    #     print("Not a file with relevant data")
    #     continue

    try:
        current.append(float(header[np.where(header == 'Input current (mA):')[0][0]][1]))
        angle.append(float(header[np.where(header == 'Feedback angle (arb. u.):')[0][0]][1]))
        datacol=len(np.genfromtxt(fname=filepath,dtype=str,delimiter='\t',skip_header=header_rows_num+2)[0])-1
        convertdict={}
            #k vypsani vsech sloupcu kde se ma zmenit desetinna carka na tecku do {} zavorky
        for x in range (1,datacol+1): convertdict[x]=convertcommas_bitwise
            #vypisovani dat vsech spekter s desetinnou teckou misto carky
        data=np.genfromtxt(fname=filepath,dtype=float,delimiter='\t',skip_header=header_rows_num+2,converters=convertdict)
    except IndexError:
        continue

    wavelenght.append(data[:,0])
    # wavelenght = np.append(wavelenght, data[:,0], axis=0)
    intensity_arb_u.append(data[:,1])

# Preprocess data to have same length and to be numpy array
def list_to_array(list_to_conv):
    min_shape_list_to_conv = min([len(list_to_conv[x]) for x in range(len(list_to_conv))])
    for x in range(len(list_to_conv)):
        list_to_conv[x] = list_to_conv[x][:min_shape_list_to_conv]
    return np.array(list_to_conv)

current = np.array(current)
angle = np.array(angle)
wavelenght = list_to_array(wavelenght)
intensity_arb_u = list_to_array(intensity_arb_u)
intensity_amps = log_converter_function_amps(intensity_arb_u)

unique_angle_index = np.unique(angle, return_index=True)[1]
current_matrix = np.array([current,]*len(wavelenght[0])).transpose() #duplicate columns
len_unique_angle = len(np.unique(angle))

for i in range(len_unique_angle):

    #Robert plot----------------------------
    angle_index_low = unique_angle_index[i]
    try: angle_index_high = unique_angle_index[i+1]
    except IndexError: angle_index_high = len(angle)

    x = wavelenght[angle_index_low::len_unique_angle]
    y = current_matrix[angle_index_low::len_unique_angle]
    z = intensity_amps[angle_index_low::len_unique_angle]
    # z = intensity_arb_u[angle_index_low::len_unique_angle]

    fig, ax = plt.subplots()
    cmap = plt.get_cmap('turbo')
    cmap.set_bad(color = 'black') #blacking out NaN values
    vmin, vmax = np.nanmin(z), np.nanmax(z) #setting min and max of colorbar and ignoring NaN values
    vmin = 10**-17
    vmin = 10**-11
    cs = plt.pcolormesh(x,y,z, cmap=cmap, norm=LogNorm(vmin=vmin, vmax=vmax))
    cbar = fig.colorbar(cs)
    cbar.locator = ticker.LogLocator(10)
    cbar.set_ticks(cbar.locator.tick_values(vmin,vmax)[1:-1])
    # cbar.minorticks_on()

    # plt.plot(x,y, 'k. ') #blackout measured data to reveal interpolated parts of graph

    # ax.set(xlim=(min(x.flatten(),max(x.flatten())), ylim=(min(y.flatten()),58300))
    # ax.set(xlim=(min(x.flatten()),max(x.flatten())), ylim=(57400,58400))
    # ax.set(xlim=(512,518))
    ax.set(xlim=(513,517), ylim=(30,max(y.flatten())))
    # ax.set(xlim=(min(x.flatten()),518))
    # ax.set(xlim=(511,515), ylim=(2898,2902))

    ax.set_xlabel('Vlnová délka [nm]')
    ax.set_ylabel('Čerpací proud LD [mA]')
    cbar.set_label('Kalibrovaný signál fotodiody [A]')
    ax.set_title(r'LD teplota: pokojová - úhel '+str(int(angle[angle_index_low])))

    ax.ticklabel_format(axis='both',useLocale=True)
    plt.minorticks_on()
    plt.tight_layout()

    if save:
        # plt.savefig(".\\"+ "map "+str(file[:-4]) + ".png",dpi=300)
        plt.savefig(dirpath+ "map - "+'LD teplota - pokojová - úhel ' +str(int(angle[angle_index_low]))+ ".png",dpi=300)
    else:
        plt.show()

#Robert plot single map----------------------------
"""
fig, ax = plt.subplots()

x = wavelenght.flatten()
angle_matrix = np.array([angle,]*len(wavelenght[0])).transpose() #duplicate columns
y = angle_matrix.flatten()

z = intensity_amps.flatten()

levels = np.logspace(np.log10(z.min()),np.log10(z.max()), 500)
cs = plt.tricontourf(x,y,z, cmap='turbo',levels=levels, locator=ticker.LogLocator(subs="auto"))
cbar = fig.colorbar(cs)
cbar.locator = ticker.LogLocator(10)
cbar.set_ticks(cbar.locator.tick_values(z.min(), z.max())[1:-1])
cbar.minorticks_on()

# plt.plot(x,y, 'k. ') #blackout measured data to reveal interpolated parts of graph
length=400
ax.set(xlim=(min(x),max(x)), ylim=(30300,30700))
# ax.set(xlim=(min(x),max(x)), ylim=(2845,2900))
# ax.set(xlim=(510,520), ylim=(2870,2885))
# ax.set(xlim=(500,530), ylim=(2850,2920))
# ax.set(xlim=(511,519), ylim=(30300,30750))
# ax.set(xlim=(511,519), ylim=(28700,29100))
ax.set(xlim=(511,519), ylim=(30300,30300+length))
# ax.set(xlim=(511,519), ylim=(28700,28700+length))
# ax.set(xlim=(511,515), ylim=(2898,2902))
ax.set_xlabel('Vlnová délka [nm]')
ax.set_ylabel('Úhel hranolu [lib. j.]')
cbar.set_label('Kalibrovaný signál fotodiody [A]')
# ax.set_title("Robertův plot")

plt.minorticks_on()
plt.tight_layout()

if save:
    # plt.savefig(".\\"+ "map "+str(file[:-4]) + ".png",dpi=300)
    plt.savefig(dirpath+ "map "+str(file[:-4]) + ".png",dpi=300)
else:
    plt.show()
"""

#Filip plot----------------------------
"""
fig, ax = plt.subplots()

xs = wavelenght
ys = intensity_arb_u
# ys = 2**(ys/100-23)
# ys = intensity_amps
hdrlen = 0
param = np.linspace(0, 1, len(angle))
cmaprange1, cmaprange2 = np.min(ys), np.max(ys)

#Linear version
levels = np.linspace(cmaprange1, cmaprange2, 500)
cs = ax.contourf(xs[0][hdrlen:], param, ys, levels=levels, cmap='turbo', )

#Log version
# levels = np.logspace(cmaprange1, cmaprange2, 500)
# cs = ax.contourf(xs[0][hdrlen:], param, ys, levels=levels, cmap='turbo', locator=ticker.LogLocator(), )

cbar = fig.colorbar(cs)
ax.set_xlabel('spectrometer wavelength (nm)')
ax.set_ylabel('tuning angle (a.u.)')
cbar.set_label('logarithmic photodiode signal (a.u.)')
ax.set_title("Filipovo Nihilnovy")
plt.show()
"""