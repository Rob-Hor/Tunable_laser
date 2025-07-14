# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 08:50:16 2024

@author: PC
"""

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # self.setParent(parent) optional
        #declaring tight_layout here will take effect upon every redraw of canvas
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)