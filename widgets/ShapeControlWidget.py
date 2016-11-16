import pyqtgraph as pg
from PySide import QtCore, QtGui


class ShapeControlWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ShapeControlWidget, self).__init__(None)
        self.parent = parent
        self.setupGUI()

    def setupGUI(self):
        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)
        self.okButton = QtGui.QPushButton("OK")
        self.layout.addWidget(self.okButton)

        if self.parent is not None:
            self.setParent(self.parent)

    def setParent(parent):
        self.parent = parent
        self.parent.layout.insertWidget(0, self)
