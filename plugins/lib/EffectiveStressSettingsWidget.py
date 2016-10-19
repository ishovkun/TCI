# -*- coding: utf-8 -*-
import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np
import re
from TCI.base_widgets.LineWidget import LineWidget

class EffectiveStressSettingsWidget(QtGui.QWidget):
    def __init__(self):
        super(EffectiveStressSettingsWidget,self).__init__()
        self.setupGUI()
        self.formula = None
        # self.okButton.clicked.connect(self.saveParameters)
        # self.cancelButton.clicked.connect(self.cancel)

    def setupGUI(self):
        self.setWindowTitle("Edit effectibve stress formula")
        self.setGeometry(500, 300, 350, 200)
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.variablesText = QtGui.QLabel('')

        # # stuff to make gray background for tree widget
        # g = pg.mkBrush(240,240,240)
        # b = pg.mkBrush(0,0,0)
        # w = pg.mkBrush(255,255,255)
        # bgBrush = pg.mkBrush(255,0,0)
        # tree.setFrameShape(QtGui.QFrame.NoFrame)
        # palette = QtGui.QPalette(g, g, g, g, g, b, b, g, g)
        # tree.setPalette(palette)

        self.variablesLine = LineWidget(type='label', label="Avaliable Variables:")
        self.axStressLine = LineWidget(type='text', label="Axial stress")
        self.confStressLine = LineWidget(type='text', label="Confining stress") 
        self.pressureLine = LineWidget(type='text', label="Pore pressure") 
        self.biotLine = LineWidget(type='value', label="Biot constant") 
        self.biotLine.box.setRange(0.1, 1)
        self.biotLine.box.setSingleStep(0.1)
        self.biotLine.setValue(0.9)
    
        self.layout.addWidget(self.variablesLine)
        self.layout.addWidget(self.axStressLine)
        self.layout.addWidget(self.confStressLine)
        self.layout.addWidget(self.pressureLine)
        self.layout.addWidget(self.biotLine)

    def setAvailableVariables(self,varlist):
        text = 'Avaliable variables: '
        i = 0
        for var in varlist:
            if (len(text)>50) and (i==0): 
                text += '\n'
                i += 1
            if (len(text)>100) and (i==1): 
                text += '\n'
                i += 1
            if (len(text)>150) and (i==2):
                text += '\n'
                i += 1
            if var!=varlist[-1]:
                text += '%s, '%(var)
            else:
                text += '%s.'%(var)
        self.variablesLine.setValue(text)

    def parameters(self):
        p1 = self.axStressLine.value()
        p2 = self.confStressLine.value()
        p3 = self.pressureLine.value()
        p4 = self.biotLine.value()
        return [p1, p2, p3, p4]

    def setParameters(self,parlist):
        self.axStressLine.setValue(parlist[0])
        self.confStressLine.setValue(parlist[1])
        self.pressureLine.setValue(parlist[2])
        self.biotLine.setValue(float(parlist[3]))

    def cancel(self):
        p1 = Parameters['Axial stress']
        p2 = Parameters['Confining pressure']
        p3 = Parameters['Pore pressure']
        p4 = Parameters['Biot coefficient']
        self.setParameters([p1,p2,p3,p4])
        self.close()

    def setConfig(self,config):
        p1 = config['Axial_stress']
        p2 = config['Confining_stress']
        p3 = config['Pore_pressure']
        p4 = config['Biot']
        self.conf = config
        self.setParameters([p1,p2,p3,p4])

    def config(self):
        p = self.parameters()
        self.conf['Axial_stress'] = p[0]
        self.conf['Confining_stress'] = p[1]
        self.conf['Pore_pressure'] = p[2]
        self.conf['Biot'] = p[3]
        return self.conf


if __name__ == '__main__':
    App = QtGui.QApplication(sys.argv)
    w = EffectiveStressSettingsWidget()
    varlist = ['sig1','sigD','Pc','Pu','1'*20,'2'*20]
    w.setAvailableVariables(varlist)
    w.setParameters(['sig1','Pc','Pu',0.8])
    w.show()
    App.exec_()
