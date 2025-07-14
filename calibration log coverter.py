#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Created on Wed Dec  4 15:12:17 2024

@author: rober
'''

import os
import pandas as pd
import numpy as np
from uncertainties import ufloat
import matplotlib.pyplot as plt
from lmfit import Model, Parameters

save = 0
dirpath='./measured spectra/kalibrace logaritmického převodníku pomocí FD odporové krabice/'
# dirpath='./measured spectra/kalibrace proudu (s interferencí motoru)/'
listoffiles = next(os.walk(dirpath))[2]
listoffiles = [x for x in listoffiles if 'txt' in x]
# listoffiles = [x for x in listoffiles if '02' in x]
listoffiles = sorted(listoffiles, key = lambda x: os.path.getmtime(os.path.join(dirpath, x)))

data_all = list()
ohms_meaning  = {"1 Tera Ohm" : 10**12,
                 "100 Giga Ohm" : 10**11,
                 "10 Giga Ohm" : 10**10,
                 "1 Giga Ohm" : 10**9,
                 "100 Mega Ohm" : 10**8}

sloupce = [None, None]# + list(columns_info_meaning.keys())
sheet = pd.DataFrame(data=sloupce).T

def convertcommas_bitwise(x):
    #funkce k prepisovani desetinnych carek na tecky
    return float(x.replace(b',',b'.'))
    
for file in listoffiles:
    filepath = dirpath + file
    # number=np.genfromtxt(fname=filepath,dtype=str,delimiter='\t')[:,0]
    header_rows_num = 10
    header=np.genfromtxt(fname=filepath,dtype=str,max_rows=header_rows_num,delimiter='\t')
    datacol=len(np.genfromtxt(fname=filepath,dtype=str,delimiter='\t',skip_header=header_rows_num+2)[0])-1

    convertdict={}
        #k vypsani vsech sloupcu kde se ma zmenit desetinna carka na tecku do {} zavorky
    for x in range (1,datacol+1): convertdict[x]=convertcommas_bitwise
        #vypisovani dat vsech spekter s desetinnou teckou misto carky
    data=np.genfromtxt(fname=filepath,dtype=float,delimiter='\t',skip_header=header_rows_num+2,converters=convertdict)

    ohms = header[np.where(header == 'Notes:')[0][0]][1]
    ohms = ohms_meaning[ohms]
    
    measured_arb_units = ufloat(np.average(data[:,1]), np.std(data[:,1]))
    real_input_current = 1/ohms
    real_input_current_err = real_input_current/10
    # current_err = vol_tage_to_current(np.std(data[:,1]), ohms)
    print(measured_arb_units)
    # data_all.append([measured_arb_units.n, real_input_current), measured_arb_units.s, np.log10(real_input_current_err)])
    data_all.append([measured_arb_units.n, real_input_current, measured_arb_units.s, real_input_current_err])
data_all = np.array(data_all)

# plt.errorbar(data_all[:,0], data_all[:,1], xerr=data_all[:,2], fmt='ko-', markersize=0.5, capsize=2.5, ecolor='black', linewidth=0.2, elinewidth=0.4, label = 'Změřená data')
"""
from scipy.interpolate import CubicSpline

x_interp = np.linspace(min(data_all[:,0]),max(data_all[:,0]), 100)
# y_interp = np.interp(x_interp,data_all[:,0], data_all[:,1])
y_interp_cube = CubicSpline(sorted(data_all[:,0]), data_all[:,1])
# plt.plot(x_interp,y_interp)
plt.plot(x_interp,y_interp_cube(x_interp), label="Cubic spline")
# plt.yscale('log')
# plt.xscale('log')
plt.xlabel(r'$I_\mathrm{log~converted}~[\mathrm{arb. u.}]$')
plt.ylabel(r'Input current$~[\mathrm{A}]$')
plt.legend()
plt.show()
"""
#%% fitting with exponential function
data_fit = [data_all[:,0],
        np.log10(data_all[:,1]),
        np.log10(data_all[:,3]),
        data_all[:,2]]

# data_fit = data_all
#hodnoty prevedene na zakladni jednotky
#data_Err = np.array(excel.iloc[1:11,4], dtype=float)

def fitfunc(x, a,b, offset):
    # return a*(x-offset)**b
    return a*np.log10(x-offset) + b

# fitovani
params = Parameters()
# params.add('a', value=0.0000000001, min=0, max=5)
# params.add('a', value=10**-18, min=0, max=1)
# params.add('b', value=3.25, min=3, max=5)
# params.add('offset', value=2110, min=1950, max=2200)

# params.add('a', value=0.0000000001, min=0, max=5)
params.add('a', value=3, min=0, max=5)
params.add('b', value=3.25, min=-25, max=5)
params.add('offset', value=2130, min=2000, max=2200)

results = Model(fitfunc).fit(data_fit[1], params, x=data_fit[0], weights=1.0/data_fit[2])
print(results.fit_report())

fig, ax = plt.subplots()
plt.grid(True,ls="dotted")
# plt.yscale('log')

# step = abs(data_X[1]-data_X[0])
# plt.xticks(np.arange(min(data_X)-step, max(data_X)+step, step=step))
# plt.yticks(np.arange(min(data_Y)-step, max(data_Y)+step, step=step))

# pojmenovani grafu a os
plt.xlabel(r'$I_\mathrm{log~converted}~[\mathrm{arb. u.}]$')
plt.ylabel(r'Input current$~[\mathrm{A}]$')
# plt.xlim(0, max(data_fit[0])*1.05)

# plt.ylim(0, max(data_fit[1])*1.2)
#osy uvnitr plotu
# plt.axhline(color='grey', lw=0.5)
# plt.axvline(color='grey', lw=0.5)


# vekresleni dat
# plt.plot(data_X, data_Y, "k.", markersize=1.5, label = "Změřená data")
#vykresleni errobaru
plt.errorbar(data_fit[0], 10**data_fit[1], xerr=data_fit[3], fmt='ko-', markersize=0.5, capsize=2.5, ecolor='black', linewidth=0.2, elinewidth=0.4, label = 'Změřená data')


# vykresleni fitovaci funkce
x = np.linspace(0,max(data_fit[0])*1.01,len(data_fit[0])*20)
a = ufloat(results.params['a'].value, results.params['a'].stderr)
b = ufloat(results.params['b'].value, results.params['b'].stderr)
offset = ufloat(results.params['offset'].value, results.params['offset'].stderr)

#TODO: zkontrolovat +- před výsledky
# plt.plot(x, 10**fitfunc(x,a.n, b.n, offset.n), ":", c="red",lw=1,
#           label = "Fit funkcí\n$y$ = %s $\cdot (x-%s)^{%s}$)"
#             %(str(("{:.2e}".format(a.n)).replace('.', ',')),
#               str(("{:.2e}".format(offset.n)).replace('.', ',')),
#             str(("{:.2e}".format(b.n)).replace('.', ','))
#             ))
if b.n > 0:
    label_plot = "Fit funkcí\n$y$ = %s $\cdot log_{10}(x-%s) + (%s)$"
elif b.n < 0:
    label_plot = "Fit funkcí\n$y$ = %s $\cdot log_{10}(x-%s) %s$"
else:
    label_plot = "Fit funkcí\n$y$ = %s $\cdot log_{10}(x-%s)$"
    
plt.plot(x, 10**fitfunc(x,a.n, b.n, offset.n), ":", c="red",lw=1,
          label = label_plot
            %(str(("{:.2f}".format(a.n)).replace('.', ',')),
              str(("{:.0f}".format(offset.n)).replace('.', ',')),
            str(("{:.1f}".format(b.n)).replace('.', ','))))

# umisteni errorbaru zmerenych dat jako prvni popisek v legende (jinak je posledni)
handles, labels = plt.gca().get_legend_handles_labels()
handles = handles[-1:] + handles[:-1]
labels = labels[-1:] + labels[:-1]
# legenda
plt.legend(handles, labels,
           loc="best", shadow=True)

if save:
    plt.savefig(dirpath+ "Fit log převodníku.png",dpi=300)
    with open("./calibration log converter.txt", "w") as f:
      f.write("10**(a*np.log10(x-offset) + b)")
      f.write("\n"+"\n"+"a = "+str(a))
      f.write("\n"+"offset = "+str(offset))
      f.write("\n"+"b = "+str(b))
else:
    plt.show()

  