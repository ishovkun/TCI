from PySide import QtGui
import sys, os
from TCI import dataviewer

App = QtGui.QApplication(sys.argv)
win = dataviewer.DataViewer()
win.show()

filename = ["/home/ishovkun/Dropbox/Experiments/TO_BE_ANALYZED/1500psi/" + \
    "_Training_Pc=1500 psi Sonic endcaps_Berea Mechanical Testing _2015-04-27_001.clf",
    u'*.clf']
win.load(filename)
win.tree.boxes["Sig1"].setChecked(True)

# SONIC WIDGET TESTING
# win.loadSonicDataAction.trigger()
directory = "/home/ishovkun/Dropbox/Experiments/TO_BE_ANALYZED/1500psi/1500pc"
files = os.listdir(directory)
for i in range(len(files)):
    files[i] = os.path.join(directory, files[i])

sonic_plugin = win.plugins[-1]
sonic_plugin.loadData(files)
sonic_plugin.addSonicTab()
sonic_plugin.bindData()
sonic_plugin.sonicViewer.plot()
sonic_plugin.createYActions()
sonic_plugin.setYParameters()
sonic_plugin.connectActions()
# for test assert not raises exception for this line
win.slider.setInterval([1, 5])
win.slider.setInterval([0.1, 0.5])

# play with modes
sonic_plugin.waveFormAction.trigger()
sonic_plugin.yAxisActions['Ev'].trigger()
sonic_plugin.contourAction.trigger()
# sonic_plugin.pWaveAction.trigger()
sonic_plugin.syWaveAction.trigger()

# shape arrival picking
sonic_plugin.shapeArrivalsAction.trigger()
sonic_plugin.shapeControlWidget.cancelButton.click()
sonic_plugin.shapeArrivalsAction.trigger()
# sonic_plugin.shapeControlWidget.okButton.click()

# assign some arbitrary arrival times
x = [40, 23, 5]
y = [0, 1000, 2200]
sonic_plugin.sonicViewer.plotWidget.rois['P'].setPoints((
    (x[0], y[0]),
    (x[1], y[1]),
    (x[2], y[2])
))
# finish arrival picking and show arrivals
sonic_plugin.shapeControlWidget.okButton.click()

# load new data_set (testing stability)
filename = [
    "/home/ishovkun/Dropbox/Experiments/" + \
    "TO_BE_ANALYZED/Hydrostatic w sonic/" + \
    "_Training_Hydrostatic with Sonic endcaps_Berea Mechanical Testing _2015-04-24_001.clf",
    u'*.clf']
win.load(filename)

# now load new sonic data
directory = "/home/ishovkun/Dropbox/Experiments/" + \
            "TO_BE_ANALYZED/Hydrostatic w sonic/"
files = os.listdir(directory)
for i in range(len(files)):
    files[i] = os.path.join(directory, files[i])
# print(win.plugins[-1])
sonic_plugin.loadData(files)
sonic_plugin.bindData()
win.slider.setInterval([0.1, 0.9])

# now activate old dataset
data_set = "_Training_Pc=1500 psi Sonic endcaps_Berea Mechanical Testing _2015-04-27_001"
win.setCurrentDataSet(data_set)
data_set = "_Training_Hydrostatic with Sonic endcaps_Berea Mechanical Testing _2015-04-24_001"
win.setCurrentDataSet(data_set)

win.close()
