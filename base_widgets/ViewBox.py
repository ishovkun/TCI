# coding: UTF-8
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
from pyqtgraph.Point import Point
# import re
# from configobj import ConfigObj

class ViewBox(pg.ViewBox):
    '''
    Modification of pg ViewBox class, which emits signal when 
    Alt + mouseclick is performed
    It yields the coordinates of the click
    '''
    sigAltClick = QtCore.Signal(object, object)
    # def __itit__()
    # altAcceptMode = False
    # altClickPos = None
    def mouseClickEvent(self, ev,axis=None):
        if (ev.button()==QtCore.Qt.LeftButton and ev.modifiers()==QtCore.Qt.AltModifier):
            ev.accept()
            # pos = self.mapSceneToView(ev.pos())
            pos = self.mapToView(ev.pos())
            self.sigAltClick.emit(self,pos)
        if ev.button() == QtCore.Qt.RightButton and self.menuEnabled():
            ev.accept()
            self.raiseContextMenu(ev)



if __name__ == '__main__':
    App = QtGui.QApplication(sys.argv)
    w = pg.GraphicsWindow()
    w.show()
    vb= ViewBox()
    p1 = w.addPlot(row=1, col=0,viewBox=vb)
    p1.setAutoVisible(y=True)
    data1 = 10000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)
    data2 = 15000 + 15000 * pg.gaussianFilter(np.random.random(size=10000), 10) + 3000 * np.random.random(size=10000)
    p1.plot(data1, pen="r")
    p1.plot(data2, pen="g")

    #def dostuff(pos,pos1):
    #    print pos1
    #vb.sigAltClick.connect(dostuff)

    App.exec_()
