#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 15:13:46 2025

@author: rober
"""
import locale
locale.setlocale(locale.LC_NUMERIC, 'cs_CZ')
# Create a custom locale object with specific number formatting
locale._override_localeconv["thousands_sep"] = ""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.colors import LogNorm
from log_converter_function import log_converter_function_amps

save = 1

dirpaths = './measured spectra/'
dirpaths = './Bp 4. úkol/'
# dirpaths = 'C:/Users/rober/Desktop/lambda, teplota/'
# finding all folders and dirpaths and sorting them from oldest to newest
dirpaths_sorted = sorted(next(os.walk(dirpaths))[1], key = lambda x: os.path.getmtime(os.path.join(dirpaths, x)))

# dirpaths_sorted = [x for x in dirpaths_sorted if '37 mA' in x]

def convertcommas_bitwise(x):
    #funkce k prepisovani desetinnych carek na tecky
    return float(x.replace(b',',b'.'))
    # return float(x.replace(',','.'))

def convertcommas(x):
    #funkce k prepisovani desetinnych carek na tecky
    return float(x.replace(',','.'))

# Preprocess data to have same length and to be numpy array
def list_to_array(list_to_conv):
    min_shape_list_to_conv = min([len(list_to_conv[x]) for x in range(len(list_to_conv))])
    for x in range(len(list_to_conv)):
        list_to_conv[x] = list_to_conv[x][:min_shape_list_to_conv]
    return np.array(list_to_conv)

def plot_dirpath(path_to_directory):
    listoffiles = next(os.walk(path_to_directory))[2]
    listoffiles = [x for x in listoffiles if 'txt' in x]
    listoffiles = [x for x in listoffiles if x[-5].isnumeric()]
    # listoffiles = [x for x in listoffiles if '291' in x]
    listoffiles = sorted(listoffiles)
    # listoffiles = sorted(listoffiles, key = lambda x: os.path.getmtime(os.path.join(path_to_directory, x)))
    
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
    
    
    for file in listoffiles:
        filepath = path_to_directory + file
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
    
    
    current = np.array(current)
    angle = np.array(angle)
    wavelenght = list_to_array(wavelenght)
    intensity_arb_u = list_to_array(intensity_arb_u)
    intensity_amps = log_converter_function_amps(intensity_arb_u)
    
    unique_current_index = np.unique(current, return_index=True)[1]
    angle_matrix = np.array([angle,]*len(wavelenght[0])).transpose() #duplicate columns
    
    for i in range(len(np.unique(current))):
    
        #Robert plot----------------------------
        current_index_low = unique_current_index[i]
        try: current_index_high = unique_current_index[i+1]
        except IndexError: current_index_high = len(current)
    
        x = wavelenght[current_index_low:current_index_high]
        y = angle_matrix[current_index_low:current_index_high]
        z = intensity_amps[current_index_low:current_index_high]
        # z = intensity_arb_u[current_index_low:current_index_high]
    
        fig, ax = plt.subplots()
        cmap = plt.get_cmap('turbo')
        cmap.set_bad(color = 'black') #blacking out NaN values
        vmin, vmax = np.nanmin(z), np.nanmax(z)
    
        cs = plt.pcolormesh(x,y,z, cmap=cmap, norm=LogNorm(vmin=vmin, vmax=vmax))
        cbar = fig.colorbar(cs)
        cbar.locator = ticker.LogLocator(10)
        cbar.set_ticks(cbar.locator.tick_values(vmin,vmax)[1:-1])
        cbar.minorticks_on()
        # ax.set(xlim=(ylim=(min(y.flatten()),58300))
        # ax.set(ylim=(29800,30250))
        # ax.set(xlim=(510,520))
        # ax.set(xlim=(500,530), ylim=(2850,2920))
        # ax.set(xlim=(min(x.flatten()),518))
        # ax.set(xlim=(511,515), ylim=(2898,2902))
        ax.set_xlabel('Vlnová délka [nm]')
        ax.set_ylabel('Úhel hranolu [lib. j.]')
        cbar.set_label('Kalibrovaný signál fotodiody [A]')
        
        try:
            temperature_end = np.genfromtxt(fname=path_to_directory+"konečná teplota.txt",dtype=float,converters={0:convertcommas_bitwise})
        except FileNotFoundError: temperature_end = None
        temperature_start = header[np.where(header == 'Notes:')[0][0]][1].split("(K) = ", 1)[1][:6].replace(",",".")
        temperatures = np.array(float(temperature_start), temperature_end)
        temperatures = temperatures[~np.isnan(temperatures)]
        temperature = sum(temperatures)/len(temperatures)
        # temperature = dirsubpath[20:-10]
        
        ax.set_title('Čerpací proud: '+str(current[current_index_low]).replace(".",",") +' mA'+
                     "\n"+"Teplota: "+str(temperature).replace(".",",") + " K")  
        ax.ticklabel_format(axis='both',useLocale=True)
        plt.minorticks_on()
        plt.tight_layout()
    
        if save:
            # plt.savefig(".\\"+ "map "+str(file[:-4]) + ".png",dpi=300)
            plt.savefig(path_to_directory+ "map - "+'LD input current '+str(current[current_index_low])+' mA'+" - teplota "+str(temperature) + " K" + ".png",dpi=300)
        else:
            plt.show()

"""
# getting the newest measurment folder
dirpath = dirpaths + dirpaths_sorted[-1] + '/'
# dirpath='./measured spectra/BP úkol 3.2 - prahová podmínka - prvotní proměření úhlů - 3/'
# dirpath='./measured spectra/BP úkol 4 - max teplota (step 100)/'
# dirpath='./measured spectra/proměřování závislosti proudu s konst. teplotou/'
# dirpath='./measured spectra/opakovatelnost měření ze 20250516 (po manual seřízení objektivu)/'
plot_dirpath(dirpath)
"""

dirsubpath = './measured spectra/BP úkol 3.2 - prahová podmínka - prvotní proměření úhlů - 3/'
plot_dirpath(dirsubpath)

# for dirsubpath in dirpaths_sorted:
#     dirpath = dirpaths + dirsubpath + '/'
#     plot_dirpath(dirpath)
    
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