#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Created on Thu Jul  4 12:22:43 2024

@author: PC
'''

import sys
def myerr(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input(exc_type)
sys.excepthook = myerr
 	#zjisteni a vypsani mozne chyby

from ctypes import windll
# buttons
MB_OK = 0x0
# icons
ICON_EXCLAIM = 0x30
ICON_STOP = 0x10

from input_current_calibration import convert_current_from_mA, convert_current_to_mA, real_current_mA
from os import walk
sys.path.append('./'+[x for x in next(walk('.'))[1] if 'rp2daq' in x][0])
import rp2daq          # import the module (must be available in your PYTHONPATH)
rp = rp2daq.Rp2daq()   # connect to the Pi Pico
# https://github.com/FilipDominec/rp2daq/tree/main



def calibrate_low_end_nm(stepper_num, conversion, step_speed):
    step_nm = -800
    print('Moving to low end position...')
    rp.stepper_move(stepper_num, to=round(conversion*step_nm), speed=step_speed, relative=True, endswitch_sensitive_down=True, reset_nanopos_at_endswitch=True)
    print('At low end position.')
    print('Initiating slow bounce back...')
    bounce_step_nm = 2
    rp.stepper_move(stepper_num, to=round(conversion*bounce_step_nm), speed=step_speed, relative=True, endswitch_sensitive_down=True)
    rp.stepper_move(stepper_num, to=round(conversion*-(bounce_step_nm*3)), speed=1, relative=True, endswitch_sensitive_down=True, reset_nanopos_at_endswitch=True)

    # backlash compensation
    backlash_calibration_const_nm = 0.70
    rp.stepper_move(stepper_num, to=round(conversion*backlash_calibration_const_nm), speed=10, relative=True, endswitch_sensitive_down=True)
    # reset nanopos to get rid of backlash by re-initialisation
    rp.stepper_init(0, dir_gpio=14, step_gpio=15, endswitch_gpio=0, inertia=30) #re-initialization of spectrometer to delete backlash
    #TODO: reinitialization from stepper number
        #rp.stepper_init(stepper_num, dir_gpio=rp.stepper_status(stepper_num)[?], step_gpio=rp.stepper_status(stepper_num)[?],
        #                   endswitch_gpio=rp.stepper_status(stepper_num)[?], inertia=rp.stepper_status(stepper_num)[?])
    print('Low end calibrated.')

def calibrate_low_end_angle(stepper_num, conversion, step_speed):
    step_angle = -200000
    print('Moving to low end position...')
    rp.stepper_move(stepper_num, to=round(conversion*step_angle), speed=step_speed, relative=True, endswitch_sensitive_down=True, reset_nanopos_at_endswitch=True)
    print('At low end position.')
    print('Initiating slow bounce back...')
    bounce_step_angle = 300
    rp.stepper_move(stepper_num, to=round(conversion*bounce_step_angle), speed=step_speed, relative=True, endswitch_sensitive_down=True)
    rp.stepper_move(stepper_num, to=round(conversion*-(bounce_step_angle*3)), speed=2, relative=True, endswitch_sensitive_down=True, reset_nanopos_at_endswitch=True)

    # backlash compensation
    # backlash_calibration_const_nm = 0.70
    # rp.stepper_move(stepper_num, to=round(conversion*backlash_calibration_const_nm), speed=10, relative=True, endswitch_sensitive_down=True)
    # reset nanopos to get rid of backlash by re-initialisation
    rp.stepper_init(1, dir_gpio=8, step_gpio=7, endswitch_gpio=1, inertia=300) #initialization of feedback prism
    #TODO: reinitialization from stepper number
        #rp.stepper_init(stepper_num, dir_gpio=rp.stepper_status(stepper_num)[?], step_gpio=rp.stepper_status(stepper_num)[?],
        #                   endswitch_gpio=rp.stepper_status(stepper_num)[?], inertia=rp.stepper_status(stepper_num)[?])
    print('Low end calibrated.')


def move_stepper_by_step_nm(stepper_num, conversion, step_speed, step_nm, callback=None):
    max_step = (780-182) # (max_nm - min_nm)
    # if rp.stepper_status(stepper_num)['endswitch'] and (step_nm<0):
    if rp.stepper_status(stepper_num).endswitch and (step_nm<0):
        warning_msg = 'At low end position. Use positive step instead of negative.'
        if sys.platform == 'win32': windll.user32.MessageBoxW(None, u'%s'%str(warning_msg), u'!!! Error !!!', MB_OK | ICON_EXCLAIM)
        else: print('At low end position. Use positive step instead of negative.')
    elif (step_nm > max_step):
        warning_msg = 'You will probably reach other end of spectrometer (cca 780 nm). Input lower step than %s nm.'%max_step
        if sys.platform == 'win32': windll.user32.MessageBoxW(None, u'%s'%str(warning_msg), u'!!! Error !!!', MB_OK | ICON_EXCLAIM)
        else: print('You will probably reach other end of spectrometer (cca 780 nm). Input lower step than %s nm.'%max_step)
    else:
        rp.stepper_move(stepper_num, to=round(conversion*step_nm), speed=step_speed, relative=True, endswitch_sensitive_down=True, _callback=callback)

def move_stepper_to_nm(stepper_num, conversion, pos_nm, low_end, step_speed, callback=None):
    if pos_nm >= 780:
        warning_msg = 'You will reach high end of spectrometer (cca 780 nm).\nInput lower target position.'
        rp.adc_stop()
        if sys.platform == 'win32': windll.user32.MessageBoxW(None, u'%s'%str(warning_msg), u'!!! Error !!!', MB_OK | ICON_EXCLAIM)
    elif pos_nm < low_end:
        warning_msg = 'You will reach low end of spectrometer (%s nm).\nInput lower target position.'%low_end
        rp.adc_stop()
        if sys.platform == 'win32': windll.user32.MessageBoxW(None, u'%s'%str(warning_msg), u'!!! Error !!!', MB_OK | ICON_EXCLAIM)
    else:
        rp.stepper_move(stepper_num, to=round(conversion*(pos_nm-low_end)), speed=step_speed, relative=False, endswitch_sensitive_down=True, _callback=callback)

def move_in_same_direction(stepper_num, conversion, low_end, next_pos):
    curr_pos = convert_stepper_nanopos_to_nm(rp.stepper_status(stepper_num).nanopos, conversion, low_end)
    if curr_pos < next_pos:same_direction = True
    else: same_direction = False
    # print("same_direction= "+str(same_direction))
    return same_direction

def get_stepper_nm(stepper_num, conversion, calibration_nm):
    #gets current position of stepper in nanometers
    return (rp.stepper_status(stepper_num)['nanopos'] / conversion) + calibration_nm

def convert_stepper_nanopos_to_nm(stepper_nanopos, conversion, calibration_nm):
    #converts current position of stepper in nanometers
    return (stepper_nanopos / conversion) + calibration_nm

def set_input_current(input_current_mA):
    rp.pwm_set_value(gpio=gpio_laser, value=convert_current_from_mA(input_current_mA))

def set_temperature(input_temp):
    rp.pwm_set_value(gpio=gpio_temp_control, value=gpio_temp_control)
    #IMPORTANT: rp.quit() does NOT turn off temperature setting. Raspberry is operating until it is disconnected from power/USB.

def set_feedback_angle_to(feedback_angle):
    angle_coversion_constant = 1000
    rp.stepper_move(1, to=round(angle_coversion_constant*feedback_angle), relative=False, speed=500, endswitch_sensitive_down=True)

def set_feedback_angle_by(feedback_angle_by_step):
    angle_coversion_constant = 1000
    rp.stepper_move(1, to=round(angle_coversion_constant*feedback_angle_by_step), relative=True, speed=500, endswitch_sensitive_down=True)


ydata = []
adc_chunk_size = 1000

def init_adc(cb):
    # clkdiv=960 --> 50 000 points per second
    # channel_mask : Masks = GPIO: 1 = 26, 2 = 27, 4 = 28; 8 = internal reference, 10 = temperature sensor
    rp.adc(channel_mask=2, infinite=True, clkdiv=960, blocksize=adc_chunk_size, _callback=cb)

gpio_laser = 11
gpio_temp_control = 12

rp.stepper_init(0, dir_gpio=14, step_gpio=15, endswitch_gpio=0, inertia=30) #initialization of spectrometer
# stepper_0_last_endpos = rp.stepper_status(0)[4]
rp.stepper_init(1, dir_gpio=8, step_gpio=7, endswitch_gpio=1, inertia=30) #initialization of feedback prism
rp.pwm_configure_pair(gpio=gpio_laser, wrap_value=65535, clkdiv=1, clkdiv_int_frac=0) #initialization of LED/LD
# rp.pwm_configure_pair(gpio=gpio_temp_control, wrap_value=65535, clkdiv=1, clkdiv_int_frac=0) #initialization of temperature control on TCLDM9 TEC driver

# print(stepper_0_last_endpos)
# conversion = 49165 #step = cca 1 nm

# rp.stepper_move(0, to=round(49165*10), relative=1, speed=100, endswitch_sensitive_down=True)

#%% Few prewritten useful commands whitout using GUI

# low_end = calibrate_low_end_pos(stepper_num=0, conversion=49165, step_speed=100, calibration_nm=183)
def backlash(stepper_num, backlash_nm, conversion):
    rp.stepper_move(stepper_num, to=round(conversion*backlash_nm), relative=1, speed=50, endswitch_sensitive_down=True)

import time
def backlash_test():
    repetitions = 2
    for i in range(repetitions):
        print(i)
        conversion = 49165
        step = 10
        backlash(+0.70, conversion) #backlash coming from high back to high
        # time.sleep(3)

        rp.stepper_move(0, to=round(conversion*step), relative=1, speed=100, endswitch_sensitive_down=True)
        time.sleep(2)

        #---------
        backlash(-0.70, conversion) #backlash coming from low back to low
        # time.sleep(3)

        rp.stepper_move(0, to=round(-1*conversion*step), relative=1, speed=100, endswitch_sensitive_down=True)
        # time.sleep(1)
        # backlash(+0.70, conversion) #backlash coming from high back to high

def backlash_test_FD():
    repetitions = 3
    rp.stepper_move(0, to=round(49165*0), relative=1, speed=100, endswitch_sensitive_down=True, reset_nanopos_at_endswitch=True)
    for i in range(repetitions):
        print(i)
        conversion = 49165
        x1 = 10
        b = 0.70
        x2 = 20
        #x1-b
        rp.stepper_move(0, to=round(conversion*(x1-b)), relative=0, speed=100, endswitch_sensitive_down=True)
        backlash(b, conversion) #backlash coming from low back to low
        # rp.stepper_move(0, to=round(conversion*x1), relative=0, speed=100, endswitch_sensitive_down=True)
        time.sleep(3)

        #---------
        rp.stepper_move(0, to=round(conversion*x2), relative=0, speed=100, endswitch_sensitive_down=True)
        time.sleep(3)
        # backlash(+0.70, conversion) #backlash coming from high back to high


def calibration_test():
    repetitions = 1
    for i in range(repetitions):
        calibrate_low_end_nm(stepper_num=0, conversion=49165, step_speed=100)
        time.sleep(2)
        rp.stepper_move(0, to=round(49165*10), relative=True, speed=100, endswitch_sensitive_down=True)
        time.sleep(2)

# calibration_test()
# backlash_test()
# backlash_test_FD()

# backlash(0, 10.20, 49165)


# rp.stepper_move(1, to=round(100*49165), relative=1, speed=100, endswitch_sensitive_down=True)

# move_stepper_by_step_nm(stepper_num=0, conversion=conversion, step_speed=100, step_nm=335)

# move_stepper_to_nm(stepper_num=0, conversion=conversion, step_speed=10, pos_nm=520,low_end=low_end, calibration_nm=182.9)

# set_feedback_angle_by(-150)
# print("feedback angle moved by -150 a.u.")

# set_input_current(60)
# calibrate_low_end_angle(stepper_num=1, conversion=1000, step_speed=500)
# set_feedback_angle_to(50500)

# print('current set')
# for i in range(5):
#     print(i)
# """ 405 nm
    # set_feedback_angle_to(50000)
    # set_feedback_angle_to(150000)
    # set_feedback_angle_to(81000)
    # set_feedback_angle_to(82500)
# """
""" 515 nm
#     set_feedback_angle_to(50000)
#     set_feedback_angle_to(70000)
#     set_feedback_angle_to(53000)
#     set_feedback_angle_to(55000)
"""
# rp.stepper_status(1)
# rp.stepper_move(1, to=round(49165*120), relative=1, speed=100, endswitch_sensitive_down=False)

# rp.quit()
