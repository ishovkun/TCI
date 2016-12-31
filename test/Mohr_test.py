from PySide import QtGui
import sys
from TCI import dataviewer

App = QtGui.QApplication(sys.argv)
win = dataviewer.DataViewer()
win.show()

filename = ["/home/ishovkun/Dropbox/Experiments/TO_BE_ANALYZED/1500psi/" + \
    "_Training_Pc=1500 psi Sonic endcaps_Berea Mechanical Testing _2015-04-27_001.clf",
    u'*.clf']
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
    "/home/ishovkun/Dropbox/Experiments/" + \
    "TO_BE_ANALYZED/Unconfined/Unconfined/" + \
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
