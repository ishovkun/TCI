import sys
import pyqtgraph as pg
from PySide import QtCore, QtGui
import inspect, os

# script filename (usually with path)
# print os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory
# import numpy as np
# from ConfigParser import SafeConfigParser
from configobj import ConfigObj
from .EffectiveStressSettingsWidget import \
        EffectiveStressSettingsWidget
from .MainSettingsWidget import MainSettingsWidget

class SettingsWidget(QtGui.QMainWindow):
    """
    Widget that consists of several tabs with TCI
    settings. Eachs tab is a separate class, and
    this widget just imports and uses those
    """
    def __init__(self, filename=None):
        super(SettingsWidget, self).__init__()
        self.conf = {}
        self.setupGUI()
        if filename is None:
            current_dir = os.path.dirname(os.path.abspath(
                    inspect.getfile(inspect.currentframe())
            ))
            # config file is stored one directory up
            filename = os.path.join(current_dir, "../config.ini")
        self.filename = filename
        self.loadConfig()
        self.okButton.clicked.connect(self.saveConfig)
        self.cancelButton.clicked.connect(self.cancel)
        
    def loadConfig(self):
        config = ConfigObj(self.filename)
        self.mcWidget.setConfig(config['effective_stress'])
        self.msWidget.setConfig(config['Main parameters'])
        self.conf = config
                
        
    def saveConfig(self):
        print('Saving Settings')
        config = ConfigObj(self.filename)
        config['effective_stress'] = self.mcWidget.config()
        config['Main parameters'] = self.msWidget.config()
        config.write()
        self.close()

    def config(self):
        config = self.conf
        config['effective_stress'] = self.mcWidget.config()
        config['Main parameters'] = self.msWidget.config()
        return config

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
        self.mcWidget = EffectiveStressSettingsWidget()
        self.msWidget = MainSettingsWidget()
        self.tabWidget.addTab(self.msWidget,u'Main Settings')
        self.tabWidget.addTab(self.mcWidget,u'Effective stress')
        # set up button layout
        self.buttonsWidget = QtGui.QWidget()
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonsWidget.setLayout(self.buttonLayout)
        self.okButton = QtGui.QPushButton("OK")
        self.cancelButton = QtGui.QPushButton("Cancel")

        self.buttonLayout.addWidget(self.okButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.setContentsMargins(0,0,0,5)
        self.centralLayout.addWidget(self.tabWidget)
        self.centralLayout.addWidget(self.buttonsWidget)


if __name__ == '__main__':
    App = QtGui.QApplication(sys.argv)
    w = SettingsWidget()
    w.setWindowTitle('Settings')
    w.show()
    App.exec_()
