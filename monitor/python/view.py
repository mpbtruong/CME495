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
    def __init__(self, GPSMonitor, parent=None):
        super(GPSThread, self).__init__(parent)
        self.GPSMonitor = GPSMonitor

    def run(self):
        timeout = 1
        counter = 0
        while not self.GPSMonitor.is_connected():
            time.sleep(timeout)
            print("Attemping to Connect to GPS...")
            self.GPSMonitor.connect_uart()
            counter += 1
            if (counter == 5):
                counter = 0
                timeout += 5


        while(1):
            time.sleep(1)
            # self.log.emit('HelloWorld!')
            # TODO print GPS sentences
            # Read GGA sentence
            # sentence = self.GPSMonitor.readNMEAFrameSelect(self.GPSMonitor.TALKER_ID_GPS,
            #     self.GPSMonitor.GGA)
            
            sentence = self.GPSMonitor.readNMEAFrame()
            # print(sentence)
            self.log.emit(f'{sentence.talker} {sentence.sentence_type}: {sentence.data}')

            # Read GSA sentence

class View(QMainWindow, Ui_MainWindow):
    def __init__(self, FPGAMonitor, GPSMonitor):
        super().__init__()
        self.FPGAMonitor = FPGAMonitor
        self.GPSMonitor = GPSMonitor
        # self.FPGAConnected = self.FPGAMonitor.is_connected()
        # self.GPSConnected = self.GPSMonitor.is_connected()

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
        self.worker = GPSThread(self.GPSMonitor)
        self.worker.log.connect(self.toGPSLog)
        self.worker.started.connect(lambda: self.toGPSLog('Starting GPS Logging...'))
        self.worker.finished.connect(lambda: self.toGPSLog('Stopping GPS Logging...'))
        self.worker.start()

    def setupGraph1(self):
        pass

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
        if not self.FPGAMonitor.is_connected():
            self.FPGAMonitor.connect_uart()
            print("Connected!")
            self.FPGATextLog.appendPlainText("Connected!")
        else:
            print("Already connected")
            self.FPGATextLog.appendPlainText("Already connected to FPGA")
    
    @pyqtSlot(bool)
    def pressDisconnectButton(self):
        """
        Press the Disconnect Button in the Connection Frame
        """
        if (self.FPGAMonitor.is_connected()):
            print("Disconnected!")
            self.FPGATextLog.appendPlainText("Disconnected!")
        else:
            print("Not connected")
            self.FPGATextLog.appendPlainText("Not connected to FPGA")

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
            cmd = self.FPGAMonitor.get_command_by_id(0)
            self.FPGAMonitor.execute_command(cmd, self.FPGAMonitor.Command.READ)
            self.FPGATextLog.appendPlainText(str(cmd))

        # Write REG0
        elif (command == "Write Reg0"):
            self.FPGATextLog.appendPlainText("Sent: " + commandVal + command)
            cmd = self.FPGAMonitor.get_command_by_id(0)
            self.FPGAMonitor.execute_command(cmd, self.FPGAMonitor.Command.WRITE, 
                commandVal.encode('utf-8'))
            self.FPGATextLog.appendPlainText(str(cmd))

        # Read REG1
        elif (command == "Read Reg1"):
            self.FPGATextLog.appendPlainText("Sent: " + command)
            cmd = self.FPGAMonitor.get_command_by_id(1)
            self.FPGAMonitor.execute_command(cmd, self.FPGAMonitor.Command.READ)
            self.FPGATextLog.appendPlainText(str(cmd))

        # Write REG1
        elif (command == "Write Reg1"):
            self.FPGATextLog.appendPlainText("Sent: " + commandVal + command)
            cmd = self.FPGAMonitor.get_command_by_id(1)
            self.FPGAMonitor.execute_command(cmd, self.FPGAMonitor.Command.WRITE,
                commandVal.encode('utf-8'))
            self.FPGATextLog.appendPlainText(str(cmd))
            
        print("Sent: " + commandVal + command)
        # self.FPGATextLog.appendPlainText("Sent: " + commandVal + command)
