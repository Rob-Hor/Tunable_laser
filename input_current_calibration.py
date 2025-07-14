# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 10:23:47 2025
Measured: 7.3.2025
@author: Robert Horesovsky 
"""
from numpy import interp

real_current_mA = [0,0.006, 0.01, 0.022, 0.037, 0.09, 0.408, 0.765, 1.77, 2.23, 2.7,
                   3.5, 5.65, 9, 13, 17, 22, 27, 52, 63, 79,
                   105, 132, 160, 185]
raspberry_values = [0,1000, 1500, 3000, 5000, 10000, 13000, 15000, 20000, 22000, 23000,
                    24000, 25000, 26000, 27000, 28000, 29000, 30000, 35000, 37000, 40000,
                    45000, 50000, 55000, 60000]
filepath = __file__

def convert_current_from_mA(wanted_current_mA: float):
    if wanted_current_mA > max(real_current_mA):
        raise Exception("Current cannot be set higher than %s mA. Choose lower value or update values in file: %s"
                        %(max(real_current_mA), filepath))
    else:
        return int(interp(wanted_current_mA, real_current_mA, raspberry_values))
    
def convert_current_to_mA(Raspberry_current: int):
    if Raspberry_current > max(raspberry_values):
        raise Exception("Current cannot be set higher than %s Raspberry value." %max(raspberry_values))
    else:
        return float(interp(Raspberry_current, raspberry_values, real_current_mA))