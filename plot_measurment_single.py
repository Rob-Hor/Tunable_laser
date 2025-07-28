# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 15:13:46 2025

@author: rober
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker, cm
from log_converter_function import log_converter_function_amps

save = 1
dirpath='./measured spectra/3. měření nové LD/'
dirpath='./measured spectra/test/'
dirpath='./measured spectra/BP úkol 1 - prahová podmínka/'

# dirpath='./measured spectra/měření Litt-Met; hranol místo mřížky; malý hranol blue max;exter nap motoru;odstíněný detektor alobalem;užší exit štěrb/'
listoffiles = next(os.walk(dirpath))[2]
listoffiles = [x for x in listoffiles if 'txt' in x]
# listoffiles = [x for x in listoffiles if '42000' in x]
# listoffiles = [x for x in listoffiles if '02' in x]
# listoffiles = sorted(listoffiles)
listoffiles = sorted(listoffiles, key = lambda x: os.path.getmtime(os.path.join(dirpath, x)))
# listoffiles = [listoffiles[24], listoffiles[34]]
listoffiles = listoffiles[0:-5:6]

angle = list()
wavelenght = list()
intensity_arb_u = list()

intensity_arb_u = list()

def convertcommas_bitwise(x):
    #funkce k prepisovani desetinnych carek na tecky
    return float(x.replace(b',',b'.'))

height = 4
ratio = 17/9
ratio = 4/3

# plt.figure(figsize=(height*ratio,height))
plt.figure()

# Preprocess data to have same length and to be numpy array
def list_to_array(list_to_conv):
    min_shape_list_to_conv = min([len(list_to_conv[x]) for x in range(len(list_to_conv))])
    for x in range(len(list_to_conv)):
        list_to_conv[x] = list_to_conv[x][:min_shape_list_to_conv]
    return np.array(list_to_conv)

for file in listoffiles:
    filepath = dirpath + file
    # number=np.genfromtxt(fname=filepath,dtype=str,delimiter='\t')[:,0]
    header_rows_num = 10
    header=np.genfromtxt(fname=filepath,dtype=str,max_rows=header_rows_num,delimiter='\t')

    # angle.append(float(header[np.where(header == 'Feedback angle (arb. u.):')[0][0]][1]))

    datacol=len(np.genfromtxt(fname=filepath,dtype=str,delimiter='\t',skip_header=header_rows_num+2)[0])-1

    convertdict={}
        #k vypsani vsech sloupcu kde se ma zmenit desetinna carka na tecku do {} zavorky
    for x in range (1,datacol+1): convertdict[x]=convertcommas_bitwise
        #vypisovani dat vsech spekter s desetinnou teckou misto carky
    data=np.genfromtxt(fname=filepath,dtype=float,delimiter='\t',skip_header=header_rows_num+2,converters=convertdict)
    
    wavelenght.append(data[:,0])
    intensity_arb_u.append(data[:,1])

    intensity = np.array(data[:,1])
    intensity = log_converter_function_amps(intensity)
    # print(len(intensity[-1]))

    # plt.plot(data[:,0],intensity[-1], label=file[29:35])
    current = float(header[np.where(header == 'Input current (mA):')[0][0]][1])

    plt.plot(wavelenght[-1],intensity, label='Čerpací proud: '+str(current).replace(".",",") +' mA')
# plt.plot(wavelenght,intensity_arb_u, label=file[-6:-4])

handles, labels = plt.gca().get_legend_handles_labels()
handles = handles[::-1]
labels = labels[::-1]
plt.legend(handles, labels,loc='best', shadow=True,fontsize =9)

plt.yscale("log")
# plt.ylim(min(min(intensity))*1,max(max(intensity))*1.1)
# plt.ylim(5*10**-13,10**-5)
plt.grid(alpha=0.6, linestyle=':')
plt.xlabel('Vlnová délka [nm]')
plt.ylabel('Kalibrovaný signál fotodiody [A]')
plt.minorticks_on()
plt.tight_layout()

if save:
    plt.savefig(dirpath+ "map slice" + ".png",dpi=300)
else:
    plt.show()

