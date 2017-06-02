import sys, os
import TCI
from TCI.widgets.DataViewer import DataViewer
from PySide import QtGui

App = QtGui.QApplication(sys.argv)
win = DataViewer()
win.show()

test_data_path = TCI.__path__[0] + "/test/test-data/"

filename = [
    test_data_path +
    "1500psi/" + \
    "_Training_Pc=1500 psi Sonic endcaps_Berea Mechanical Testing _2015-04-27_001.clf",
    u'*.clf']
win.load(filename)
win.tree.boxes["Sig1"].setChecked(True)

combo = win.plugins[2]
# Combolist check
combo.addSceneAction.trigger()
combo.activateAction.trigger()
combo.plotButton.click()

# win.close()

App.exec_()
