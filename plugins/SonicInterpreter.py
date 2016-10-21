# coding: UTF-8
import sys,os
import pyqtgraph as pg
from PySide import QtGui, QtCore
from pyqtgraph.parametertree import Parameter, ParameterTree
from pyqtgraph.parametertree import types as pTypes
from pyqtgraph.Point import Point
import numpy as np

import pickle

from TCI.widgets.SonicViewer import SonicViewer
from TCI.lib.readtrc import read_TRC
from TCI.lib.functions import *

BadBindingMessage = '''
Duplicates found in the comments column.
This is bad. I will do my best to 
square things away, but don't rely on me.
'''

FILE_DIALOG_TITLE = 'Open files'
WAVE_TYPES = ['P','Sx','Sy']

class SonicInterpreter:
    '''
    Class responsible for interaction of SonicViewerWidget
    and dataviewer class
    '''
    def __init__(self, parent=None):
        self.sonicViewer = SonicViewer(parent=parent)
        # self.sonicViewer.show()
        # self.sonicViewer.activateWindow()
        # self.sonicViewer.raise_()
        # self.fAmlitudeWidget
        # self.fPhaseWidget
        self.parent = parent
        self.progressDialog = QtGui.QProgressDialog()
        
        if parent is not None:
            self.setupActions()
            self.parent.sigSettingGUI.connect(self.modifyParentMenu)
            self.connectActions()

    def loadFileDialog(self):
        '''
        shows file dialog and calls loadData upon selecting
        files
        '''
        lastdir = self.parent.checkForLastDir()
        filter_mask = "Sonic data files (*.TRC *.txt)"
        filenames = QtGui.QFileDialog.getOpenFileNames(None,
            FILE_DIALOG_TITLE, "%s"%(lastdir), filter_mask)[0]
        
        if filenames != []:
            self.loadData(filenames)
            self.addSonicTab()
            self.bindData()

    def addSonicTab(self):
        '''
        Adds sonic tab to parent. If it exists just activates it
        '''
        tab_bar = self.parent.tabWidget
        if tab_bar.indexOf(self.sonicViewer) == -1:
            tab_bar.addTab(self.sonicViewer, "Sonic")
        tab_bar.setCurrentWidget(self.sonicViewer)

    def loadData(self, filenames):
        '''
        Read the supplied files.
        show progress dialog during that operations
        '''
        n_files = len(filenames)
        raw_data = {"P":{}, "Sx":{}, "Sy":{}}
        self.progressDialog.show()

        # iterate through files
        i = 0.
        for f in filenames:
            fdir, fname = os.path.split(f)
            # check file extension
            if '.TRC' in fname:
                waves = read_TRC(f)
                # determine what wave this thing pertains to
                wave_type_inferred = False
                for wave_name in WAVE_TYPES:
                    if wave_name  in fname:
                        raw_data[wave_name][fname] = waves
                        wave_type_inferred = True
                        
                if not wave_type_inferred:
                    print("Could not infer wave type for %s"%(fname))
            else:
                print('unknown extension')
            i += 1
            self.progressDialog.setValue(i/n_files*100)
        self.progressDialog.hide()

        # organize data
        self.sonicViewer.setData(raw_data)


    def connectActions(self):
        self.loadSonicDataAction.triggered.connect(self.loadFileDialog)

    def setupActions(self):
        # add entry to load sonic files
        self.loadSonicDataAction = QtGui.QAction('Load sonic',
                                                 self.parent)
        self.parent.loadSonicDataAction = self.loadSonicDataAction
        
        self.autoScaleAction = QtGui.QAction('Auto scale', self.parent,
                                             checkable=True,
                                             shortcut='Ctrl+S')
        self.autoScaleAction.setChecked(True)
        self.showArrivalsAction = QtGui.QAction('Arrivals', self.parent,
                                                checkable=True)
        self.showArrivalsAction.setDisabled(True)
        self.showTableAction = QtGui.QAction('Table', self.parent)
        self.editGradientsAction = QtGui.QAction('Edit Gradients', self.parent)
        self.invertYAction = QtGui.QAction('Invert y axis', self.parent,
                                           checkable=True)
        self.modeGroup = QtGui.QActionGroup(self.parent)
        self.waveFormAction = QtGui.QAction('Wave Forms', self.parent,
                                            checkable=True)
        self.contourAction = QtGui.QAction('Contours', self.parent,
                                           checkable=True)
        self.waveFormAction.setActionGroup(self.modeGroup)
        self.contourAction.setActionGroup(self.modeGroup)
        self.contourAction.setChecked(True)
        self.pickArrivalsAction = QtGui.QAction('Pick arrivals', self.parent)
        self.handPickArrivalsAction = QtGui.QAction('Hand pick', self.parent,
                                                    checkable=True)
        self.moduliAction = QtGui.QAction('Elastic moduli', self.parent)
        self.moduliAction.setDisabled(True)
        self.handPickArrivalsAction.setDisabled(True)

        self.showForrierMagnitudeAction = QtGui.QAction('Fourrier magnitude',
                                                        self.parent)
        self.showForrierPhasesAction = QtGui.QAction('Fourrier phases',
                                                     self.parent)
        self.filteringAction = QtGui.QAction('Frequency filtering',
                                             self.parent,
                                             checkable=True)

        # dict to store actions for y Axis
        self.yAxisActions = {}
        self.yAxisGroup = QtGui.QActionGroup(self.parent)
        self.yAxisActions['Track #'] = QtGui.QAction('Track #', self.parent,
                                                     checkable=True)
        self.yAxisActions['Track #'].setActionGroup(self.yAxisGroup)
        self.yAxisActions['Track #'].setChecked(True)
        
    def modifyParentMenu(self):
        # setting up the menu bar
        menuBar = self.parent.menuBar

        self.parent.fileMenu.insertAction(self.parent.saveButton,
                                          self.loadSonicDataAction)
        
        
        # menubar entry corresponding to sonic widget
        self.menu = menuBar.addMenu('Sonic')
        self.viewMenu = self.menu.addMenu('View')
        self.modeMenu = self.menu.addMenu('Mode')
        self.transformMenu = self.menu.addMenu('Transform')
        self.intMenu = self.menu.addMenu('Interpretation')
 
        # VIEW MENU
        self.viewMenu.addAction(self.autoScaleAction)
        self.viewMenu.addAction(self.showArrivalsAction)
        self.viewMenu.addAction(self.showTableAction)
        self.viewMenu.addAction(self.editGradientsAction)
        self.viewMenu.addAction(self.invertYAction)

        # y axis menu
        self.yAxisMenu = self.viewMenu.addMenu('y axis')
        self.yAxisMenu.addAction(self.yAxisActions['Track #'])

        # MODE MENU
        self.modeMenu.addAction(self.waveFormAction)
        self.modeMenu.addAction(self.contourAction)

        # INTERPRETATION MENU
        self.intMenu.addAction(self.pickArrivalsAction)
        self.intMenu.addAction(self.handPickArrivalsAction)
        self.intMenu.addAction(self.moduliAction)
        
        # TRANSFORM MENU
        self.transformMenu.addAction(self.showForrierMagnitudeAction)
        self.transformMenu.addAction(self.showForrierPhasesAction)
        self.transformMenu.addAction(self.filteringAction)
        
    def bindData(self):
        '''
        bind wave tracks to the time of experiment the were measured.
        it essentially implies parsing comments and comparing it to sonic data
        names
        Algorithm:
        - find times for non-empty comments
        - throw out repeated comments (take last occurrence)
        - compare comments with sonic file names
        '''
        record_times = {}
        comments = self.parent.comments
        times = self.parent.findData(self.parent.timeParam)
        
        # filter out empty comments
        non_empty = [i for i, c in enumerate(comments) if c != b'' and c!='']
        comments = comments[non_empty]
        times = times[non_empty]

        # check if there are any duplicates
        comments, ind = remove_duplicates(comments)
        times = times[ind]

        # find same strings in sonic file names
        for wave in WAVE_TYPES[0]:
            wave_files = list(self.sonicViewer.data[wave].keys())
            indices = compare_arrays(comments, wave_files)
            # which items wave_keys are not in comments
            spurious_entries = array_diff(wave_files, comments)
            for e in spurious_entries:
                del self.sonicViewer.data[wave][wave_files[e]]
            record_times[wave] = times[indices]
            
        # rebuild sonic table
        self.sonicViewer.createTable()
           
           
           


