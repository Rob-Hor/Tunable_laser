# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 16:15:04 2024

@author: PC
"""
# Source: https://stackoverflow.com/questions/23279125/python-pyqt4-functions-to-save-and-restore-ui-widget-values#23398876
# If this script is insufficient try using module pyqtconfig from https://github.com/pythonguis/pyqtconfig

from PyQt5.QtWidgets import (QComboBox, QCheckBox, QLineEdit, QWidget, QRadioButton,
                             QSpinBox, QDoubleSpinBox, QSlider, QListWidget)
from PyQt5.QtCore import QSettings
from inspect import getmembers

def GetHandledTypes():
    return (QComboBox, QLineEdit, QCheckBox, QRadioButton,
            QSpinBox, QDoubleSpinBox, QSlider, QListWidget)

def IsHandledType(widget):
    return any(isinstance(widget, t) for t in GetHandledTypes())

#===================================================================
# save "ui" controls and values to registry "setting"
#===================================================================

def GuiSave(ui : QWidget, settings : QSettings, uiName="uiwidget"):
    namePrefix = f"{uiName}/"
    settings.setValue(namePrefix + "geometry", ui.saveGeometry())

    for name, obj in getmembers(ui):
        if not IsHandledType(obj):
            continue

        name = obj.objectName()
        value = None
        if isinstance(obj, QComboBox):
            index = obj.currentIndex()  # get current index from combobox
            value = obj.itemText(index)  # get the text for current index

        if isinstance(obj, QLineEdit):
            value = obj.text()

        if isinstance(obj, QCheckBox):
            value = obj.isChecked()

        if isinstance(obj, QRadioButton):
            value = obj.isChecked()

        if isinstance(obj, QSpinBox):
            value = obj.value()
            
        if isinstance(obj, QDoubleSpinBox):
            value = obj.value()

        if isinstance(obj, QSlider):
            value = obj.value()

        if isinstance(obj, QListWidget):
            settings.beginWriteArray(name)
            for i in range(obj.count()):
                settings.setArrayIndex(i)
                settings.setValue(namePrefix + name, obj.item(i).text())
            settings.endArray()
        elif value is not None:
            settings.setValue(namePrefix + name, value)

#===================================================================
# restore "ui" controls with values stored in registry "settings"
#===================================================================

def GuiRestore(ui : QWidget, settings : QSettings, uiName="uiwidget"):
    from distutils.util import strtobool

    namePrefix = f"{uiName}/"
    geometryValue = settings.value(namePrefix + "geometry")
    if geometryValue:
        ui.restoreGeometry(geometryValue)

    for name, obj in getmembers(ui):
        if not IsHandledType(obj):
            continue

        name = obj.objectName()
        value = None
        if not isinstance(obj, QListWidget):
            value = settings.value(namePrefix + name)
            if value is None:
                continue

        if isinstance(obj, QComboBox):
            index = obj.findText(value)  # get the corresponding index for specified string in combobox

            if index == -1:  # add to list if not found
                obj.insertItems(0, [value])
                index = obj.findText(value)
                obj.setCurrentIndex(index)
            else:
                obj.setCurrentIndex(index)  # preselect a combobox value by index

        elif isinstance(obj, QLineEdit):
            obj.setText(value)

        elif isinstance(obj, QCheckBox):
            if type(value) == bool: obj.setChecked(value)
            elif type(value) == str: obj.setChecked(strtobool(value))
            else: print("Object %s with value '%s' is not type 'bool' or 'str' but is type %s."
                        %(str(name), str(value), type(value)))
            pass

        elif isinstance(obj, QRadioButton):
            if type(value) == bool: obj.setChecked(value)
            elif type(value) == str: obj.setChecked(strtobool(value))
            else: print("Object %s with value '%s' is not type 'bool' or 'str' but is type %s."
                        %(str(name), str(value), type(value)))
            pass

        elif isinstance(obj, QSlider):
            obj.setValue(int(value))

        elif isinstance(obj, QSpinBox):
            obj.setValue(int(value))
            
        elif isinstance(obj, QDoubleSpinBox):
            obj.setValue(float(value))

        elif isinstance(obj, QListWidget):
            size = settings.beginReadArray(namePrefix + name)
            for i in range(size):
                settings.setArrayIndex(i)
                value = settings.value(namePrefix + name)
                if value is not None:
                    obj.addItem(value)
            settings.endArray()