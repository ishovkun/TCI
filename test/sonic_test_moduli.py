from PySide import QtGui
import sys, os
import TCI
from TCI.widgets.DataViewer import DataViewer

'''
Description
Read cfl from 1500psi
Read sonic data
Tweak slider
Plot contours
Shape-pick:
    Assign some hard-coded arrival points
    Compute arrivals from shapes
Compute moduli
Plot young's moduli
'''

test_data_path = TCI.__path__[0] + "/test/test-data/"
data_set1 = "_Training_Pc=1500 psi Sonic endcaps_Berea Mechanical Testing _2015-04-27_001.clf"
data_set2 = "_Training_Hydrostatic with Sonic endcaps_Berea Mechanical Testing _2015-04-24_001.clf"
data_set1_dir = "1500psi/"
data_set2_dir = "Hydrostatic w sonic/"
data_set1_sonic_dir = "1500psi/1500pc"
data_set2_sonic_dir = "Hydrostatic w sonic/"

App = QtGui.QApplication(sys.argv)
win = DataViewer()
win.show()

filename = [test_data_path + data_set1_dir + data_set1, u'*.clf']
win.load(filename)
win.tree.boxes["Sig1"].setChecked(True)

# SONIC WIDGET TESTING
# win.loadSonicDataAction.trigger()
sonic_dir = test_data_path + data_set1_sonic_dir
files = os.listdir(sonic_dir)
for i in range(len(files)):
    files[i] = os.path.join(sonic_dir, files[i])

sonic_plugin = win.plugins[-1]
sonic_plugin.loadData(sorted(files))
sonic_plugin.addSonicTab()
sonic_plugin.bindData()
sonic_plugin.sonicViewer.plot()
sonic_plugin.createYActions()
sonic_plugin.setYParameters()
sonic_plugin.connectActions()
win.slider.setInterval([0.1, 0.5])
sonic_plugin.contourAction.trigger()
# sonic_plugin.syWaveAction.trigger()

# shape arrival picking
sonic_plugin.shapeArrivalsAction.trigger()
sonic_plugin.shapeControlWidget.cancelButton.click()
sonic_plugin.shapeArrivalsAction.trigger()
# sonic_plugin.shapeControlWidget.okButton.click()

# assign some arbitrary arrival times
x = [22, 19, 18]
y = [480, 1110, 2240]
sonic_plugin.sonicViewer.plotWidget.rois['P'].setPoints((
    (x[0], y[0]),
    (x[1], y[1]),
    (x[2], y[2])
))
x = [33.5, 30, 29]
y = [450, 1110, 2230]
sonic_plugin.sonicViewer.plotWidget.rois['Sx'].setPoints((
    (x[0], y[0]),
    (x[1], y[1]),
    (x[2], y[2])
))

# sonic_plugin.syWaveAction.trigger()
# sonic_plugin.sxWaveAction.trigger()
x = [33.5, 30, 29]
y = [450, 1110, 2230]
sonic_plugin.sonicViewer.plotWidget.rois['Sy'].setPoints((
    (x[0], y[0]),
    (x[1], y[1]),
    (x[2], y[2])
))

# finish arrival picking and show arrivals
sonic_plugin.shapeControlWidget.okButton.click()
sonic_plugin.moduliAction.trigger()
sonic_plugin.interpretationSettings.okButton.click()

sonic_plugin.moduliWidget.tree.boxes['Young'].setChecked(True)
sonic_plugin.moduliWidget.tree.boxes['Young_x'].setChecked(True)
sonic_plugin.moduliWidget.tree.boxes['Young_y'].setChecked(True)

# Activate sonic tab and move slider
# there is some bug that makes arrival times appear to be zero
win.tabWidget.setCurrentWidget(sonic_plugin.sonicViewer)
win.slider.setInterval([0.1, 0.6])

# sonic_plugin.exportArrivalsAction.trigger()
project_root = TCI.__path__[0]
fname = project_root + "/arrivals.csv"
sonic_plugin.exportArrivals(fname)
os.remove(fname)

fname = project_root + "/moduli.csv"
sonic_plugin.exportModuli(fname)
os.remove(fname)

# load new dataset
filename = [test_data_path + data_set2_dir + data_set2, u'*.clf']
win.load(filename)

# check if moduli widget is plotting anything when disabled
moduli_widget_tab = win.tabWidget.indexOf(sonic_plugin.moduliWidget)
assert not win.tabWidget.isTabEnabled(moduli_widget_tab)

# win.close()
App.exec_()
