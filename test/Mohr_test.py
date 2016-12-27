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

# Mohr circle actions
win.mcPlugin.addPointAction.trigger()
win.mcPlugin.addPointAction.trigger()
win.mcPlugin.activateAction.trigger()
win.settingsButton.trigger()
win.tree.boxes["Sig1"].setChecked(True)
win.mcPlugin.activateAction.trigger()
# autoscale bug case
win.tree.boxes["Sig1"].setChecked(False)

win.close()
