"""
Demonstrates some customized mouse interaction by drawing a crosshair that follows 
the mouse.


"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point


class CrossHairPlot(pg.PlotItem):
    def __init__(self):
        super(CrossHairPlot, self).__init__()
        self.label = pg.LabelItem(justify='right')
        self.chMode = False

    vLine = pg.InfiniteLine(angle=90, movable=False)
    hLine = pg.InfiniteLine(angle=0, movable=False)
    
    def setCrossHairMode(self, setMode=False):
        if setMode:
            self.chMode = True
            self.addItem(self.vLine, ignoreBounds = True)
            self.addItem(self.hLine, ignoreBounds = True)
            proxy = pg.SignalProxy(self.scene().sigMouseMoved,
                                   rateLimit=60,
                                   slot=self.mouseMoved)
            self.scene().sigMouseMoved.connect(self.mouseMoved)
        else:
            self.chMode = False
            try:
                self.removeItem(self.vLine)
                self.removeItem(self.hLine)
                self.scene().sigMouseMoved.disconnect(self.mouseMoved)
                self.label.setText("")
            except: pass

    def mouseMoved(self, evt):
        pos = (evt.x(), evt.y())
        if self.sceneBoundingRect().contains(evt):
            mousePoint = self.vb.mapSceneToView(evt)
            index = int(mousePoint.x())
            if (index > 0):
                self.label.setText(
                    ("<span style='font-size: 12pt'>x=%0.4f, " + \
                     "<span style='font-size: 12pt'>y=%0.4f</span>") % \
                    (mousePoint.x(), mousePoint.y())
                )
                self.vLine.setPos(mousePoint.x())
                self.hLine.setPos(mousePoint.y())
                
    def plot(self, *args, **kwargs):
        super(CrossHairPlot, self).plot(*args, **kwargs)
        if self.chMode:
            self.addItem(self.vLine, ignoreBounds = True)
            self.addItem(self.hLine, ignoreBounds = True)
        


if __name__ == "__main__":  
    #generate layout
    app = QtGui.QApplication([])
    win = pg.GraphicsWindow()
    win.setWindowTitle('pyqtgraph example: crosshair')

    p1 = CrossHairPlot()
    win.addItem(p1.label)
    win.addItem(p1, row=2, col=0)

    #create numpy arrays
    data1 = 10000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)
    data2 = 15000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)

    p1.plot(data1, pen="r")
    p1.plot(data2, pen="g")
    p1.setCrossHairMode(True)
    # p1.setCrossHairMode(False)

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


