# coding: UTF-8
from PySide import QtCore, QtGui
import sys
import pyqtgraph as pg
import numpy as np
from ..lib.LabelStyles import *

class Slider(pg.GradientEditorItem):
    def __init__(self, *args, **kargs):
        super(Slider,self).__init__(*args,**kargs)
    def tickClicked(self,tick,ev):
        pass

class Axis(pg.AxisItem):
    def __init__(self, *args, **kargs):
        super(Axis,self).__init__(*args,**kargs)

class SliderWidget(pg.GraphicsLayout):
    sigRangeChanged = QtCore.Signal(object)
    def __init__(self):
        super(SliderWidget,self).__init__(None)
        self.setupGUI()
        self.slider.sigGradientChanged.connect(self.emitRangeChangedSig)

    def emitRangeChangedSig(self):
        self.sigRangeChanged.emit(self)
        self.interval()
        
    def setupGUI(self):
        self.setWindowTitle("Igor")
        pg.setConfigOption('background', (255,255,255))
        pg.setConfigOption('foreground',(0,0,0))
        # self.setGeometry(500, 300, 350, 200)
        self.slider = Slider(orientation='top', allowAdd=False)
        # self.slider = pg.TickSliderItem(orientation='top', allowAdd=False)
        self.addItem(self.slider)
        self.slider.tickSizer = 0
        self.slider.rectSize = 0
        for i in self.slider.ticks:
            self.slider.setTickColor(i, QtGui.QColor(150,150,150))
        self.axis = pg.AxisItem('bottom')
        self.axis = Axis('bottom')
        self.nextRow()
        self.addItem(self.axis)
        # self.slider.setMaxDim(5)
        self.axis.setStyle(tickTextOffset=TickOffset)
        self.axis.tickFont = TickFont

    def setRange(self, min, max):
        self.axis.setRange(min, max)
        
    def axisRange(self):
        return self.axis.range

    def interval(self):
        r = self.axisRange()
        interval = []
        for i in self.slider.ticks:
            interval.append(self.slider.tickValue(i))
        scale = self.axisRange()[1]
        interval = np.array(sorted(interval))*scale
        return interval
    
    def setInterval(self, interval):
        '''
        interval list [min, max]
        min and max are floats >0 and < 1
        '''
        for i, tick in enumerate(self.slider.ticks):
            self.slider.setTickValue(tick, interval[i])

            
if __name__ == '__main__':
    pg.setConfigOption('foreground',(0,0,0))
    pg.setConfigOption('background', (255,255,255))

    App = QtGui.QApplication(sys.argv)
    view = pg.GraphicsView()
    slider = SliderWidget()
    view.setCentralItem(slider)
    view.setGeometry(80, 50, 800, 600)
    view.show()
    App.exec_()

