import pyqtgraph as pg
from PySide import QtCore, QtGui


class ShapeControlWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ShapeControlWidget, self).__init__(None)
        self.parent = parent
        self.setupGUI()
        self.cancelButton.pressed.connect(self.cancel)

    def setupGUI(self):
        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)
        self.okButton = QtGui.QPushButton("OK")
        self.cancelButton = QtGui.QPushButton("Cancel")
        self.layout.addWidget(self.okButton)
        self.layout.addWidget(self.cancelButton)
        self.setMaximumHeight(50)

        if self.parent is not None:
            self.setParent(self.parent)

    def setParent(self, parent):
        self.parent = parent
        self.parent.layout.insertWidget(0, self)

    def cancel(self):
        self.hide()
        if self.parent is not None:
            # remove ROIs
            active_waves = self.parent.getActivePlots()
            for wave in active_waves:
                plot = self.parent.plots[wave]
                roi = self.parent.plotWidget.rois[wave]
                plot.removeItem(roi)
            # print(self.parent.plotWidget.rois)

    # def closeEvent(self, event):
    #     if self.parent is not None:
    #         self.hide()
    #     super(ShapeControlWidget, self).closeEvent(event)

    def computeArrivalTimes(self, x, y):
        for wave in self.parent.getActivePlots():
            print(wave)
