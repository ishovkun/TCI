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
    u'*.clf'
    ]
win.load(filename)
win.tree.boxes["Sig1"].setChecked(True)

# find mohr circle plugin
mc = win.plugins[1]
mc.addPointAction.trigger()
# print(mc.cursors)
mc.cursors[0].translate(700, 0)
mc.cursors[0].moveToNearest()

# load second dataset
filename = [
    test_data_path +
    "Unconfined/" + \
    "_Training_Unconfined Sonic endcaps_Berea Mechanical Testing _2015-04-28_001.clf",
    u'*.clf']

win.load(filename)

win.tree.boxes["Sig1"].setChecked(True)
mc.addPointAction.trigger()
mc.cursors[0].translate(600, 0)
mc.cursors[0].moveToNearest()
mc.activateAction.trigger()

# # autoscale bug case
### win.tree.boxes["Sig1"].setChecked(False)

# win.close()
App.exec_()
