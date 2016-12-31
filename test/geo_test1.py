from PySide import QtGui
import sys
from TCI.widgets.DataViewer import DataViewer

App = QtGui.QApplication(sys.argv)
win = DataViewer()
# win.showMaximized()
win.show()
# win.showFullScreen()

filename = ["/home/ishovkun/Dropbox/Experiments/TO_BE_ANALYZED/1500psi/" + \
    "_Training_Pc=1500 psi Sonic endcaps_Berea Mechanical Testing _2015-04-27_001.clf",
    u'*.clf']
win.load(filename)
win.tree.boxes["Sig1"].setChecked(True)
win.plt.setCrossHairMode(True)
win.plt.setCrossHairMode(False)
win.settings.show()
win.close()
App.exec_()
