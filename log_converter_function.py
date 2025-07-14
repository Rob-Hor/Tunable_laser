#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 28 17:39:16 2025

@author: rober
"""
from numpy import log10

def log_converter_function_amps(x):
    a = 3.69
    offset = 2131
    b = -18.1
    return 10**(a*log10(x-offset) + b)