# coding: UTF-8
import sys,os
import pyqtgraph as pg
import pickle
from PySide import QtGui, QtCore
from copy import copy
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.parametertree import types as pTypes
from pyqtgraph.Point import Point
import numpy as np

# custom modules
from TCI.base_classes.MultiLine import MultiLine
from TCI.lib.functions import *
from TCI.styles.Gradients import Gradients
from TCI.styles.setup_plot import setup_plot
from TCI.base_widgets.ViewBox import ViewBox
from TCI.base_widgets.TableWidget import TableWidget
from TCI.base_widgets.TriplePlotWidget import TriplePlotWidget
from TCI.base_widgets.GradientEditorWidget import GradientEditorWidget
from TCI.lib.logger import logger

X_LABEL = 'Oscilloscope time (μs)'
fXAxisName = 'Frequency (MHz)'
phXAxisName = 'Phase (deg)'
N_COLORS = 100

Parameters = [
    {'name': 'Show', 'type': 'bool', 'value': True, 'tip': "Press to plot wave"},
     {'name': 'Arrival times', 'type': 'group', 'children': [
            {'name': 'Mpoint', 'type': 'float', 'value': 10},
            {'name': 'BTA', 'type': 'int', 'value': 200},
            {'name': 'ATA', 'type': 'int', 'value': 5},
            {'name': 'DTA', 'type': 'int', 'value': 200},
        ]},
    ]
WaveTypes = ['P','Sx','Sy']
LabelStyle = {'color': '#000000', 'font-size': '14pt','font':'Times'}

ARRIVALS_PEN = pg.mkPen(color=(72, 209, 204), width=2)

class SonicViewer(QtGui.QWidget):
    '''
    Has 3 plots stored in dict plots={'P':,'Sx':,'Sy':}
    has 3 modifuing parameter trees to operate data:
    Shift - shift the data along x axis
    Amplify
    '''
    # mode = 'Contours'
    mode = 'WaveForms'
    autoShift = {'P':True,'Sx':True,'Sy':True} # flag to match 0 and transmission time
    arrivalsPicked = False
    updateQTable = True # don't need
    skipPlottingFAmpFlag = False
    skipPlottingFPhaseFlag = False
    enabled = True

    plot_arrival_times_flag = False

    def __init__(self, parent=None, controller=None):
        super(SonicViewer, self).__init__()
        self.parent = parent
        self.controller = controller

        self.setupGUI()
        # self.fWidget = TriplePlotWidget()
        # self.phWidget = TriplePlotWidget()
        # self.bWidget = BindingWidget(parents=[parent, self])
        # self.isWidget = InterpretationSettingsWidget()
        self.data = {'P':{}, 'Sx':{}, 'Sy':{}}
        # self.connectPlotButtons()
        self.gradEditor = GradientEditorWidget()
        self.gradEditor.waveGradientWidget.restoreState(Gradients['hot'])
        self.gradEditor.fourierGradientWidget.restoreState(Gradients['hot'])
        self.gradEditor.phaseGradientWidget.restoreState(Gradients['hot'])
        # self.fgw.restoreState(Gradients['hot'])
        # self.pgw.restoreState(Gradients['hot'])
        # self.allParameters = []
        # self.yAxis = 'Track #'
        self.y = {}
        # self.aTimes = {}
        # Connect everything
        # self.showArrivalsButton.triggered.connect(self.parent.plotSonicData)
        # self.pickArrivalsButton.triggered.connect(self.pickAllArrivals)
        # self.invertYButton.triggered.connect(self.parent.plotSonicData)
        # self.autoScaleButton.triggered.connect(self.autoScalePlots)
        # self.editGradientsButton.triggered.connect(self.gEdit.show)
        # self.gEdit.okButton.pressed.connect(self.parent.plotSonicData)
        # self.showTableButton.triggered.connect(self.showTable)
        # self.showForrierMagnitudeButton.triggered.connect(self.showFourrier)
        # self.showForrierPhasesButton.triggered.connect(self.showPhases)
        # # self.showArrivalsButton.triggered.connect(self.plot)
        # self.waveFormButton.triggered.connect(lambda: self.setMode('WaveForms'))
        # self.contourButton.triggered.connect(lambda: self.setMode('Contours'))
        # self.moduliButton.triggered.connect(self.isWidget.show)
        # self.isWidget.okButton.pressed.connect(self.runBindingWidget)
        # self.filteringButton.triggered.connect(self.parent.plotSonicData)
        # self.fWidget.sigRegionChanged.connect(self.plotFilteredData)
        # # self.moduliButton.triggered.connect(self.bWidget.run)
        # for wave in WaveTypes:
        #   self.params[wave].param('Arrival times').param('Mpoint').sigValueChanged.connect(self.recomputeArrivals)
        #   self.params[wave].param('Arrival times').param('BTA').sigValueChanged.connect(self.recomputeArrivals)
        #   self.params[wave].param('Arrival times').param('ATA').sigValueChanged.connect(self.recomputeArrivals)
        #   self.params[wave].param('Arrival times').param('DTA').sigValueChanged.connect(self.recomputeArrivals)
        #   self.plots[wave].vb.sigAltClick.connect(self.handPick)

    def setEnabled(self, state=True):
        '''
        When disabled this widget doesn't do anything
        (plotting)
        '''
        self.enabled = state

    def handPick(self,sender,pos):
        if not self.handPickArrivalsButton.isChecked():
            return
        else:
            # first find sender
            for wave in self.getActivePlots():
                if self.plots[wave].vb == sender:
                    break
            # now wave is the type sent the signal
            # find closest sonic track to the y position
            closest = abs(self.y[wave] - pos.y()).argmin()
            self.aTimes[wave][closest] = pos.x()
            self.parent.plotSonicData()

    def plotFilteredData(self):
        self.skipPlottingFAmpFlag = True
        self.parent.plotSonicData()

    def runBindingWidget(self):
        testconf = self.isWidget.testconf
        capsconf = self.isWidget.capsconf
        if testconf == None: return 0
        dens = self.isWidget.dens
        length = self.isWidget.length
        atime = self.isWidget.atime
        self.bWidget.setConfig(testconf, capsconf, dens, length, atime)
        self.bWidget.run()

    def setRawData(self, data):
        '''
        data is a dictionary with keys: P,Sx,Sy
        '''
        for wave in WaveTypes:
            self.data[wave] = data[wave]
        self.createTable()
        # self.getFourrierTransforms()
        self.arrivalsPicked = False

    def setSonicTable(self, table, y=None):
        '''
        set already processed sonic data
        '''
        self.table = table
        if y is None:
            for wave in WaveTypes:
                self.y[wave] = np.arange(self.table[wave].shape[1])
        else:
            self.y = y

    def setIndices(self, ind, geo_ind=None):
        '''
        ind - indices for specific wave tracks
        geo_indices - for geomechanical dataset
        also
        '''
        self.indices = ind
        self.geo_indices = geo_ind

    def hasData(self):
        '''
        check if the viewer has data to work with
        '''
        for wave in WaveTypes:
            if len(self.data[wave])>0: return True
        return False

    def createTable(self):
        '''
        store all data in one 3D np-array
        1st dimension - time or amplitude
        2nd dimension - number of file
        3rd dimension - datapoints
        '''
        if not self.hasData(): return 0 # if no data pass
        logger.info('Building sonic matrix')
        ### add some function that checks for constant dt
        # if dt is not uniform, interpolate data and add some points
        self.table = {}
        for wave in WaveTypes:
            self.table[wave] = get_table(self.data[wave])
            self.y[wave] = np.arange(self.table[wave].shape[1])

    def showFourrier(self):
        self.fWidget.show()
        self.fWidget.activateWindow()
        self.parent.plotSonicData()

    def showPhases(self):
        self.phWidget.show()
        self.phWidget.activateWindow()
        self.parent.plotSonicData()

    def getFourrierTransforms(self):
        if not self.hasData(): return 0 # if no data pass
        logger.info('Building Fourrier matrix')
        self.fft = {} # power
        self.fftamp = {} # power
        self.fftph = {} # phase
        for wave in WaveTypes:
            x = self.table[wave][0,:,:]
            y = self.table[wave][1,:,:]
            N = y.shape[1]
            h = x[0,1] - x[0,0]
            # yf = np.fft.fft(y).real[:,:N/2]
            ft = np.fft.fft(y)
            fft = ft[:, :N/2]
            fft = np.fft.fft(y)[:, :N/2]
            yf = np.absolute(fft)
            yp = np.arctan2(fft.imag,fft.real)
            xf0 = np.fft.fftfreq(N,h)
            xf = xf0[:N/2]
            xf = np.tile(xf,y.shape[0])
            xf0 = np.tile(xf0,y.shape[0])
            xf = xf.reshape(yf.shape[0],yf.shape[1])
            xf0 = xf0.reshape(ft.shape[0],ft.shape[1])
            self.fft[wave] = np.array((xf0,ft))
            self.fftamp[wave] = np.array((xf,yf))
            self.fftph[wave] = np.array((xf,yp))

    def connectPlotButtons(self):
        for wave in WaveTypes:
            self.params[wave].param('Show').sigValueChanged.connect(self.changeLayout)

    def showHidePlots(self):
        logger.info('changing layout')
        for wave in WaveTypes:
            try:
                # self.sublayout.removeItem(self.plots[wave])
                self.plotWidget.sublayout.removeItem(self.plots[wave])
                # self.fWidget.sublayout.removeItem(self.fWidget.plots[wave])
            except:
                pass

        for wave in self.getActivePlots():
            if wave:
                self.plotWidget.sublayout.addItem(self.plots[wave])
                # self.fWidget.sublayout.addItem(self.fWidget.plots[wave])
                # self.sublayout.nextRow()
                # self.fWidget.sublayout.nextRow()

        self.plot()

    def autoScalePlots(self):
        if self.autoScaleButton.isChecked():
            for wave in self.getActivePlots():
                self.plots[wave].enableAutoRange()
                self.fWidget.plots[wave].enableAutoRange()
                self.phWidget.plots[wave].enableAutoRange()
        else:
            for wave in self.getActivePlots():
                self.plots[wave].disableAutoRange()
                self.fWidget.plots[wave].disableAutoRange()
                self.phWidget.plots[wave].disableAutoRange()

    def getActivePlots(self):
        if self.controller is None: return WaveTypes
        else: return self.controller.activeWaves()

    def pickAllArrivals(self) :
        pBar = QtGui.QProgressDialog(None,QtCore.Qt.WindowStaysOnTopHint)
        pBar.setWindowTitle("Picking first arrivals")
        pBar.setAutoClose(True)
        pBar.show()
        pBar.activateWindow()
        progress = 0
        pBar.setValue(progress)
        for wave in WaveTypes:
            self.pickArrivals(wave)
            progress += 33
            pBar.setValue(progress)
        pBar.setValue(100)
        self.arrivalsPicked = True
        self.showArrivalsButton.setDisabled(False)
        self.moduliButton.setDisabled(False)
        self.handPickArrivalsButton.setDisabled(False)
        self.showArrivalsButton.trigger()

    def getInverseFFT(self):
        ifft = {}
        interval = self.fWidget.interval()
        for wave in WaveTypes:
            x = self.table[wave][0,:,:]
            xf = self.fft[wave][0,:,:]
            yf = copy(self.fft[wave][1,:,:])
            yf[abs(xf)<min(interval)] = 0
            yf[abs(xf)>max(interval)] = 0
            ift = np.fft.ifft(yf)
            ifft[wave] = np.array((x,ift.real))
        return ifft

    def getYArray(self, wave):
        '''
        get y values that are plotted
        '''
        if self.controller is None: y = None
        else:
            ylabel = self.controller.yLabel()
            if ylabel == "Track #":
                y = self.indices[wave]
            else:
                y = self.getFullYArray(wave)[self.indices[wave]]

            return y

    def getFullYArray(self, wave):
        '''
        get y values that are plotted
        something's wrong
        '''
        if self.controller is None: y = None
        else:
            ylabel = self.controller.yLabel()
            if ylabel == "Track #":
                data = self.table[wave]
                y = np.r_[0: data.shape[1]]
            else:
                y = self.parent.findData(ylabel)[self.controller.geo_indices[wave]]
            return y

    def plot(self):
        if not self.enabled: return 0
        for k, wave in enumerate(self.getActivePlots()):
            # prepare plot
            plot = self.plots[wave]
            plot.clear();
            # labels
            ylabel = self.controller.yLabel()
            plot.getAxis('left').setLabel(ylabel, **LabelStyle)
            plot.getAxis('bottom').setLabel(X_LABEL, **LabelStyle)

            # auto scaling
            if self.controller.autoScaleAction.isChecked():
                plot.enableAutoRange(enable=True)
            else:
                plot.disableAutoRange()

            # y axis invert
            if self.controller.invertYAction.isChecked():
                self.plots[wave].invertY(True)
            else: self.plots[wave].invertY(False)

            # y array of geomechanical data
            ind = self.indices[wave]
            y = self.getYArray(wave)

            data = self.table[wave][:, ind,:]
            if data.shape[1] == 0: continue  # skip empty plot

            if self.mode == 'WaveForms':
                self.plotWaveForms(data, self.plots[wave], y)
            elif self.mode == 'Contours':
                if k == 0: # get only one color lookup table
                    gradient_widget = self.gradEditor.sgw
                    lut = gradient_widget.getLookupTable(N_COLORS, alpha=None)

                self.plotContours(data, self.plots[wave], y, lut)

            # plot arrival times
            if (self.plot_arrival_times_flag and
                wave in self.arrival_times.keys()):
                x = self.arrival_times[wave][self.indices[wave]]
                self.plots[wave].plot(x, y, pen=ARRIVALS_PEN)


    def plotWaveForms(self, data, plot_widget, y_array, amplify=None):
        '''
        input:
        data - np.array(2, n_tracks, track_length)
        plot_widget - pyqtgraph.plotItem that hold the image
        y_array - array of geomechanical data
        amplify - float, amplification coefficient (y-stretch of wave forms)
        '''
        # compute amplification
        if amplify is None:
            amplify = np.abs(np.diff(y_array)).max()/data[1, :, :].max()

        # generate array to plot
        n_lines = data.shape[1]
        y = amplify*data[1,:,:] + y_array.reshape(n_lines, 1)

        # convert array to a graphical path
        graphic_path = MultiLine(data[0, :, :], y)
        try: plot_widget.addItem(graphic_path)
        except: pass

    def plotContours(self, data, plot_widget, y_array, lut=None):
        '''
        input:
        data - np.array(2, n_tracks, track_length)
        plot_widget - pyqtgraph.plotItem that hold the image
        y_array - array of geomechanical data
        lut - lookup table for colors
        '''
        image = pg.ImageItem()
        image.setImage(data[1, :, :].T)
        plot_widget.addItem(image)

        # scale image
        x = data[0, 0, :]
        shiftX0 = x[0]
        scaleX = (x[-1] - x[0])/x.shape[0]
        ymax = y_array.max()
        ymin = y_array.min()
        shiftY0 = ymin
        scaleY = float(ymax - ymin)/y_array.shape[0]

        image.translate(shiftX0, shiftY0)
        image.scale(scaleX, scaleY)

        # set Colors
        if lut is not None:
            image.setLookupTable(lut, update=True)

    def setArrivalTimes(self, arrival_times):
        '''
        arrival_times is a dict:[wave] = np.array(arrival_times)
        '''
        self.arrival_times = arrival_times


    def setYAxisParameters(self,parameters):
        # we use setLimits because of weird implementation
        # in pyqtgraph
        self.allParameters = parameters
        self.yAxisMenu.clear()
        self.yAxisButtons = {}
        self.yAxisButtons['Track #'] = QtGui.QAction('Track #',self,checkable=True)
        self.yAxisButtons['Track #'].setActionGroup(self.yAxisGroup)
        self.yAxisMenu.addAction(self.yAxisButtons['Track #'])
        for p in parameters:
            if self.mode == 'Contours' and p!='Time': continue
            self.yAxisButtons[p] = QtGui.QAction(p,self,checkable=True)
            self.yAxisButtons[p].setActionGroup(self.yAxisGroup)
            self.yAxisMenu.addAction(self.yAxisButtons[p])
            pass
        try:
            logger.info('Setting y axis to: Time')
            self.yAxisButtons['Time'].setChecked(True)
            self.yAxis = 'Time'
        except: logger.warning('setting was not successful')

    def setMode(self, mode):
        '''
        takes string arguments: WaveForms and Contours
        '''
        self.mode = mode
        if mode == 'WaveForms':
            logger.info('Setting mode to Wave Forms')
            # self.modeMenu.setDefaultAction(self.waveFormButton)
        elif mode == 'Contours':
            logger.info('Setting mode to Contours')
            # self.modeMenu.setDefaultAction(self.contourButton)
        else:
            raise ValueError("This mode is not available: %s"%(mode))

    def setupGUI(self):
        self.setWindowTitle("Sonic Viewer")

        # setup layout
        self.layout = QtGui.QVBoxLayout()
        # pg.setConfigOption('foreground',(0,0,0))
        pg.setConfigOption('background', (255,255,255))
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # splitter gonna contain plot widget and side widgets if necessary
        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        # self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        self.plotWidget = TriplePlotWidget()
        self.plots = self.plotWidget.plots
        self.splitter.addWidget(self.plotWidget)

    def setupArrivalsSettingsWidgets(self):
        pass

    def pickArrivals(self,wave):
        logger.info('Computing arrival times for %s wave'%(wave))
        win = [0,0,0]
        mpoint = self.params[wave].param('Arrival times').param('Mpoint').value()
        win[0] = self.params[wave].param('Arrival times').param('BTA').value()
        win[1] = self.params[wave].param('Arrival times').param('ATA').value()
        win[2] = self.params[wave].param('Arrival times').param('DTA').value()
        x = self.table[wave][0,:,:]
        y = self.table[wave][1,:,:]
        h = x[0,1] - x[0,0]
        r = multi_window(y,win)
        rx = np.arange(r.shape[1])*h + x[0,win[0]]
        mind = abs(rx-mpoint).argmin() #index of middle point
        sInd = r[:,:mind].argmax(axis=1) # sender indices
        sTimes = rx[sInd] # sender times
        rInd = r[:,mind:].argmax(axis=1) # receiver indices
        rTimes = rx[mind+rInd]
        self.aTimes[wave] = rTimes - sTimes
        # shift initial data so
        if self.autoShift[wave]:
            shift = np.mean(sTimes)
            self.table[wave][0,:,:] -= shift
            self.autoShift[wave] = False

    def editArrivals(self):
        data = self.QTable.getValues()
        indices = self.parent.trsIndices
        if self.yAxis == 'Track #':
            for wave in WaveTypes:
                indices[wave] = np.arange(len(self.parent.sTimes[wave]))
            pass
        self.aTimes['P'][indices['P']] = data[:,3]
        self.aTimes['Sx'][indices['Sx']] = data[:,4]
        self.aTimes['Sy'][indices['Sy']] = data[:,5]
        self.updateQTable = False
        self.parent.plotSonicData()

    def recomputeArrivals(self):
        parent = self.sender().parent().parent().name()
        wave = parent.split()[0]
        self.pickArrivals(wave)
        self.parent.plotSonicData()

    def showTable(self):
        # show = self.showTableButton.isChecked()
        self.QTable.show()
        self.QTable.activateWindow()

    def closeEvent(self,event):
        QtGui.QWidget.closeEvent(self, event)
        # self.fWidget.close()
        # self.phWidget.close()
        # self.QTable.close()
        # self.bWidget.close()
