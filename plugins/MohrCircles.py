# -*- coding: utf-8 -*-
'''
WARNING:
PRESSING 'CANCEL' BUTTON DOESN'T CLOSE THE APPLICATION
USE X BUTTON INSTEAD
(THIS IS ONLY IMPORTANT FOR RUNNING THIS WIDGET
    AS A STANDALONE)
'''

from PySide import QtGui, QtCore
from PySide.QtCore import Slot
import pyqtgraph as pg
import numpy as np
import sys

from TCI.base_widgets.CursorItem import CursorItem
from TCI.plugins.lib.MohrCirclesWidget import MohrCirclesWidget
# we need to store the parameters for effective stresses in settings,
# add this widget to settings tab
from TCI.plugins.lib.EffectiveStressSettingsWidget import EffectiveStressSettingsWidget

parentMenuString = 'Mohr\' Circles'
addPointActionString = 'Add point'
removePointActionString = 'Delete point'
activateActionString = 'Draw Mohr\'s Circles'

class MohrCircles:
    def __init__(self, parent):
        self.parent = parent
        self.cursors = []   # cursors for current data set
        self.allCursors = {}    # cursors for all datasets
        self.parent.sigSettingGUI.connect(self.modifyParentGUI)
        self.parent.sigConnectParameters.connect(self.enableParentMenu)
        self.mcWidget = MohrCirclesWidget()

    def modifyParentGUI(self):
        self.parentMenu = self.parent.menuBar.addMenu(parentMenuString)
        # self.parentMenu.setEnabled(False)
        
        # add EffectiveStressSettingsWidget to parent settings menu
        self.effectiveStressWidget = EffectiveStressSettingsWidget()
        self.parent.settings.addWidget(self.effectiveStressWidget,
                                       config_header="effective_stress",
                                       label="Effective stress")
        
        self.addPointAction = QtGui.QAction(addPointActionString,
                                            self.parent, shortcut='Ctrl+Q')
        self.removePointAction = QtGui.QAction(removePointActionString,
                                               self.parent, shortcut='Ctrl+R')
        self.activateAction = QtGui.QAction(activateActionString,
                                            self.parent, shortcut='Alt+M')
        self.parentMenu.addAction(self.addPointAction)
        self.parentMenu.addAction(self.removePointAction)
        self.parentMenu.addAction(self.activateAction)
        
        self.addPointAction.setEnabled(True)
        self.removePointAction.setEnabled(True)
        self.activateAction.setEnabled(True)
        self.addPointAction.triggered.connect(self.addCursor)
        self.removePointAction.triggered.connect(self.removeCursor)
        self.parent.sigConnectParameters.connect(self.enableParentMenu)
        self.parent.plt.sigRangeChanged.connect(self.scaleCursors)
        self.parent.tree.sigStateChanged.connect(self.bindCursors)
        self.parent.sigNewDataSet.connect(self.newDataSet)
        self.parent.sigSaveDataSet.connect(self.saveDataSet)
        self.parent.sigUpdatingPlot.connect(self.drawCursors)
        self.activateAction.triggered.connect(self.runMCWidget)

    @Slot(str)
    def saveDataSet(self, dataSetName):
        self.allCursors[dataSetName] = self.cursors

    @Slot(str)
    def loadDataSet(self, dataSetName):
        self.cursors = self.allCursors[dataSetName] 

    def newDataSet(self):
        self.allCursors[self.parent.currentDataSetName] = []

    def addCursor(self):
        print('adding a Cursor')
        viewrange = self.parent.plt.viewRange()
        
        # this is a weird way to scale a new cursor initially
        rangeX = [viewrange[0][0], viewrange[0][1]]
        rangeY = [viewrange[1][0], viewrange[1][1]]
        pos = [(rangeX[0] + rangeX[1])/2, (rangeY[0] + rangeY[1])/2]
        xSize = float(rangeX[1]-rangeX[0])/50*800/self.parent.plt.width()
        ySize = float(rangeY[1]-rangeY[0])/50*800/self.parent.plt.height()
        cursor = CursorItem(pos, [xSize,ySize], pen=(4, 9))
        self.cursors.append(cursor)
        self.allCursors[self.parent.currentDataSetName] = self.cursors
        
        # bind cursor if there is something to plot
        if len(self.parent.activeEntries()) > 0:
            self.bindCursors()
            self.drawCursors()

    def removeCursor(self):
        if len(self.cursors)>0:
            cursor = self.cursors.pop(-1)
            self.parent.plt.removeItem(cursor)

    def scaleCursors(self):
        '''
        make cursors circles of an appropriate size when scaling plot
        '''
        plt = self.parent.plt
        viewrange = plt.viewRange()
        rangeX = [viewrange[0][0], viewrange[0][1]]
        rangeY = [viewrange[1][0], viewrange[1][1]]
        xSize = float(rangeX[1]-rangeX[0])*16/plt.width()
        ySize = float(rangeY[1]-rangeY[0])*16/plt.height()
        size = np.array([xSize,ySize])
        for cursor in self.cursors:
            # workaround to force the cursor stay on the same place
            oldSize = cursor.getSize() 
            cursor.translate(oldSize/2,snap=None)
            cursor.setSize(size)
            cursor.translate(-size/2,snap=None)
        
    def bindCursors(self):
        '''
        make cursor slide along data
        '''
        plotlist = self.parent.activeEntries()
        if len(plotlist) > 0: # if some of tree items are checked
            if self.parent.mainAxis == 'y':
                xlabel = plotlist[-1]
                ylabel = self.parent.modparams.param('Parameter').value()
            elif self.parent.mainAxis == 'x':
                ylabel = plotlist[-1]
                xlabel = self.parent.modparams.param('Parameter').value()
                x_data = self.parent.findData(xlabel)
                y_data = self.parent.findData(ylabel)
                x = x_data[self.parent.indices]
                y = y_data[self.parent.indices]
            for cursor in self.cursors:
                cursor.setData(x,y)
        else:  # if tree is inactive remove cursors
            for cursor in self.cursors:
                self.parent.plt.removeItem(cursor)

    def drawCursors(self):
        '''
        add cursors again after clearing the plot window
        '''
        if len(self.parent.activeEntries()) > 0:
            for cursor in self.cursors:
                self.parent.plt.addItem(cursor)
            
    def enableParentMenu(self):
        pass
        # self.parentMenu.setEnabled(True)
        # self.addPointAction.setEnabled(True)
        # self.removePointAction.setEnabled(True)

    def runMCWidget(self):
        config = self.effectiveStressWidget.parameters()
        biot_coef = config[3]
        # parent.settings.mcWidget.parameters()
        # self.mcWidget.show()
        for dataset in self.allCursors.keys():
            print(dataset)
            cursors = self.allCursors[dataset]
            ncircles = 0
            if cursors == []: continue    # skip dataset
            else:    # retreive data from cursor-selected points
                indices = []
                for cursor in cursors:
                    index = cursor.index
                    indices.append(index)
                    ncircles += 1
                    
                    # find axial stress
                    all_ax_stress = self.parent.findDatainAllDatasets(dataset,
                                                                  key=config[0])
                    ax_stress = all_ax_stress[index]

                    # find confining stress
                    if config[1] == '0': conf_stress = 0 # force to 0
                    else:
                        # all conf stress points
                        all_conf_stress = self.parent.findDatainAllDatasets(dataset,
                                                                 key=config[1])
                        conf_stress = all_conf_stress[index]

                    # find pore pressure
                    if config[2]=='0': pressure = 0 # force to 0
                    else:
                        all_pressure = self.parent.findDatainAllDatasets(dataset,
                                                                 key=config[2])
                        pressure = all_pressure[index]

                    # compute effective stresses
                    sigma_ax = ax_stress - biot_coef*pressure
                    sigma_conf = conf_stress - biot_coef*pressure
                    sigma1 = max(sigma_ax, sigma_conf)
                    sigma3 = min(sigma_ax, sigma_conf)
                    self.mcWidget.addData(sigma1, sigma3,
                                          name=dataset + "_" + str(ncircles))
                    self.mcWidget.run()
                    self.mcWidget.show()
                    self.mcWidget.activateWindow()

