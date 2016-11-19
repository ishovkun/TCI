# coding: UTF-8
import sys,os
import pyqtgraph as pg
import numpy as np
from copy import copy
from PySide import QtGui, QtCore
from TCI.lib.Gradients import Gradients
from TCI.lib.setup_plot import setup_plot
from TCI.base_widgets.PlotItem import PlotItem


WAVE_TYPES = ['P','Sx','Sy']
ROI_PEN = pg.mkPen(color=(72, 209, 204), width=3)
ROI_PEN_ACTIVE = pg.mkPen(color=(0, 0, 204), width=3)

class Region(pg.LinearRegionItem):
    '''
    Maybe change colors for the region,
    probablym make it transparent and show boundaries only,
    alson, hovering event colors it. don't need it
    '''
    def init(self,*args,**kwargs):
        super(Region, self).__init__(self,*args,**kwargs)
    def hoverEvent(self, ev):
        pass

class MultiLineROI(pg.PolyLineROI):
    def getPoints(self):
        '''
        returns numpy arrays x, y corresponding to handle coordinates
        '''
        points = self.getState()['points']
        x = []
        y = []
        for point in points:
            x.append(point.x())
            y.append(point.y())
        x = np.array(x)
        y = np.array(y)
        return x, y

class TriplePlotWidget(QtGui.QWidget):
    sigRegionChanged = QtCore.Signal(object)
    sync = True
    def __init__(self):
        super(TriplePlotWidget, self).__init__(None)
        self.regions = {}
        self.rois = {}
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255, 70))
        for wave in WAVE_TYPES:
            # self.regions[wave] = pg.LinearRegionItem()
            self.regions[wave] = Region(brush=brush)
            self.regions[wave].sigRegionChanged.connect(self.moveRegions)
        self.setupROIs()
        self.setupGUI()

    def setupROIs(self):
        self.rois = {}
        for wave in WAVE_TYPES:
            # self.rois[wave] = pg.PolyLineROI([
            self.rois[wave] = MultiLineROI([
                    [0, 0],
                    [1, 1],
            ], closed=False, pen=ROI_PEN)
        # use cool method parentBounds()

    def showROIs(self, roi_names=WAVE_TYPES):
        for wave in roi_names:
            self.plots[wave].addItem(self.rois[wave])
            bounds = self.rois[wave].parentBounds()

    def setupGUI(self):
        pg.setConfigOption('background', (255,255,255))
        pg.setConfigOption('foreground', (0,0,0))
        self.layout = QtGui.QVBoxLayout()
        self.sublayout = pg.GraphicsLayoutWidget()
        self.setLayout(self.layout)
        self.layout.addWidget(self.sublayout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.plots = {}
        for wave in WAVE_TYPES:
            # self.plots[wave] = self.sublayout.addPlot()
            self.plots[wave] = PlotItem()
            self.sublayout.addItem(self.plots[wave])
            # self.sublayout.nextRow()
            setup_plot(self.plots[wave])
        self.plots['P'].setXLink(self.plots['Sx'])
        self.plots['P'].setYLink(self.plots['Sx'])
        self.plots['Sy'].setXLink(self.plots['Sx'])
        self.plots['Sy'].setYLink(self.plots['Sx'])

    def addRegions(self):
        for wave in WAVE_TYPES:
            plt = self.plots[wave]
            region = self.regions[wave]
            region.setZValue(10)
            plt.addItem(self.regions[wave],ignoreBounds=True)

    def moveRegions(self):
        sender = self.sender()
        # Find sender name
        waves = copy(WAVE_TYPES)
        for wave, region in self.regions.items():
            if sender == region:
                waves.remove(wave)
        rangex = sender.getRegion()
        for wave in waves:
            region = self.regions[wave]
            # region.setZValue(10)
            region.sigRegionChanged.disconnect(self.moveRegions)
            self.regions[wave].setRegion(rangex)
            region.sigRegionChanged.connect(self.moveRegions)
        self.sigRegionChanged.emit(self)

    def interval(self):
        region = self.regions['P']
        return region.getRegion()


if __name__ == '__main__':
    App = QtGui.QApplication(sys.argv)
    x = np.arange(10)
    y = {}
    y[0] = x*2 + np.sin(x)
    y[1] = x*3 + np.sin(2*x)
    y[2] = x*3 + np.cos(2*x)

    win = TriplePlotWidget()
    i=0
    win.addRegions()
    for wave in WAVE_TYPES:
        plt = win.plots[wave]
        plt.plot(x, y[i], pen='g')
        plt.enableAutoRange()
        i+=1

    win.showROIs()
    # use cool method parentBounds()
    win.show()
    win.setGeometry(80, 30, 1000, 700)
    App.exec_()
