# coding: UTF-8
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np

class OKCancelWidget(QtGui.QWidget):
    def __init__(self,type='text',label=''):
        super(OKCancelWidget, self).__init__()
        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)
        self.okButton = QtGui.QPushButton('OK')
        self.cancelButton = QtGui.QPushButton('Cancel')
        self.layout.addWidget(self.okButton)
        self.layout.addWidget(self.cancelButton)

if __name__ == '__main__':
    App = QtGui.QApplication(sys.argv)
    w = OKCancelWidget()
    w.show()
    App.exec_()
