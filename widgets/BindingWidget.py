# coding: UTF-8
import sys
import numpy as np
from scipy.interpolate import interp1d
import pyqtgraph as pg
from PySide import QtGui, QtCore
from TCI.styles.setup_plot import setup_plot
from TCI.widgets.CParameterTree import CParameterTree
from TCI.styles.LabelStyles import AXIS_LABEL_STYLE
from TCI.styles.LineColors import DYNAMIC_MODULI_COLORS, STATIC_MODULI_COLORS

WaveTypes = ['P','Sx','Sy']
psi = 6894.75729
cm = 1e-2
inch = 2.54*cm
arrival_time_units = 1e-6

class BindingWidget(QtGui.QWidget):
    '''
    Widget computes geomechanic moduli as slopes
    for variables pointed in configuration
    and all moduli from sonic data
    '''
    enabled = False
    def __init__(self, parents=[None, None]):
        super(BindingWidget, self).__init__(None)
        	# QtCore.Qt.WindowStaysOnTopHint)
        self.setupGUI()
        self.static_moduli = {} # static moduli
        self.dynamic_moduli = {} # dynamic moduli
        self.parent = parents[0] # main widget
        self.controller = parents[1] # Sonic interpreter
        try:
            self.parent.slider.sigRangeChanged.connect(self.plot)
        except: pass
        self.autoScaleAction.triggered.connect(self.plot)
        self.plotVsXAction.triggered.connect(self.plot)
        self.plotVsYAction.triggered.connect(self.plot)

    def setConfig(self, testconf, capsconf, dens, length, atime, time='Time'):
        self.config = testconf
        self.capsconf = capsconf
        self.interval = atime
        self.sampLength = length*inch
        self.density = dens*1000.
        self.time = self.parent.findData(time)

    def run(self):
        self.dmoduli = {}
        self.smoduli = {}
        self.show()
        self.getSonicTimes()
        self.interpolateGData()
        self.getSlopes()
        self.getDynamicModuli()
        self.setupTree()
        self.setupMenu()
        self.tree.sigStateChanged.connect(self.plot)
        self.plot()

    def interpolateGData(self):
        self.gdata = {}
        print ('Interpolating geomechanical data')
        for key in self.parent.keys:
            interp = interp1d(self.parent.findData('Time'),
                              self.parent.findData(key),
                              bounds_error=False)
            self.gdata[key] = interp(self.itimes)

    def setupMenu(self):
        # clear y axis menu and groups
        self.parMenu.clear()
        for action in self.parameterGroup.actions():
            self.parameterGroup.removeAction(action)
        self.parameterActions = {}
        # assign new actions
        for key in self.parent.keys:
            action = QtGui.QAction(key,self,checkable=True)
            action.setActionGroup(self.parameterGroup)
            self.parMenu.addAction(action)
            self.parameterActions[key] = action
            action.triggered.connect(self.plot)
        try:
            self.parameterActions['Time'].setChecked(True)
        except: pass

    def getSonicTimes(self):
        '''
        every wave has its own recording time
        geomecanic time range includes all sonic times
        no need to plot all geomechanics
        take average recording times for sonic data
        plot geomechanics at them
        also, there can be different amount of sonic data
        for each wave. so must make arrays same length.
        '''
        print ('Computing times for output')
        l = []
        for wave in WaveTypes:
            l.append(len(self.controller.times[wave]))
        l = min(l)
        gtimes = np.zeros(l)
        for wave in WaveTypes:
            gtimes += self.controller.times[wave][:l]
        gtimes /= 3
        self.itimes = gtimes

    def getSlopes(self):
        '''
        Get moduli from geomechanical data
        '''
        N = len(self.itimes)
        config = self.config
        for mod in self.config['moduli'].keys():
            self.smoduli[mod] = np.zeros(N)
            xarr = self.parseExpression(config['moduli'][mod]['x'])
            yarr = self.parseExpression(config['moduli'][mod]['y'])
            for i in range(N):
                ind = abs(self.time-self.itimes[i]) < self.interval/2
                x = xarr[ind]
                y = yarr[ind]
                A = np.array([x, np.ones(len(y))]).T
                slope,intersection = np.linalg.lstsq(A, y)[0]
                self.smoduli[mod][i] = slope

    def computeVelocities(self):
        '''
        compute speed of sound base on
        - arrival times/sample length
        - changes in sample length due to strain
        - sonic cap correction
        Algorithm:
        get arrival times from somic viewer
        substrac sonic cap correction
        correct sample length for strain
        get velocity
        '''
        velocities = {}
        for wave in WaveTypes:
            arrival_times = np.copy(self.controller.sonicViewer.arrival_times[wave])
            ### correct for end-caps
            corr = float(self.capsconf[wave])
            arrival_times -= corr
            # convert to seconds
            arrival_times *= arrival_time_units
            # interpolate arrival times
            interpolator = interp1d(self.controller.times[wave], arrival_times,
                                    bounds_error=False)
            interpolated_arrival_times =  interpolator(self.itimes)

            # get sanoke length base on strains
            axial_strain = self.parent.findData('Ex')[self.controller.geo_indices[wave]]
            interpolator = interp1d(self.controller.times[wave], (1-axial_strain),
                                    bounds_error=False)
            interpolated_lengths = self.sampLength*interpolator(self.itimes)

            # compute velocities
            velocities[wave] = interpolated_lengths/interpolated_arrival_times

        return velocities

    def getDynamicModuli(self):
        velocities = self.computeVelocities()
        Ctx = velocities['Sx']
        Cty = velocities['Sy']
        Cl = velocities['P']
        rho = self.density
        Gx = Ctx**2*rho
        Gy = Cty**2*rho
        lambx = (Cl**2-Ctx**2)*rho
        lamby = (Cl**2-Cty**2)*rho
        Ex = Gx*(3*lambx + 2*Gx)/(lambx + Gx)
        Ey = Gy*(3*lamby + 2*Gy)/(lamby + Gy)
        nux = lambx/2/(lambx + Gx)
        nuy = lamby/2/(lamby + Gy)
        Kx = Ex/3./(1.-2*nux)
        Ky = Ey/3./(1.-2*nuy)
        if self.config['units']['Young'] == 'psi':
            self.dmoduli['Young_x'] = Ex/psi
            self.dmoduli['Young_y'] = Ey/psi
        elif self.config['units']['Young'] == 'Pa':
            self.dmoduli['Young_x'] = Ex
            self.dmoduli['Young_y'] = Ey
        if self.config['units']['Shear'] == 'psi':
            self.dmoduli['Shear_x'] = Gx/psi
            self.dmoduli['Shear_y'] = Gy/psi
        if self.config['units']['Shear'] == 'Pa':
            self.dmoduli['Shear_x'] = Gx
            self.dmoduli['Shear_y'] = Gy
        if self.config['units']['Bulk'] == 'psi':
            self.dmoduli['Bulk_x'] = Kx/psi
            self.dmoduli['Bulk_y'] = Ky/psi
        if self.config['units']['Bulk'] == 'Pa':
            self.dmoduli['Bulk_x'] = Kx
            self.dmoduli['Bulk_y'] = Ky
        if self.config['units']['Poisson'] == '':
            self.dmoduli['Poisson_x'] = nux
            self.dmoduli['Poisson_y'] = nuy

    def plot(self):
        if not self.enabled: return 0
        if not self.isVisible(): return 0
        self.plt.clear()
        self.plt.showGrid(x=True, y=True)
        interval_parameter = self.parent.sliderParam
        interval = self.parent.slider.interval()
        ind = self.getIndices()
        active = self.tree.activeItems()
        par = self.parameter()
        geo_data = self.getGeoArray()
        geo_unit_str = self.parent.findUnits(par)
        if self.plotVsXAction.isChecked():
            x = geo_data
            xName = par
            xName += " %s"%geo_unit_str
        elif self.plotVsYAction.isChecked():
            y = geo_data
            yName = par
            yName += " %s"%geo_unit_str
        for group in active.keys():
            for key in active[group]:
                color = self.getColor(group, key)
                linestyle = pg.mkPen(color=color, width=3)
                unit_str = self.config['units'][key]
                if group=='Static':
                    if self.plotVsXAction.isChecked():
                        y = self.smoduli[key][ind]
                        yName = key + " (%s)"%unit_str
                    elif self.plotVsYAction.isChecked():
                        x = self.smoduli[key][ind]
                        xName = key + " (%s)"%unit_str
                elif group=='Dynamic':
                    if self.plotVsXAction.isChecked():
                        y = self.dmoduli[key][ind]
                        yName = key + " (%s)"%unit_str
                    elif self.plotVsYAction.isChecked():
                        x = self.dmoduli[key][ind]
                        xName = key + " (%s)"%unit_str
                self.plt.plot(x, y, pen=linestyle)
                self.plt.setLabel('left', yName, **AXIS_LABEL_STYLE)
                self.plt.setLabel('bottom', xName, **AXIS_LABEL_STYLE)

        if self.autoScaleAction.isChecked():
            self.plt.enableAutoRange()

    def getGeoArray(self, idx=None):
        '''
        get vector from the geomechanical dataset
        '''
        if idx is None:
            idx = self.getIndices()
        par = self.parameter()
        result = self.gdata[par][idx]
        return result

    def getIndices(self):
        interval = self.parent.slider.interval()
        idx = (self.itimes>=interval[0]) & (self.itimes<=interval[1])
        return idx

    def getColor(self, group, key):
        '''
        get color from tree
        Input:
        group: string
        key: string
        '''
        assert group in self.tree.activeItems().keys(), \
            "Bad group keyword %s"%(group)
        assert key in self.tree.groups[group]['colors'].keys(), \
            "Bad key keyword %s"%(key)
        return self.tree.groups[group]['colors'][key].getColor()

    def getActiveModuli(self):
        '''
        get arrays (truncated with indices) of moduli
        corresponding to active checkboxes
        returns a dict: {key: np.array}
        '''
        moduli = {}
        active = self.tree.activeItems()
        idx = self.getIndices()
        for group in active.keys():
            for key in active[group]:
                if group=='Static':
                    # key_out = key + "_" + "st"
                    moduli[key] = self.smoduli[key][idx]
                elif group=='Dynamic':
                    # key_out = key + "_" + "din"
                    moduli[key] = self.dmoduli[key][idx]
        return moduli

    def setupTree(self):
        # for mod in self.dmoduli:
        print ('setting up binding widget tree')
        self.tree.clear()
        self.tree.addItems(self.dmoduli.keys(), group='Dynamic',
                           colors=DYNAMIC_MODULI_COLORS)
        self.tree.addItems(self.smoduli.keys(), group='Static',
                           colors=STATIC_MODULI_COLORS)

    def parameter(self):
        for key in self.parameterActions.keys():
            if self.parameterActions[key].isChecked(): return key

    def parseExpression(self, expr):
        '''
        computes array corresponding to expression
        '''
        if expr=='':
            return 0
        if 'import' in expr: return 0
        if 'sys' in expr: return 0
        if 'os' in expr: return 0
        for key in self.parent.keys:
            exec('%s=self.parent.findData(\'%s\')'%(key,key))
        try:
            return eval(expr)
        except:
            return 0

    def setupGUI(self):
        pg.setConfigOption('background', (255,255,255))
        pg.setConfigOption('foreground', (0, 0, 0))
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        # menu
        self.menuBar = QtGui.QMenuBar()
        self.layout.setMenuBar(self.menuBar)
        # menu actions
        self.viewMenu = self.menuBar.addMenu('View')
        self.parMenu = self.viewMenu.addMenu('Parameter')
        self.plotVsMenu = self.viewMenu.addMenu('Plot versus')
        self.plotVsXAction = QtGui.QAction('x', self, checkable=True)
        self.plotVsYAction = QtGui.QAction('y', self, checkable=True)
        self.plotVsGroup = QtGui.QActionGroup(self)
        self.plotVsXAction.setActionGroup(self.plotVsGroup)
        self.plotVsYAction.setActionGroup(self.plotVsGroup)
        self.plotVsMenu.addAction(self.plotVsXAction)
        self.plotVsMenu.addAction(self.plotVsYAction)
        self.plotVsXAction.setChecked(True)
        self.autoScaleAction = QtGui.QAction('Auto scale', self,
                                             checkable=True)
        self.autoScaleAction.setChecked(True)
        self.viewMenu.addAction(self.autoScaleAction)
        self.parameterGroup = QtGui.QActionGroup(self)
        # widgets
        splitter = QtGui.QSplitter()
        splitter.setOrientation(QtCore.Qt.Horizontal)
        self.tree = CParameterTree(name='Elastic moduli')

        self.sublayout = pg.GraphicsLayoutWidget()
        #
        self.layout.addWidget(splitter)
        splitter.addWidget(self.tree)
        splitter.addWidget(self.sublayout)
        self.plt = self.sublayout.addPlot()
        setup_plot(self.plt)
        #
        self.tree.setGeometry(0,0,200,15)
        splitter.setSizes([int(self.width()*0.4),
            int(self.width()*0.6),
            ])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    def setEnabled(self, enabled=True):
        self.enabled = enabled
