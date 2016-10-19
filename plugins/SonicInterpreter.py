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

BadBindingMessage = '''
Duplicates found in the comments column.
This is bad. I will do my best to 
square things away, but don't rely on me.
'''

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
        
        if parent is not None:
            self.parent.sigSettingGUI.connect(self.modifyParentMenu)

        
    def modifyParentMenu(self):
        # setting up the menu bar
        menuBar = self.parent.menuBar

        # add entry to load sonic files
        self.loadSonicDataAction = QtGui.QAction('Load sonic',
                                                 self.parent)
        self.parent.fileMenu.insertAction(self.parent.saveButton,
                                          self.loadSonicDataAction)
        
        # menubar entry corresponding to sonic widget
        self.menu = menuBar.addMenu('Sonic')
        self.viewMenu = self.menu.addMenu('View')
        self.modeMenu = self.menu.addMenu('Mode')
        self.transformMenu = self.menu.addMenu('Transform')
        self.intMenu = self.menu.addMenu('Interpretation')
 
        # VIEW MENU
        self.autoScaleAction = QtGui.QAction('Auto scale', self.parent,
                                             checkable=True,
                                             shortcut='Ctrl+S')
        self.autoScaleAction.setChecked(True)
        self.showArrivalsAction = QtGui.QAction('Arrivals', self.parent,
                                                checkable=True)
        self.showArrivalsAction.setDisabled(True)
        self.showTableAction = QtGui.QAction('Table', self.parent)
        self.yAxisMenu = self.viewMenu.addMenu('y axis')
        self.editGradientsAction = QtGui.QAction('Edit Gradients', self.parent)
        self.invertYAction = QtGui.QAction('Invert y axis', self.parent,
                                           checkable=True)
        self.viewMenu.addAction(self.autoScaleAction)
        self.viewMenu.addAction(self.showArrivalsAction)
        self.viewMenu.addAction(self.showTableAction)
        self.viewMenu.addAction(self.editGradientsAction)
        self.viewMenu.addAction(self.invertYAction)

        # MODE MENU
        self.modeGroup = QtGui.QActionGroup(self.parent)
        self.waveFormAction = QtGui.QAction('Wave Forms', self.parent,
                                            checkable=True)
        self.contourAction = QtGui.QAction('Contours', self.parent,
                                           checkable=True)
        self.waveFormAction.setActionGroup(self.modeGroup)
        self.contourAction.setActionGroup(self.modeGroup)
        self.contourAction.setChecked(True)

        self.modeMenu.addAction(self.waveFormAction)
        self.modeMenu.addAction(self.contourAction)

        # INTERPRETATION MENU
        self.pickArrivalsAction = QtGui.QAction('Pick arrivals', self.parent)
        self.handPickArrivalsAction = QtGui.QAction('Hand pick', self.parent,
                                                    checkable=True)
        self.moduliAction = QtGui.QAction('Elastic moduli', self.parent)
        self.moduliAction.setDisabled(True)
        self.handPickArrivalsAction.setDisabled(True)

        self.intMenu.addAction(self.pickArrivalsAction)
        self.intMenu.addAction(self.handPickArrivalsAction)
        self.intMenu.addAction(self.moduliAction)
        
        # TRANSFORM MENU
        self.showForrierMagnitudeAction = QtGui.QAction('Fourrier magnitude',
                                                        self.parent)
        self.showForrierPhasesAction = QtGui.QAction('Fourrier phases',
                                                     self.parent)
        self.filteringAction = QtGui.QAction('Frequency filtering',
                                             self.parent,
                                             checkable=True)
        self.transformMenu.addAction(self.showForrierMagnitudeAction)
        self.transformMenu.addAction(self.showForrierPhasesAction)
        self.transformMenu.addAction(self.filteringAction)
        
        # dict to store actions for y Axis
        self.yAxisActions = {}
        self.yAxisGroup = QtGui.QActionGroup(self.parent)
        self.yAxisActions['Track #'] = QtGui.QAction('Track #', self.parent,
                                                     checkable=True)
        self.yAxisActions['Track #'].setActionGroup(self.yAxisGroup)
        self.yAxisMenu.addAction(self.yAxisActions['Track #'])
        self.yAxisActions['Track #'].setChecked(True)

