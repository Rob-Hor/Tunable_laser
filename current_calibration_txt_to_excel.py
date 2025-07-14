#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Created on Wed Dec  4 15:12:17 2024

@author: rober
'''

import os
import pandas as pd
import numpy as np
from uncertainties import ufloat, unumpy
import matplotlib.pyplot as plt
from re import findall

dirpath='./measured spectra/kalibrace proudu/'
# dirpath='./measured spectra/kalibrace proudu (s interferencí motoru)/'
listoffiles = next(os.walk(dirpath))[2]
listoffiles = [x for x in listoffiles if 'txt' in x]
listoffiles = sorted(listoffiles, key = lambda x: os.path.getmtime(os.path.join(dirpath, x)))

data_all = list()

sloupce = [None, None]# + list(columns_info_meaning.keys())
sheet = pd.DataFrame(data=sloupce).T

def convertcommas_bitwise(x):
    #funkce k prepisovani desetinnych carek na tecky
    return float(x.replace(b',',b'.'))

def voltage_to_current(x, ohms):
    voltage = x / (2**12 - 1) * 3.3 # convert from arb. u. to volts
    ## TODO precisely compute the voltage divider %
    voltage = voltage /0.42 # calculate in voltage divider guessed 42% because of impedance of Raspberry
    current = voltage / ohms
    return current
    
for file in listoffiles:
    filepath = dirpath + file
    # number=np.genfromtxt(fname=filepath,dtype=str,delimiter='\t')[:,0]
    header_rows_num = 7
    header=np.genfromtxt(fname=filepath,dtype=str,max_rows=header_rows_num,delimiter='\t')
    datacol=len(np.genfromtxt(fname=filepath,dtype=str,delimiter='\t',skip_header=header_rows_num+2)[0])-1

    convertdict={}
        #k vypsani vsech sloupcu kde se ma zmenit desetinna carka na tecku do {} zavorky
    for x in range (1,datacol+1): convertdict[x]=convertcommas_bitwise
        #vypisovani dat vsech spekter s desetinnou teckou misto carky
    data=np.genfromtxt(fname=filepath,dtype=float,delimiter='\t',skip_header=header_rows_num+2,converters=convertdict)

    ohms = header[np.where(header == 'Excitation light:')[0][0]][1].replace(',','.')
    ohms = float(findall(r'[-+]?(?:\d*\.*\d+)', ohms)[0])
    
    current = voltage_to_current(unumpy.uarray(np.average(data[:,1]), np.std(data[:,1])), ohms) * 1000
    # current_err = voltage_to_current(np.std(data[:,1]), ohms)
    input_current = float(header[np.where(header == 'Input current:')[0][0]][1])
    print(current)
    data_all.append([input_current, current.n, current.s])
data_all = np.array(data_all)

plt.errorbar(data_all[:,0], data_all[:,1], yerr=data_all[:,2], fmt='ko', markersize=0.5, capsize=2.5, ecolor='black', elinewidth=0.4, label = 'Změřená data')
plt.xlabel(r'Input current$~[\mathrm{arb. u.}]$')
plt.ylabel(r'$I_\mathrm{real}~[\mathrm{mA}]$')
plt.legend()
plt.show()
