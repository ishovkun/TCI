import sys, os
from TCI.widgets.DataViewer import DataViewer
from PySide import QtGui

App = QtGui.QApplication(sys.argv)
win = DataViewer()
win.show()
App.exec_()
