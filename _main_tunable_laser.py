#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Created on Thu Jul  4 08:39:52 2024

@author: Robert H. & Filip D.
'''

import sys
from serial import SerialException
from ctypes import windll
# zjisteni a vypsani mozne chyby
def myerr(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input(exc_type)
sys.excepthook = myerr
 	# zjisteni a vypsani mozne chyby

try: import hw_backend # imports rp2daq and my custom built functions for monochromator
except (RuntimeError, SerialException) as error:
    # button
    MB_OK = 0x0
    # icons
    # ICON_EXCLAIM = 0x30
    ICON_STOP = 0x10
    if sys.platform == 'win32':
        windll.user32.MessageBoxW(None, u'%s\n\nTry reconnecting USB.' %str(error),
                                  u'!!! Error !!!', MB_OK | ICON_STOP)
    sys.exit()

# from input_current_calibration import convert_current_from_mA, convert_current_to_mA
import guisettingssaver
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QThread, QSettings, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from datetime import datetime
from numpy import arange, array
import pandas as pd
import time
import os
import threading

from log_converter_function import log_converter_function_amps
# Makes icon in .ui visible on Windows OS taskbar
if sys.platform == 'win32': windll.shell32.SetCurrentProcessExplicitAppUserModelID('fzu.tunable_laser.app')

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Load the UI Page
        uic.loadUi('_main_tunable_laser.ui', self)
        self.centralwidget.setContentsMargins(6, 6, 6, 6) #setting margins here because hint from .ui doesn't work

        # self.canvas.hide()
        #TODO plt toolbar same as canvas and not this
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.addToolBar(Qt.BottomToolBarArea, self.toolbar)
        self.toolbar.hide()
        self.resize(self.minimumSizeHint())

        # Load last settings
        self.settings = QSettings('settings.ini', QSettings.IniFormat)
        guisettingssaver.GuiRestore(self,self.settings)


        self.conversion_nm = 49165 #step = cca 1 nm (changed from 49199 in 14.4.2025)
        '''
        # TODO convert between units
        self.units = {'nm':'Wavelenghts',
                      'eV':'Energy',
                      'cm-1':'Raman shift'}
        '''
        self.data_xlabel = 'Wavelength (nm)'
        self.data_ylabel = 'Intensity (arb. u.)'

        self.thread_calibrate = calibrate()
        self.buttonCalibrate.clicked.connect(self.thread_calibrate.start)

        self.thread_acquire = acquire()
        self.buttonAcquire.clicked.connect(self.thread_acquire.start)

        self.buttonStop.clicked.connect(self.stop)
        self.buttonClear_spectra.clicked.connect(self.clear_spectra)

        if self.checkBoxAutomaticSaveTxt.isChecked(): self.buttonSaveTxt.hide()
        # shows button when checkbox unchecked
        self.checkBoxAutomaticSaveTxt.stateChanged.connect(lambda: self.update_checkBox_button_state(self.buttonSaveTxt))
        self.buttonSaveTxt.clicked.connect(self.save_last_to_txt)

        if self.checkBoxAutomaticSavePng.isChecked(): self.buttonSavePng.hide()
        # shows button when checkbox unchecked
        self.checkBoxAutomaticSavePng.stateChanged.connect(lambda: self.update_checkBox_button_state(self.buttonSavePng))
        self.buttonSavePng.clicked.connect(self.save_last_to_png)

        self.update_checkBoxSaveDefault_state()
        self.checkBoxSaveDefault.stateChanged.connect(self.update_checkBoxSaveDefault_state)

        # if self.textRange_current_to.textChanged and (float(self.textRange_current_to.text()) > max(hw_backend.real_current_mA)):

        self.textRange_current_to.textEdited.connect(lambda: self.check_max_mA(self.textRange_current_to))
        self.textRange_current_from.textEdited.connect(lambda: self.check_max_mA(self.textRange_current_from))

        self.canvas_clear()
        self.canvas.show()
        self.show() #pops up window to the foreground when started

        self.label_timer.hide()
        self.timer.hide()
        self.timer_start()

    
    def timer_start(self):
        self.time_left_int = 0

        self.my_qtimer = QTimer(self)
        self.my_qtimer.timeout.connect(self.timer_timeout)
        self.my_qtimer.start(1000)

    def timer_timeout(self):
        self.time_left_int -= 1
        self.timer.setText(time.strftime('%H:%M:%S', time.gmtime(self.time_left_int)))
        if self.time_left_int <= 0:
            self.timer.hide()
            self.label_timer.hide()

    def check_max_mA(self, LineEdit):
        #checks and corrects if user have set miliamps which are not in calibrated range
        try:
            max_mA = float(convertcommas(LineEdit.text()))
            if float(max_mA) > max(hw_backend.real_current_mA):
                LineEdit.setText(str(max(hw_backend.real_current_mA)))
            elif float(max_mA) < min(hw_backend.real_current_mA):
                LineEdit.setText(str(min(hw_backend.real_current_mA)))
        except: pass
        
    def update_checkBox_button_state(self, button):
        button.hide() if self.sender().isChecked() else button.show()

    def update_checkBoxSaveDefault_state(self):
        if not self.checkBoxSaveDefault.isChecked():
            self.labelDirpath_txt.setEnabled(True)
            self.textDirpath_txt.setEnabled(True)
        else:
            self.labelDirpath_txt.setEnabled(False)
            self.textDirpath_txt.setEnabled(False)
            self.textDirpath_txt.setText('./measured spectra/')

    def update_plot(self):
        # Trigger the canvas to update and redraw.
        show_num = 10
        if len(self.canvas.axes.get_lines()) > show_num:
            for curves in self.canvas.axes.get_lines()[:-show_num]:
                curves.remove()
        # self.canvas.axes = self.canvas.axes.get_lines()[-2:]
        self.canvas.axes.axis('on')
        self.curve.set_data(self.data_x, self.data_y)
        self.canvas.axes.set_xlim([(self.range_from-self.range_lenght*0.01), (self.range_to+self.range_lenght*0.01)])
        if self.data_y:
            data_y_size = abs(max(self.data_y)-min(self.data_y))
            self.canvas.axes.set_ylim([min(self.data_y)-data_y_size*0.03, max(self.data_y)+data_y_size*0.03])
        self.canvas.axes.minorticks_on()
        self.canvas.axes.set_xlabel(self.data_xlabel)
        self.canvas.axes.set_ylabel(self.data_ylabel)

        handles, labels = self.canvas.axes.get_legend_handles_labels()
        handles, labels = handles[-show_num:], labels[-show_num:]
        self.canvas.axes.legend(handles, labels,loc='best', shadow=True)
        # self.canvas.draw()
        self.canvas.draw_idle()
        self.canvas.flush_events()

    def get_file_name(self):
        self.text_info = pd.DataFrame([['Measurement project:', self.textData_project.text()],
                                    ['Time of acquisition:', self.data_time.strftime('%Y-%m-%d %H:%M:%S')],
                                    ['Excitation light:', self.textData_exc_light.text()],
                                    ['Sample:', self.textData_sample.text()],
                                    ['Filter:', self.textData_filter.text()],
                                    ['Detector:', self.textData_detector.text()],
                                    ['Input current (mA):', str(self.current_input_current)],
                                    # ['Temperature (K):', str(self.current_temperature)],
                                    ['Feedback angle (arb. u.):', str(self.current_feedback_angle)],
                                    ['Monochromator speed (arb. u.):', self.textStep_speed.text()],

                                    ['Notes:', self.textData_notes.text()],
                                    []])

        #datum_title//dalsi info_00.txt
        self.file_name = '_'.join([inputed for inputed in self.text_info.iloc[2:-2][1] if (inputed != '')])

    #TODO
    def stop(self): ##NEFUNGUJE: vše proběhne, ale program pak už nezvládne další Acquire
                    # nápad: možná místo move by step=0 je potřeba aby Filip napsal funkci stepper_stop() díky které se spustí callback od stepper acquire
        #https://forum.pythonguis.com/t/pause-a-running-worker-thread/147/4?u=martin
        print('\n')
        self.timer.hide()
        self.label_timer.hide()

        # for thread in threading.enumerate(): print(thread.name)
        try: hw_backend.rp.adc_stop() # stop adc acquisition
        except Exception as error_stop:
            print('Tried to stop adc but for some reason coudln\'t. \n', type(error_stop).__name__, ' ', error_stop)
            pass

        hw_backend.set_input_current(0) # turn off input current
        # stop stepper == move by step size=0 ##NEFUNGUJE
        hw_backend.move_stepper_by_step_nm(stepper_num=0, conversion=self.conversion_nm, step_speed=5, step_nm=0.001)
        print('\nstopped acquisition')

    def canvas_clear(self):
        self.canvas.axes.clear()
        self.canvas.axes.axis('off')
            # rgb(240, 240, 240)
        # self.canvas.draw()

    #TODO
    def clear_spectra(self): #NEFUNGUJE: Graf se smaže, ale při dalším Acquire už se nevykreslují data (ale data se sbírají a uloží)
        # self.canvas.fig.clf()
        # self.data_x, self.data_y = list(), list()


        # self.canvas.hide()
        self.canvas_clear()

        self.toolbar.hide()
        self.buttonSaveTxt.setEnabled(False)
        self.setGeometry(self.x(), self.y(), self.width(), self.minimumHeight())
        # self.resize(self.minimumSizeHint())


    def save_last_to_txt(self): # Save Info + Data to .txt file
        text_data = pd.DataFrame([[self.data_xlabel] + self.data_x,
                             [self.data_ylabel] + self.data_y]).T
        text_all = pd.concat([self.text_info, text_data])
        text_all.to_csv(self.dirpath_project+self.data_name+'.txt', sep='\t', index=False, header=False, mode='x')

    def save_last_to_png(self): # Save Info + Data to .png file
        fig, ax = plt.subplots()
        calibrate_intensity = 0
        if calibrate_intensity:
            intensity = log_converter_function_amps(array(self.data_y))
            plt.ylabel('Calibrated photodiode signal [A]')
            plt.yscale("log")
        else:
            intensity = array(self.data_y)
            plt.ylabel('Uncalibrated photodiode signal [arb.u.]')

        plt.plot(self.data_x,intensity)
        plt.title(self.data_name, wrap=True)
        # plt.legend(loc='best', shadow=True,fontsize =8)
        plt.xlim(self.range_from-self.range_lenght*0.01,self.range_to+self.range_lenght*0.01)
        # plt.ylim(min(min(intensity)),max(max(intensity))*1.1)
        plt.grid(alpha=0.4, linestyle='--')
        plt.xlabel('Wavelength [nm]')
        plt.minorticks_on()
        plt.tight_layout()
        plt.savefig(self.dirpath_project+self.data_name+'.png',dpi=100)


        # self.canvas.draw()
        # self.canvas.fig.savefig(self.dirpath_project+self.data_name+'.png', dpi=100)

    def closeEvent(self, event):
    #close COM port for Spyder IPython kernel to import again rp2daq while pressing Run Script in Spyder
    #(not necessary for double-click in Windows)
        guisettingssaver.GuiSave(self,self.settings)
        try:
            hw_backend.set_input_current(0)
            hw_backend.rp.quit()
        except:
            print("Couldn't use hw_backend. Cable to RP2DAQ probably disconnected before proper program termination.")

# PyQT5 way of doing threading to unfreeze GUI while this class have not yet finished
class calibrate(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        hw_backend.calibrate_low_end_nm(stepper_num=0, conversion=main.conversion_nm, step_speed=90)
        main.textCalibration.setEnabled(True)
        hw_backend.calibrate_low_end_angle(stepper_num=1, conversion=1000, step_speed=500)
        main.buttonAcquire.setEnabled(True)

class acquire(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        #saving current settings in case of app crash during acquisition
        guisettingssaver.GuiSave(main,main.settings)

        main.textCalibration.setEnabled(False)
        main.calibration_nm = float(convertcommas(main.textCalibration.text()))

        main.range_from, main.range_to = float(convertcommas(main.textRange_from.text())), float(convertcommas(main.textRange_to.text()))
        main.range_lenght = abs(main.range_from - main.range_to)

        range_current = arange(float(convertcommas(main.textRange_current_from.text())),
                        float(convertcommas(main.textRange_current_to.text())),
                        float(convertcommas(main.textRange_current_step.text())))
        range_angle = arange(float(convertcommas(main.textRange_angle_from.text())),
                        float(convertcommas(main.textRange_angle_to.text())),
                        float(convertcommas(main.textRange_angle_step.text())))

        main.num_of_measurments_left = len(range_current)*len(range_angle)

        for current_input_current in range_current:
            main.current_input_current = round(current_input_current, 3)
            hw_backend.set_input_current(current_input_current)
            print('input current set to %s mA'%current_input_current)

            """ Temp regulation not functional
            for current_temperature in arange(float(convertcommas(main.textRange_temperature_from.text())),
                            float(convertcommas(main.textRange_temperature_to.text())),
                            float(convertcommas(main.textRange_temperature_step.text()))):
                main.current_temperature = current_temperature
                conversion_K = 1 #not calibrated yet
                hw_backend.set_temperature(int(current_temperature/conversion_K))
                # print('\nsetting temperature to %s mA'%current_temperature)
                # time.sleep(5) #waiting for thermal stabilisation
                print('temperature set to %s K'%current_temperature)
            """
            for current_feedback_angle in range_angle:
                main.current_feedback_angle = round(current_feedback_angle, 3)
                print('setting angle to %s ...'%current_feedback_angle)

                if not hw_backend.move_in_same_direction(stepper_num=1, conversion=1000, low_end=0, next_pos=current_feedback_angle):
                    hw_backend.set_feedback_angle_to(current_feedback_angle-500)
                    hw_backend.set_feedback_angle_to(current_feedback_angle)
                else:
                    hw_backend.set_feedback_angle_to(current_feedback_angle)
                print('angle set to %s'%current_feedback_angle)

                threading.Thread(target=self.acquire_single_spectrum).start()
                result_available.wait() # wait here for the result to be available before continuing
                result_available.clear()
            # print('acquired for %s mA, %s K'%(current_input_current,current_temperature))
            print('acquired for %s mA'%(current_input_current))

        app.beep()
        print("acquisition done :)")
        # hw_backend.set_input_current(0) # turn off input current after acquisition is done
        # hw_backend.set_temperature(293.15) # turn off temp control after acquisition is done

    def acquire_single_spectrum(self):
        print('start acquiring')
        # stop any previous adc acquisition
        hw_backend.rp.adc_stop()

        # move to start position of interval with backlash of monochromator compensation
        # hw_backend.move_stepper_to_nm(stepper_num=0, conversion=main.conversion_nm, step_speed=90,
        #                               low_end=main.calibration_nm, pos_nm= main.range_from - hw_backend.backlash_calibration_const_nm,
        #                               callback=None)
        # hw_backend.backlash(0, hw_backend.backlash_calibration_const_nm, main.conversion_nm)

        # if not hw_backend.move_in_same_direction(stepper_num=0, conversion=main.conversion_nm, low_end=main.calibration_nm, next_pos= main.range_from):
        #     direction_same = False
        #     start = main.range_from - hw_backend.backlash_calibration_const_nm*2 #maybe the const was poorly set
        #     # low_end = main.calibration_nm + 10.3
        # else:
        #     direction_same = True
        #     start = main.range_from
        #     # low_end = main.calibration_nm
        # low_end = main.calibration_nm
        # hw_backend.move_stepper_to_nm(stepper_num=0, conversion=main.conversion_nm, step_speed=90,
        #                               low_end=low_end, pos_nm= start-1.2,
        #                               callback=None)
        # hw_backend.move_stepper_to_nm(stepper_num=0, conversion=main.conversion_nm, step_speed=90,
        #                               low_end=low_end, pos_nm= start,
        #                               callback=None)

        hw_backend.move_stepper_to_nm(stepper_num=0, conversion=main.conversion_nm, step_speed=90,
                                      low_end=main.calibration_nm, pos_nm= main.range_from-1.2,
                                      callback=None)

        hw_backend.move_stepper_to_nm(stepper_num=0, conversion=main.conversion_nm, step_speed=90,
                                      low_end=main.calibration_nm, pos_nm= main.range_from,
                                      callback=None)

        main.time_acq_single_start = time.time() #timer for end of acquisition estimate
        # time.sleep(3) # to check starting nm on analog counter
        # print('At range_from %s' %float(main.textRange_from.text()))
        main.data_time = datetime.now() #time of acquisition
        main.data_x, main.data_y = list(), list()
        main.mt0, main.mp0 = None, None

        if not main.textData_project.text() == '':
            main.data_project = main.textData_project.text()
        else:
            main.data_project = 'Measurement'
            main.textData_project.setText(main.data_project)

        if main.checkBoxSaveDefault:
            main.dirpath_projects = './measured spectra/'
        else:
            # TODO open filemanager in cwd
            # choose directory
            # copy text of chosen directory to textdirpath_projects
            main.dirpath_projects = str(main.textDirpath_txt.text())

        main.dirpath_project = main.dirpath_projects+main.data_project+'/'
        if not os.path.isdir(main.dirpath_project): os.makedirs(main.dirpath_project) #creates dirpath_projects if folder doesn't exists

        main.get_file_name()

        # checking for files with the same name
        file_num = 1
        while os.path.isfile(main.dirpath_project+main.file_name+'_'+str(file_num).zfill(2)+'.txt'): file_num = file_num+1
        main.data_name = main.file_name+'_'+str(file_num).zfill(2)

        main.curve = main.canvas.axes.plot(main.data_x, main.data_y, linewidth=1, label=main.data_name)[-1]

        # initiate adc
        hw_backend.init_adc(cb=adc_callback)
        print('initiating adc...')
        time.sleep(1) # wait to stabilise circuit before adc signal will start to plot
        # add plot to window and resize window
        main.canvas.show()
        # print("canvas showed")
        main.toolbar.show()
        # main.resize(main.sizeHint())
        # move to end position of interval and plot received data

        # if not direction_same:
        #     end = main.range_to + 0.2 #maybe the const was poorly set
        #     # low_end = main.calibration_nm + 0.3
        # else:
        #     end = main.range_to
        #     # low_end = main.calibration_nm
        # hw_backend.move_stepper_to_nm(stepper_num=0, conversion=main.conversion_nm, low_end=low_end,
        #                               step_speed=int(convertcommas(main.textStep_speed.text())),
        #                               pos_nm=end, callback=stepper_callback)

        hw_backend.move_stepper_to_nm(stepper_num=0, conversion=main.conversion_nm, low_end=main.calibration_nm,
                                      step_speed=int(convertcommas(main.textStep_speed.text())),
                                      pos_nm=main.range_to+0.2, callback=stepper_callback)

        main.buttonClear_spectra.setEnabled(True) # allows Clear all spectra button to be clicked
        main.buttonSaveTxt.setEnabled(True)
        main.buttonSavePng.setEnabled(True)


    def stop_thread(self):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()

''' Depreciated interpolation of adc+stepper info which was too unprecise
def adc_callback_interpolated(**kwargs):
    main.mta = (kwargs['start_time_us']+kwargs['end_time_us'])/2 #average of adc timestamps in microseconds
    stepper_info = hw_backend.rp.stepper_status(0) #dictionary of stepper_status
    main.mt1 = stepper_info['timestamp_us']
    main.mp1 = hw_backend.convert_stepper_nanopos_to_nm(stepper_info['nanopos'], main.conversion_nm)
    if not main.mt0:
        adc_nanopos = main.mp1
    else:
        # interpolation of incoming adc position
        adc_nanopos = main.mp0 + (main.mp1-main.mp0)*(main.mta-main.mt0)/(main.mt1-main.mt0)
    if (main.mp0 != main.mp1) and (main.mp0 is not None):
        # append position of stepper in nm to data_x
        main.data_x.append(adc_nanopos)
        main.data_y.append(sum(kwargs['data'])/hw_backend.adc_chunk_size)
    if len(main.data_y)%30 == 0: # update plot by 30 points to help computer draw in real time
        main.update_plot()
    main.mt0, main.mp0 = main.mt1, main.mp1
    # print(f'{len(main.data_y)} ADC samples received so far')
    # if len(main.data_x)%30 == 0: print(int(adc_nanopos))
'''

def adc_callback(rv):
    #rv are return values
    adc_nanopos = (rv.start_sync_value + rv.end_sync_value)/2
    adc_nanopos_nm = hw_backend.convert_stepper_nanopos_to_nm(adc_nanopos, main.conversion_nm, main.calibration_nm)
    # if last data point in data_x was measured then overwrite coresponding data_y with new data_y
    # and if not then append both X and Y data point to their respective lists
    try: data_x_last = main.data_x[-1]
    except IndexError: data_x_last = False

    if  adc_nanopos_nm == data_x_last:
        main.data_y[-1] = (sum(rv.data)/hw_backend.adc_chunk_size)
    # elif adc_nanopos_nm >= main.range_from and adc_nanopos_nm <= main.range_to:
    else:
        main.data_x.append(adc_nanopos_nm) # append position of stepper in nm to data_x
        main.data_y.append(sum(rv.data)/hw_backend.adc_chunk_size)

    if len(main.data_y)%30 == 0: # update plot by 30 points to help computer draw in real time
        main.update_plot()

def stepper_callback(rv):
    main.update_plot() # updates the last 30 or so data points to the graph
    hw_backend.rp.adc_stop()
    if main.checkBoxAutomaticSaveTxt.isChecked(): main.save_last_to_txt()
    if main.checkBoxAutomaticSavePng.isChecked(): main.save_last_to_png()

    time_acq_single_end = time.time()
    main.num_of_measurments_left -= 1
    main.time_left_int = (time_acq_single_end - main.time_acq_single_start)*main.num_of_measurments_left
    main.label_timer.show()
    main.timer.show()

    result_available.set()

def convertcommas(x): #funkce k prepisovani desetinnych carek na tecky
    return x.replace(',','.')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    tempdict = main.__dict__
    result_available = threading.Event()
    app.exec_()
    sys.exit()
