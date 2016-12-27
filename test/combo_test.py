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

# Combolist check
win.comboList.addSceneAction.trigger()
win.comboList.activateAction.trigger()
win.comboList.plotButton.click()

win.close()
