# Imports ######################################################################
from re import S
import sys

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSlot

from .MainWindow import Ui_MainWindow

# Globals ######################################################################

# Library ######################################################################
class View(QMainWindow, Ui_MainWindow):
    def __init__(self, model, controller):
        super().__init__()

        self._model = model
        self._controller = controller

        # self._ui = Ui_MainWindow()
        # self._ui.setupUi(self)
        self.setupUi(self)

        # connect widgets to controller
        # self.ConnectButton.clicked.connect(self._controller.pressConnectButton)
        # self.DisconnectButton.clicked.connect(self._controller.pressDisconnectButton)
        self.ConnectButton.clicked.connect(self.pressConnectButton)
        self.DisconnectButton.clicked.connect(self.pressDisconnectButton)


        # TODO: listen for model event signals to update

    def setupUI(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(490, 663)

    @pyqtSlot(bool)
    def pressConnectButton(self):
        """
        Press the Connect Button in the Connection Frame
        """
        # TODO
        self._model.connectStatus = True
        print("Connected!")
        self.FPGATextLog.appendPlainText("Connected!")
    
    @pyqtSlot(bool)
    def pressDisconnectButton(self):
        """
        Press the Disconnect Button in the Connection Frame
        """
        # TODO
        self._model.connectStatus = False
        print("Disconnected!")
        self.FPGATextLog.appendPlainText("Disconnected!")

    @pyqtSlot(int)
    def sendCommand(self, commandNum):
        """
        Send a command to the FPGA
        """
        # TODDO
        print("Sent: " + commandNum)
        