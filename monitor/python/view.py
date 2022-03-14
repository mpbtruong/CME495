# Imports ######################################################################
import sys, time
from threading import Thread

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QThread

from MainWindow import Ui_MainWindow

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
    def __init__(self, monitor):
        super().__init__()

        self.monitor = monitor

        self.commandList = ["Read Reg0", "Write Reg0", "Read Reg1", 
            "Write Reg1", "Read Reg2", "Write Reg2"]

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
        """
        Set up a thread for displaying GPS logging data
        """
        self.worker = GPSThread()
        self.worker.log.connect(self.toGPSLog)
        self.worker.started.connect(lambda: self.toGPSLog('Starting GPS Logging...'))
        self.worker.finished.connect(lambda: self.toGPSLog('Stopping GPS Logging...'))
        self.worker.start()

    def toGPSLog(self, txt):
        """
        Display a message on the GPS plain text widget.
        """
        self.GPSTextLog.appendPlainText(txt)

    @pyqtSlot(bool)
    def pressConnectButton(self):
        """
        Press the Connect Button in the Connection Frame
        """
        # TODO
        print("Connected!")
        self.FPGATextLog.appendPlainText("Connected!")
    
    @pyqtSlot(bool)
    def pressDisconnectButton(self):
        """
        Press the Disconnect Button in the Connection Frame
        """
        # TODO
        print("Disconnected!")
        self.FPGATextLog.appendPlainText("Disconnected!")

    @pyqtSlot(bool)
    def sendCommand(self):
        """
        Send a command to the FPGA
        """
        commandVal = self.CommandTextInput.toPlainText()
        command = self.CommandComboBox.currentText()
        
        # TODO replace read/write REG to abstracted (user-friendly) commands
        # so that user cannot directly read/write the registers
        # Read REG0
        if (command == "Read Reg0"):
            self.FPGATextLog.appendPlainText("Sent: " + command)
            cmd = self.monitor.get_command_by_id(0)
            self.monitor.execute_command(cmd, self.monitor.Command.READ)
            self.FPGATextLog.appendPlainText(str(cmd))

        # Write REG0
        elif (command == "Write Reg0"):
            self.FPGATextLog.appendPlainText("Sent: " + commandVal + command)
            cmd = self.monitor.get_command_by_id(0)
            self.monitor.execute_command(cmd, self.monitor.Command.WRITE, 
                commandVal.encode('utf-8'))
            self.FPGATextLog.appendPlainText(str(cmd))

        # Read REG1
        elif (command == "Read Reg1"):
            self.FPGATextLog.appendPlainText("Sent: " + command)
            cmd = self.monitor.get_command_by_id(1)
            self.monitor.execute_command(cmd, self.monitor.Command.READ)
            self.FPGATextLog.appendPlainText(str(cmd))

        # Write REG1
        elif (command == "Write Reg1"):
            self.FPGATextLog.appendPlainText("Sent: " + commandVal + command)
            cmd = self.monitor.get_command_by_id(1)
            self.monitor.execute_command(cmd, self.monitor.Command.WRITE,
                commandVal.encode('utf-8'))
            self.FPGATextLog.appendPlainText(str(cmd))
            
        print("Sent: " + commandVal + command)
        # self.FPGATextLog.appendPlainText("Sent: " + commandVal + command)
