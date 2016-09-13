import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import inspect, os

# import numpy as np
from configobj import ConfigObj
from TCI.widgets.MainSettingsWidget import MainSettingsWidget


class SettingsWidget(QtGui.QMainWindow):
    """
    Widget that consists of several tabs with TCI
    settings. Eachs tab is a separate class, and
    this widget just imports and uses those
    """
    def __init__(self, filename=None):
        super(SettingsWidget, self).__init__()
        self.conf = {}
        # self.mcWidget = EffectiveStressSettingsWidget()
        # widgets that whould be shown on tabs
        self.widgets = []
        # configuration sections names that widgets will get data from and edit
        self.conf_headers = []

        self.setupGUI()
        if filename is None:
            current_dir = os.path.dirname(os.path.abspath(
                    inspect.getfile(inspect.currentframe())
            ))
            # config file is stored one directory up
            filename = os.path.join(current_dir, "../config.ini")
            
        self.filename = filename
        self.okButton.clicked.connect(self.saveConfig)
        self.cancelButton.clicked.connect(self.cancel)
        
        # add basic widget
        self.msWidget = MainSettingsWidget()
        self.addWidget(self.msWidget, config_header="Main parameters",
                       label=u'Main Settings')

    def loadConfig(self):
        print("Loading config")
        config = ConfigObj(self.filename)
        for i in range(len(self.widgets)):
            self.widgets[i].setConfig(config[self.conf_headers[i]])
        self.conf = config

    def saveConfig(self):
        print('Saving Settings')
        config = ConfigObj(self.filename)
        for i in range(len(self.widgets)):
            config[self.conf_headers[i]] = self.widgets[i].config()
        config.write()
        self.close()

    def config(self):
        config = self.conf
        for i in range(len(self.widgets)):
            config[self.conf_headers[i]] = self.widgets[i].config()
        return self.conf

    def cancel(self):
        print('cancel settings change')
        self.loadConfig()
        self.close()

    def setupGUI(self):
        self.setWindowTitle('Settings')
        self.setGeometry(500, 300, 400, 300)
        centralWidget = QtGui.QWidget()
        self.centralLayout = QtGui.QVBoxLayout()
        self.setCentralWidget(centralWidget)
        centralWidget.setLayout(self.centralLayout)

        self.tabWidget = QtGui.QTabWidget()
        # self.tabWidget.addTab(self.msWidget, u'Main Settings')
        # self.tabWidget.addTab(self.mcWidget, u'Effective stress')
        # set up button layout
        self.buttonsWidget = QtGui.QWidget()
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonsWidget.setLayout(self.buttonLayout)
        self.okButton = QtGui.QPushButton("OK")
        self.cancelButton = QtGui.QPushButton("Cancel")

        self.buttonLayout.addWidget(self.okButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.setContentsMargins(0, 0, 0, 5)
        self.centralLayout.addWidget(self.tabWidget)
        self.centralLayout.addWidget(self.buttonsWidget)

    def addWidget(self, widget, config_header, label=''):
        '''
        widget - instance of widget
        lable - tab string
        '''
        print("adding widget to settings menu")
        self.tabWidget.addTab(widget, label)
        self.widgets.append(widget)
        self.conf_headers.append(config_header)
        self.loadConfig()

        



if __name__ == '__main__':
    App = QtGui.QApplication(sys.argv)
    w = SettingsWidget()
    w.setWindowTitle('Settings')
    w.show()
    App.exec_()

