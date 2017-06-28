from PySide import QtGui
import sys, os
import TCI
from TCI.widgets.DataViewer import DataViewer

'''
Description:

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
win.setGeometry(2200, 400, 800, 600)
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
sonic_plugin.showFFTPhaseAction.trigger()

# load new data_set (testing stability)
filename = [test_data_path + data_set2_dir + data_set2, u'*.clf']
win.load(filename)

# Assert sonic components are disabled because no sonic data
# for the new dataset
assert not sonic_plugin.sonicViewer.fftWidget.isVisible()
assert not sonic_plugin.exportModuliAction.isEnabled()
assert not sonic_plugin.menu.isEnabled()
assert not sonic_plugin.yAxisMenu.isEnabled()
assert not sonic_plugin.activeWaveMenu.isEnabled()
assert not sonic_plugin.modeMenu.isEnabled()
assert not sonic_plugin.autoScaleAction.isEnabled()
sonic_tab_index = win.tabWidget.indexOf(sonic_plugin.moduliWidget)
assert not win.tabWidget.isTabEnabled(sonic_tab_index)


# now load new sonic data
sonic_dir = test_data_path + data_set2_sonic_dir
files = os.listdir(sonic_dir)
for i in range(len(files)):
    files[i] = os.path.join(sonic_dir, files[i])

sonic_plugin.loadData(files)
sonic_plugin.bindData()
win.slider.setInterval([0.1, 0.9])

# now activate old dataset
data_set1 = "_Training_Pc=1500 psi Sonic endcaps_Berea Mechanical Testing _2015-04-27_001"
win.setCurrentDataSet(data_set1)
win.slider.setInterval([0.2, 0.3])
data_set2 = "_Training_Hydrostatic with Sonic endcaps_Berea Mechanical Testing _2015-04-24_001"
win.setCurrentDataSet(data_set2)
win.slider.setInterval([0.1, 0.9])
win.setCurrentDataSet(data_set1)
win.slider.setInterval([0.5, 0.7])

sonic_plugin.invertYAction.trigger()

# test autoscale
sonic_plugin.sonicViewer.plots['P'].setXRange(0, 200)
# sonic_plugin.autoScaleAction.trigger()

# Fourrier analysis
sonic_plugin.waveFormAction.trigger()
sonic_plugin.waveFormAction.setChecked(True)
sonic_plugin.showFFTMagnitudeAction.trigger()
sonic_plugin.contourAction.trigger()
sonic_plugin.contourAction.setChecked(True)
sonic_plugin.showFFTPhaseAction.trigger()
sonic_plugin.sonicViewer.fftWidget.close()

# win.close()
App.exec_()
