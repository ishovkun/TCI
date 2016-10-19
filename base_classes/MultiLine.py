import sys
import pyqtgraph as pg
import numpy as np
from PySide import QtCore, QtGui

class MultiLine(pg.QtGui.QGraphicsPathItem):
    def __init__(self, x, y):
        """x and y are 2D arrays of shape (Nplots, Nsamples)"""
        connect = np.ones(x.shape, dtype=bool)
        connect[:,-1] = 0 # don't draw the segment between each trace
        self.path = pg.arrayToQPath(x.flatten(), y.flatten(), connect.flatten())
        pg.QtGui.QGraphicsPathItem.__init__(self, self.path)
        self.setPen(pg.mkPen('b',width=1))
    def shape(self): # override because QGraphicsPathItem.shape is too expensive.
        return pg.QtGui.QGraphicsItem.shape(self)
    def boundingRect(self):
        return self.path.boundingRect()

if __name__ == '__main__':
    
    App = QtGui.QApplication(sys.argv)
    x = np.array([[1,2,3],[4,5,6]])
    y = np.array([[1,1,1],[2,2,2]])
    # a = MultiLine(x,y)

    # y = np.random.normal(size=(120,20000), scale=0.2) + np.arange(120)[:,np.newaxis]
    # x = np.empty((120,20000))
    # x[:] = np.arange(20000)[np.newaxis,:]
    view = pg.GraphicsLayoutWidget()
    view.show()
    w1 = view.addPlot()
    now = pg.ptime.time()
    lines = MultiLine(x, y)
    w1.addItem(lines)
    print ("Plot time: %0.2f sec" % (pg.ptime.time()-now))
    # a.show()
    # App._exec()
    QtGui.QApplication.instance().exec_()
    # print a.__dict__
