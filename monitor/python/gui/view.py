# Imports ######################################################################
import sys, time
from threading import Thread

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QThread

from .MainWindow import Ui_MainWindow

# Globals ######################################################################

# Library ######################################################################

class GPSThread(QThread):
    log = pyqtSignal(str)
    def __init__(self, parent=None):
        super(GPSThread, self).__init__(parent)

    def run(self):
        while(1):
            time.sleep(1)
            self.log.emit('HelloWorld!')

class View(QMainWindow, Ui_MainWindow):
    def __init__(self, model, controller):
        super().__init__()

        self._model = model
        self._controller = controller

        self.commandList = ["Read Reg1", "Write Reg1", "Read Reg2", "Write Reg2"]

        # self._ui = Ui_MainWindow()
        # self._ui.setupUi(self)
        self.setupUi(self)
        self.setupGPSLogging()

        # connect widgets to controller
        # self.ConnectButton.clicked.connect(self._controller.pressConnectButton)
        # self.DisconnectButton.clicked.connect(self._controller.pressDisconnectButton)
        self.ConnectButton.clicked.connect(self.pressConnectButton)
        self.DisconnectButton.clicked.connect(self.pressDisconnectButton)
        self.CommandButton.clicked.connect(self.sendCommand)

        self.CommandComboBox.addItems(self.commandList)

    def setupUI(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(630, 990)

    def setupGPSLogging(self):
        self.worker = GPSThread()
        self.worker.log.connect(self.toLog)
        self.worker.started.connect(lambda: self.toLog('Starting GPS Logging...'))
        self.worker.finished.connect(lambda: self.toLog('Stopping GPS Logging...'))
        self.worker.start()

    def toLog(self, txt):
        self.GPSTextLog.appendPlainText(txt)

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

    @pyqtSlot(bool)
    def sendCommand(self):
        """
        Send a command to the FPGA
        """
        # TODO
        commandVal = self.CommandTextInput.toPlainText()
        command = self.CommandComboBox.currentText()
        print("Sent: " + commandVal + command)
        self.FPGATextLog.appendPlainText("Sent: " + commandVal + command)
        