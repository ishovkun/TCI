# For build
# from pyqtgraphBundleUtils import *
# from pyqtgraph import setConfigOption
# setConfigOption('useOpenGL', False)
###############
import sys, os
# sys.path.append('dataviewer_lib') # comment this line on build and put files from the lib directly to the same folder
import numpy as np
import PySide
import pyqtgraph as pg
from PySide import QtGui, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
# from pyqtgraph.parametertree import types as pTypes
from pyqtgraph.Point import Point
# from TCI.base_widgets.CursorItem import CursorItem
from TCI.widgets.SettingsWidget import SettingsWidget
from TCI.widgets.CParameterTree import CParameterTree
from TCI.widgets.CrossHairPlot import CrossHairPlot
from TCI.gui_settings.setup_plot import setup_plot
from TCI.gui_settings.Colors import DataViewerTreeColors
from TCI.gui_settings.LabelStyles import *
from TCI.base_widgets.Slider import SliderWidget
from TCI.base_classes.InputReader import InputReader

# Plugins
from TCI.plugin_list import get_plugin_list
# from TCI.plugins.ComboList import ComboList
# from TCI.plugins.CalculatorPlot import CalculatorPlot
# from TCI.plugins.MohrCircles import MohrCircles

BadHeaderMessage = '''Couldn't locate the header.
Go to Preferences->Main settings and adjust the header parameters'''


ModifyingParameters = [
    {'name':'Plot vs.','type':'list','values':['x','y']},
    {'name':'Parameter', 'type':'list'},
    # {'name':'Interval', 'type':'list'},
    {'name':'min', 'type':'float', 'value':0.0,'dec':True,'step':1.0},
    {'name':'max', 'type':'float', 'value':1.0,'dec':True,'step':1.0},
    {'name':'Null', 'type':'bool', 'value':False,'tip': "Press to null data"},
    {'name': 'Linear Trend', 'type': 'group', 'children': [
        {'name': 'Show trend', 'type': 'bool', 'value': False, 'tip': "Press to plot trend"},
        {'name':'Trend parameter', 'type':'list'},
        {'name':'Slope', 'type':'float', 'value':0.0,'dec':True},
        {'name':'Intersection', 'type':'float', 'value':0.0,'dec':True}
    ]},
]

TrendPen = pg.mkPen(color=(72, 209, 204), width=3)
MAXNROWS = 1e4  # if data is longer, we slice data

class DataViewer(QtGui.QWidget):
    # to update plots in visible plugins
    sigUpdatingPlot = QtCore.Signal(object)
    # to add GUI entries for plugins
    sigSettingGUI  = QtCore.Signal(object)
    # to enable some data upon loading
    sigConnectParameters = QtCore.Signal(object)
    # to save data for the dataset - carries data set name
    sigSaveDataSet = QtCore.Signal(str)
    # to load data for the stored dataset
    sigLoadDataSet = QtCore.Signal(str)
    # when creating a new dataset
    sigNewDataSet = QtCore.Signal(object)

    def __init__(self):
        super(DataViewer, self).__init__()
        self.settings = SettingsWidget()
        self.iReader = InputReader()
        self.plugins = []   # list to store plugin items
        self.loadPlugins()
        self.setupGUI()
        # self.comboList = ComboList(parent=self)
        # self.calcPlot = CalculatorPlot(parent=self)
        # self.mcPlugin = MohrCircles(parent=self)
        # default plots will be drawn with multiple y and single x
        self.mainAxis = 'x'
        self.sliderParam = self.settings.config()['Main parameters']['slider']
        self.timeParam = self.settings.config()['Main parameters']['time']
        # no legend at first (there is no data)
        self.legend = None
        self.currentDataSetName = None
        self.dataSetButtons = {}  # list of items in the dataset section of the menu bar
        '''
        Note:
        indices = piece of all data indices, corresponding to the
        values interval, contrained by the slider
        THE VIEWER PLOTTS DATA using indices!!!!
        '''
        self.data = None         # dictionary with full current data set
        self.indices = None     # array with indices for the current interval
        self.comments = {}
        self.allComments = {}
        self.allData = {}       # data values for different datasets
        self.allKeys = {}       # keys for different datasets
        self.allIndices = {}    # contains all truncated indices ???
        self.allSampleLengths = {}      # ????
        self.allUnits = {}
        self.settings.okButton.pressed.connect(self.settings.hide)
        self.exitAction.triggered.connect(sys.exit)
        self.settingsButton.triggered.connect(self.settings.show)
        self.loadButton.triggered.connect(self.requestLoad)
        self.crossHairButton.triggered.connect(self.toggleCrossHair)
        self.setStatus('Ready')

    def loadPlugins(self):
        '''
        get plugin list and create instances of plugins
        set dataviewer as parent, and store them
        '''
        plugin_classes = get_plugin_list()
        for plugin_class in plugin_classes:
            self.plugins.append(plugin_class(parent=self))

    def toggleCrossHair(self):
        ch_mode = self.crossHairButton.isChecked()
        self.plt.setCrossHairMode(ch_mode)

    def checkForLastDir(self):
        '''
        tries to open file 'lastdir'
        if it exists, returns the contents,
        else returns none
        '''
        try:
            with open('lastdir','r') as f:
                return f.read()
        except IOError:
            return ''

    def makeLastDir(self,filename):
        '''
        gets directory name from file absolute path
        create file 'lastdir' and writes
        '''
        with open('lastdir','w') as f:
            f.write(os.path.dirname(filename))

    def requestLoad(self):
        '''
        opens file manager, gets filename,
        calls load
        '''
        self.lastdir = self.checkForLastDir()
        # second par - name of file dialog window
        # third parameter - default file name
        # forth parameter - file filter. types separated by ';;'
        filename = QtGui.QFileDialog.getOpenFileName(self, "",
         "%s"%(self.lastdir), "*.clf;;MAT files (*.mat)")
        self.load(filename)

    def findData(self, key):
        assert key in self.keys, "%s not found"%(key)
        i = self.keys.index(key)
        return self.data[:, i]

    def findDatainAllDatasets(self, dataset, key):
        i = self.allKeys[dataset].index(key)
        return self.allData[dataset][:, i]

    def findUnits(self, key):
        i = self.keys.index(key)
        return self.units[i]

    def sliceData(self, nrows):
        """
        slice data so that the number of rows is less than nrows.
        Leave the entries that contain comments
        """
        datasize = self.data.shape[0]
        # rows that will be included in the slice (initially none)
        active_rows = np.zeros(datasize, dtype=bool)
        # we will take every n-th row of all data
        every_n = (datasize // nrows) + 1
        # counter that will be reset when we leave a row in the slice
        counter = 1
        for i in xrange(datasize):
            if self.comments[i] != b'' or counter == every_n:
                active_rows[i] = 1
                counter = 0
            counter += 1

        sliced_data = self.data[active_rows]
        sliced_comments = self.comments[active_rows]

        self.data = sliced_data
        self.comments = sliced_comments

    def load(self, filename):
        '''
        opens file manager, reads data from file,
        calls generateList to put into GUI
        '''
        headerexpr = self.settings.msWidget.getHeaderExpr()
        slengthexpr = self.settings.msWidget.getSampleLengthExpr()
        if filename[0] == '': return

        elif filename[1] == u'*.clf':
            clf_data = self.iReader.read_clf(filename[0])
            # names, units, values, comments = clf_data

        # Handle wrong header
        #     if tup==None:
        #         reply = QtGui.QMessageBox.warning(self,
        #         'Wrong header',
        #         BadHeaderMessage, QtGui.QMessageBox.Ok )
        #         IOError('Cannot read this file.')
        #     data,comments,length = tup

        # If something's wrong
        # else: raise IOError('Cannot read this file format.')

        self.keys = clf_data[0]
        self.units = clf_data[1]
        self.data = clf_data[2]
        self.comments = clf_data[3]

        if self.data.shape[0] > MAXNROWS:
            self.sliceData(MAXNROWS)

        # this should be in read_clf command
        comments = []
        for c in self.comments:
            comments.append(c[0].decode('UTF-8'))
        self.comments = np.array(comments)
        # end

        # this is to remember this name when we wanna save file
        self.makeLastDir(filename[0]) # extract filename from absolute path
        self.filename = os.path.basename(filename[0])

        # # remove extension from name
        dataSetName = os.path.splitext(self.filename)[0]
        self.currentDataSetName = dataSetName
        self.addDataSet(dataSetName)
        self.setCurrentDataSet(dataSetName)

    def addDataSet(self, dataSetName):
        # self.allSampleLengths[self.filename] = length
        # self.allIndices[self.filename] = np.arange(l)
        self.indices = np.arange(self.data.shape[0])
        if dataSetName in self.allData.keys():
            isNew = False
        else:
            isNew = True

        self.allComments[dataSetName] = self.comments
        self.allUnits[dataSetName] = self.units
        self.allKeys[dataSetName] = self.keys
        self.allData[dataSetName] = self.data
        if isNew:       # modify gui dataset entries
            self.addDataSetToGUI(dataSetName)

    def addDataSetToGUI(self, dataSetName):
        '''
        create menu entry for a new data set, set is as current,
        add it to the list of all buttons, connect the menu entry to
        an action
        '''
        print('Modifying GUI: adding data set button')
        dataSetButton = QtGui.QAction(dataSetName, self, checkable=True)
        dataSetButton.setActionGroup(self.dataSetGroup)
        dataSetButton.setChecked(True)
        self.dataSetMenu.addAction(dataSetButton)
        self.dataSetButtons[dataSetName] = dataSetButton
        dataSetButton.triggered.connect(lambda: self.setCurrentDataSet(dataSetName))

        self.sigNewDataSet.emit(self)

    def setCurrentDataSet(self, dataSetName):
        '''
        Store old data in the dictionary.
        Load new data from the dictionary.
        '''
        print('New data set is chosen')
        self.sigSaveDataSet.emit(dataSetName)
        # if we switch to a different data set (if it's not the first),
        # remember cursors for the old one
        if self.currentDataSetName:
            print('Saving old data')
            self.allIndices[self.currentDataSetName] = self.indices
            # self.allCursors[self.currentDataSetName] = self.cursors
            self.allComments[self.currentDataSetName] = self.comments

        print('Setting new data')
        # set current data dictionaries to new values
        self.currentDataSetName = dataSetName
        self.data = self.allData[dataSetName]
        self.units = self.allUnits[dataSetName]
        # self.sampleLength = self.allSampleLengths[dataSetName]
        self.indices = self.allIndices[dataSetName]
        self.dataSetMenu.setDefaultAction(self.dataSetButtons[dataSetName])

        self.sigLoadDataSet.emit(dataSetName)

        self.comments = self.allComments[dataSetName]

        # fill the data tree widget with data keys
        self.setTreeParameters()
        self.connectParameters()
        self.updatePlot()

    def setTreeParameters(self):
        print( 'Modifying GUI: adding parameters to plot')
        # Modify parameter tree (i.r. plotting trend etc.)
        self.modparamlist = ModifyingParameters
        self.modparamlist[1]['values'] = self.keys      # Parameter
        # self.modparamlist[2]['values'] = self.data.keys() # Interval
        self.modparamlist[5]['children'][1]['values'] = self.keys # Trend parameter
        # create parameter class instances()
        self.modparams = Parameter.create(name='Options',
                                          type='group',
                                          children=self.modparamlist)
        # modify main tree
        self.tree.clear()
        self.tree.addItems(self.keys, DataViewerTreeColors)
        self.modtree.setParameters(self.modparams, showTop=True)
        self.assignAttributes() # to get shorter names


    def save(self):
        self.lastdir = self.checkForLastDir()
        # second par - name of file dialog window
        # third parameter - default file name
        # forth parameter - file filter. types separated by ';;'
        filename = pg.QtGui.QFileDialog.getSaveFileName(self,
            "Save to MATLAB format", "%s%s"%(self.lastdir,self.currentDataSetName), "MAT files (*.mat)")
        if filename[0] == '': return
        pymat.save(filename[0],self.data)

    def connectParameters(self):
        '''
        Makes new connection of list entries with plot after
        loading a new dataset.
        'Parameter' with name Time is default if it's in the list
        Default Interval variable is set to Time
        '''
        # set default values for modifying parameters
        self.modparams.param('Parameter').setValue(self.timeParam)
        # connect signals to updating functions
        self.tree.sigStateChanged.connect(self.updatePlot)
        # self.tree.sigStateChanged.connect(self.bindCursors)
        self.slider.sigRangeChanged.connect(self.truncate)
        # self.modparams.param('Interval').sigValueChanged.connect(self.updatePlot)
        self.modparams.param('min').sigValueChanged.connect(self.setTicks)
        self.modparams.param('max').sigValueChanged.connect(self.setTicks)
        self.modparams.param('Parameter').sigValueChanged.connect(self.updatePlot)
        self.modparams.param('Plot vs.').sigValueChanged.connect(self.setMainAxis)

        # connection with trend computations
        self.tree.sigStateChanged.connect(self.setTrendParameter)
        self.modparams.param('Parameter').sigValueChanged.connect(self.checkTrendUpdates)
        self.modparams.param('Plot vs.').sigValueChanged.connect(self.setTrendParameter)
        self.computeTrendFlag.sigValueChanged.connect(self.checkTrendUpdates)
        self.trendParameter.sigValueChanged.connect(self.setTrendParameter)
        # connect Null parameter
        self.nullFlag.sigValueChanged.connect(self.updatePlot)

        # send signals to plugins
        self.sigConnectParameters.emit(self)

    def checkTrendUpdates(self):
        if self.computeTrendFlag.value():
            self.computeTrend()
        self.updatePlot()

    def setTrendParameter(self):
        entries = self.activeEntries()
        for i in entries: pass
        if entries != []: self.trendParameter.setValue(i)
        self.checkTrendUpdates()

    def truncate(self):
        interval = self.slider.interval()
        arr = self.findData(self.sliderParam)
        self.indices = (arr>=interval[0]) & (arr <= interval[1])
        self.checkTrendUpdates()
        self.updatePlot()

    def setMainAxis(self):
        self.mainAxis = self.modparams.param('Plot vs.').value()
        self.updatePlot()

    def updateLimits(self):
        '''
        Update limits shown in options based on old slider state
        '''
        interval = self.slider.interval()
        try:
            self.modparams.param('min').sigValueChanged.disconnect(self.setTicks)
            self.modparams.param('max').sigValueChanged.disconnect(self.setTicks)
        except RuntimeError:
            pass
        self.modparams.param('min').setValue(interval[0])
        self.modparams.param('max').setValue(interval[1])
        self.modparams.param('min').sigValueChanged.connect(self.setTicks)
        self.modparams.param('max').sigValueChanged.connect(self.setTicks)

    def setTicks(self):
        '''
        sets ticks to state coressponding to  Interval min/max
        values, when they are manually changed
        '''
        # scale = self.data[self.sliderParam].max()
        scale = self.findData(self.sliderParam).max()
        values = [float(self.modparams.param('min').value())/scale,
                  float(self.modparams.param('max').value())/scale
                 ]
        # print(values)
        self.slider.setInterval(values)
        self.updatePlot()

    def updatePlot(self):
        '''
        updates plot
        '''
        self.setAxisScale()
        self.updateLimits()
        self.sigUpdatingPlot.emit(self)
        ### Ready to update
        # self.setAutoFillBackground(True)
        self.clearPlotWindow()
        self.plt.showGrid(x=True, y=True)
        if self.mainAxis == 'x':
            self.plotVersusX()
        if self.mainAxis == 'y':
            self.plotVersusY()
        if self.computeTrendFlag.value():
            self.plotTrend()

        # send signal to plugins
        self.sigUpdatingPlot.emit(self)

    def plotVersusX(self):
        '''
        plot when we have sevaral y's versus of x.
        '''
        # Get variables to plot
        data = self.data
        plotlist = self.activeEntries()
        xlabel = self.modparams.param('Parameter').value()
        null = self.nullFlag.value()
        for i in range(len(plotlist)):
            ylabel = plotlist[i]
            color = self.tree.colors[ylabel].getColor()
            linestyle = pg.mkPen(color=color, width=3)
            yunits = self.findUnits(ylabel)
            xdata = self.findData(xlabel)[self.indices]
            ydata = self.findData(ylabel)[self.indices]
            if null: ydata -= ydata[0]
            self.plt.plot(xdata, ydata,
                pen=linestyle, name=plotlist[i])
            ylabel += " " + yunits
            self.plt.setLabel('left', ylabel, **AxisLabelStyle)

        xunits = self.findUnits(xlabel)
        xlabel += " " + xunits
        # if len(plotlist)>0: self.bindCursors(data[xlabel],data[ylabel])
        self.plt.setLabel('bottom', xlabel, **AxisLabelStyle)

    def plotVersusY(self):
        '''
        plot when we have sevaral y's versus of x.
        '''
        # Get variables to plot
        data = self.data
        plotlist = self.activeEntries()
        ylabel = self.modparams.param('Parameter').value()
        yunits = self.findUnits(ylabel)
        null = self.nullFlag.value()
        for i in range(len(plotlist)):
            xlabel = plotlist[i]
            color = self.tree.colors[xlabel].getColor()
            linestyle = pg.mkPen(color=color, width=3)
            xdata = self.findData(xlabel)[self.indices]
            ydata = self.findData(ylabel)[self.indices]
            if null: xdata -= xdata[0]
            xunits = self.units[xlabel]
            xlabel += " " + xunits
            self.plt.plot(xdata, ydata,
                pen=linestyle, name=plotlist[i])
            self.plt.setLabel('bottom', xlabel,units=xunits,**AxisLabelStyle)
        self.plt.setLabel('left', ylabel,units=yunits,**AxisLabelStyle)

    def plotTrend(self):
        '''
       plots linear trend
        '''
        if self.mainAxis == 'x':
            xpar = self.modparams.param('Parameter').value()
            ypar = self.trendParameter.value()
            self.plt.setLabel('bottom', xpar)
        if self.mainAxis == 'y':
            xpar = self.trendParameter.value()
            ypar = self.modparams.param('Parameter').value()
        x = self.findData(xpar)[self.indices]
        y = self.slope*x + self.intersection
        self.plt.plot(x,y,pen=TrendPen, name='%s Trend'%(self.trendParameter.value()))
        self.plt.setLabel('bottom', xpar)
        self.plt.setLabel('left', ypar)

    def clearPlotWindow(self):
        '''
        clears plot from data. clears legend.
        if there is no legend creates it
        '''
        # default legend position
        position = [30, 30]
        # clear plot area
        self.plt.clear()
        # remove old legend
        if self.legend:
            position = self.legend.pos()
            self.legend.scene().removeItem(self.legend)
        # creadte new legend
        self.plt.addLegend([90,20],offset=position)
        self.legend = self.plt.legend

    def setAxisScale(self):
        '''
        sets scale to the interval axis. if time, sets minimum value to 0,
        because it could have been cleared
        '''
        interval_parameter = self.sliderParam
        interval_data = self.findData(interval_parameter)
        if interval_parameter == self.timeParam:
            min_value = 0
        self.slider.setRange(min_value,
                             interval_data.max())

    def activeEntries(self):
        '''
        returns a list of active entries in the data bar
        '''
        plotlist = []
        # for i in self.data.keys():
        #     if self.params.param(i).value() == True:
        for item in self.keys:
            if self.tree.boxes[item].value() == True:
                plotlist.append(item)
        return plotlist


    def assignAttributes(self):
        '''
        assign parameters from modparams tree to class DataViewer
        attributes to shorten code
        '''
        self.nullFlag = self.modparams.param('Null')
        # assign chilren of 'Linear Trend' group to class attributes
        self.computeTrendFlag = self.modparams.param('Linear Trend').children()[0]
        self.trendParameter = self.modparams.param('Linear Trend').children()[1]
        self.trendSlope = self.modparams.param('Linear Trend').children()[2]
        self.trendIntersection = self.modparams.param('Linear Trend').children()[3]

    def setupGUI(self):
        pg.setConfigOption('background', (255, 255, 255))
        pg.setConfigOption('foreground',(0, 0, 0))
        self.setWindowIcon(QtGui.QIcon('images/Logo.png'))

        # Global widget where we place our layout
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        # Create and add menu bar
        self.menuBar = QtGui.QMenuBar()
        self.fileMenu = self.menuBar.addMenu('File')
        self.viewMenu = self.menuBar.addMenu('View')
        self.dataSetMenu = self.menuBar.addMenu('Dataset')
        # self.mohrMenu = self.menuBar.addMenu('Mohr\' Circles')
        self.prefMenu = self.menuBar.addMenu('Preferences')
        self.dataSetGroup = QtGui.QActionGroup(self)
        # create status bar
        self.layout.addWidget(self.menuBar, 0)
        self.layout.setMenuBar(self.menuBar)
        # create submenu items
        self.loadButton = QtGui.QAction('Load',self)
        self.saveButton = QtGui.QAction('Save',self)
        self.exitAction = QtGui.QAction('Exit',self,shortcut="Alt+F4")
        self.autoScaleButton = QtGui.QAction('Auto scale',self)
        self.crossHairButton = QtGui.QAction('Cross-hair',self, checkable=True)
        self.settingsButton = QtGui.QAction('Settings',self)
        # Add buttons to submenus
        self.fileMenu.addAction(self.loadButton)
        self.fileMenu.addAction(self.saveButton)
        self.fileMenu.addAction(self.exitAction)
        self.viewMenu.addAction(self.autoScaleButton)
        self.viewMenu.addAction(self.crossHairButton)
        self.prefMenu.addAction(self.settingsButton)
        # splitter is a widget, which handles the layout
        # it splits the main window into parameter window
        # and the plotting area
        self.tabWidget = QtGui.QTabWidget()
        self.layout.addWidget(self.tabWidget)
        self.splitter = QtGui.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.tabWidget.addTab(self.splitter, 'Main')

        # tree is a list of parameters to plot
        # self.tree = ParameterTree(showHeader=False)
        self.tree = CParameterTree(name='Data')
        # modtree is a list of governing parameters to modify plot
        self.modtree = ParameterTree(showHeader=False)
        # treesplitter splits parameter window into 2 halfs
        self.treesplitter = QtGui.QSplitter()
        self.buttonsplitter = QtGui.QSplitter()
        self.treesplitter.setOrientation(QtCore.Qt.Vertical)
        self.treesplitter.addWidget(self.tree)

        self.treesplitter.addWidget(self.modtree)
        self.treesplitter.setSizes(
            [int(self.height()*0.7), int(self.height()*0.3), 20]
        )
        self.treesplitter.setStretchFactor(0, 0)
        self.treesplitter.setStretchFactor(1, 0.9)

        self.splitter.addWidget(self.treesplitter)

        rightWidget = QtGui.QWidget()
        self.sublayout = QtGui.QVBoxLayout()
        rightWidget.setLayout(self.sublayout)

        self.plotContainer = pg.GraphicsLayoutWidget()
        self.sliderContainer = pg.GraphicsLayoutWidget()
        self.sliderContainer.setFixedHeight(80)
        # self.tabWidget.addTab(self.plotContainer, u"Main")

        self.sublayout.addWidget(self.plotContainer)
        self.layout.addWidget(self.sliderContainer)

        self.splitter.addWidget(rightWidget)
        self.splitter.setSizes([int(self.width()*0.4), int(self.width()*0.6)])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        # # crosshair plot is a class with cross hair capabilities
        # # first we need to add it's label attribute to sublayout
        # # so we could show the values of the crosshair
        self.plt = CrossHairPlot()
        self.plotContainer.addItem(self.plt.label)
        self.plotContainer.nextRow()
        self.plotContainer.addItem(self.plt)

        # set nice fonts
        setup_plot(self.plt)

        self.plt.setLabel('bottom', 'X Axis', **AxisLabelStyle)
        self.plt.setLabel('left', 'Y Axis', **AxisLabelStyle)
        self.plt.enableAutoRange(enable=True)
        self.autoScaleButton.triggered.connect(self.plt.enableAutoRange)

        self.slider = SliderWidget()
        self.sliderContainer.addItem(self.slider)

        self.setGeometry(80, 50, 800, 600)
        self.treesplitter.setStretchFactor(2, 0)
        self.treesplitter.setCollapsible(2, 0)
        # self.statusBar.setSizePolicy(QtGui.QSizePolicy.Ignored,
        #                              QtGui.QSizePolicy.Fixed)
        self.setGeometry(80, 30, 1000, 700)
        self.sigSettingGUI.emit(self)

    def setStatus(self,message):
        pass
        # self.statusBar.showMessage(message)
        # print(message)

    def computeTrend(self):
        '''
        computer linear trend a and b and
        from truncated data.
        '''
        if self.mainAxis == 'x': # if multiple plots vs x
            xpar = self.modparams.param('Parameter').value()
            ypar = self.trendParameter.value()
        if self.mainAxis == 'y': # if multiple plots vs y
            ypar = self.modparams.param('Parameter').value()
            xpar = self.trendParameter.value()

        x = self.findData(xpar)[self.indices]
        y = self.findData(ypar)[self.indices]
        A = np.array([x, np.ones(len(y))]).T
        ## Solves the equation a x = b by computing a vector x that
        ## minimizes the Euclidean 2-norm || b - a x ||^2.
        self.slope,self.intersection = np.linalg.lstsq(A,y)[0]
        self.trendSlope.setValue(self.slope)
        self.trendIntersection.setValue(self.intersection)

    def closeEvent(self, event):
        '''
        When pressing X button, show quit dialog.
        if yes, closes the window and ends the process
        '''
        # reply = QtGui.QMessageBox.question(self, 'Quit Dataviewer',
        #     "Are you sure to quit?", QtGui.QMessageBox.Yes |
        #     QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        # if reply == QtGui.QMessageBox.Yes:
        #     sys.exit()
        #     event.accept()
        # else:
        #     event.ignore()
        sys.exit()


if __name__ == '__main__':
    App = QtGui.QApplication(sys.argv)
    win = DataViewer()
    # win.showMaximized()
    win.show()
    # win.showFullScreen()
    # win.close()
    App.exec_()
