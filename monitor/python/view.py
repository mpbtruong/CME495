# Imports ######################################################################
import sys, time
from threading import Thread, Lock

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QThread

from MainWindow import Ui_MainWindow

# Globals ######################################################################

# Library ######################################################################
class GraphThread(QThread):
    signal = pyqtSignal(int, int)
    def __init__(self, parent=None):
        super(GraphThread, self).__init__(parent)
        self.xval = 0
        self.yval = 0
    
    def run(self):
        while(1):
            time.sleep(1)
            # self.GraphWidget.plot(xval, yval)
            # self.signal.emit([self.xval, self.yval])
            self.signal.emit(self.xval, self.yval)
            self.xval = self.xval + 1
            self.yval = self.yval + 1

class GPSThread(QThread):
    log = pyqtSignal(str)
    def __init__(self, GPSMonitor, parent=None):
        super(GPSThread, self).__init__(parent)
        self.GPSMonitor = GPSMonitor

    def run(self):
        timeout = 1
        counter = 0

        # Attempt to connect to GPS if not connected
        while not self.GPSMonitor.is_connected():
            time.sleep(timeout)
            print("Attemping to Connect to GPS...")
            self.log.emit("Attemping to Connect to GPS...")
            self.GPSMonitor.connect_uart()
            counter += 1
            if (counter == 5) and (not timeout >= 120):
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
        self.cmdLock = Lock()

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

        self.graph1XVals = []
        self.graph1YVals = []
        # for i in range(3600):
        #     self.graph1XVals.append(i)
        #     self.graph1YVals.append(i)
        self.setupGraph1()

        self.graph2XVals = []
        self.graph2YVals = []
        self.setupGraph2()

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
        """
        Setup Graph 1 used for phase error vs time.
        """
        self.Graph1worker = GraphThread()
        self.Graph1worker.signal.connect(self.plotGraph1)
        self.Graph1worker.started.connect(lambda: print("Start Graph1"))
        self.Graph1worker.finished.connect(lambda: print("End Graph1"))
        self.Graph1worker.start()

    def setupGraph2(self):
        """
        Setup Graph 2 used for DAC (bits) vs time.
        """
        self.Graph2worker = GraphThread()
        self.Graph2worker.signal.connect(self.plotGraph2)
        self.Graph2worker.started.connect(lambda: print("Start Graph2"))
        self.Graph2worker.finished.connect(lambda: print("End Graph2"))
        self.Graph2worker.start()

    def plotGraph1(self, xval, yval):
        """
        Setup Graph 3 used for PID out (bits) vs time.
        """
        # TODO replace with plotGraph wrapper 
        if self.FPGAMonitor.is_connected():
            cmd = self.FPGAMonitor.get_command(self.FPGAMonitor.CMD_127)
            self.executeCommand(cmd, self.FPGAMonitor.Command.READ)
            print(cmd)
            self.graph1YVals.append(cmd.get_read_data())
            self.graph1XVals.append(xval)
            if len(self.graph1XVals) > 100:
                self.graph1XVals = self.graph1XVals[:100]
                self.graph1YVals = self.graph1YVals[:100]
            self.Graph1Widget.plot(self.graph1XVals,  self.graph1YVals)

    def plotGraph2(self, xval, yval):
        # TODO replace with plotGraph wrapper 
        # print(xval)
        # print(yval)
        self.graph2XVals.append(xval)
        self.graph2YVals.append(yval)
        if len(self.graph2XVals) > 100:
            self.graph2XVals = self.graph2XVals[:100]
            self.graph2YVals = self.graph2YVals[:100]
        self.Graph2Widget.plot(self.graph2XVals,  self.graph2YVals)

    def plotGraph(self, graphWidget, xvals, yvals):
        """
        Plots a graph widget with the list of values from xvals and yvals
        """
        graphWidget.plot(xvals, yvals)

    def toGPSLog(self, txt):
        """
        Display a message on the GPS plain text widget.
        """
        self.GPSTextLog.appendPlainText(txt)

    def executeCommand(self, cmd, cmdType, data=None):
        if self.FPGAMonitor.is_connected():
            if (cmdType == self.FPGAMonitor.WRITE):
                self.FPGATextLog.appendPlainText("Sent: " + commandVal + command)
            else:
                self.FPGATextLog.appendPlainText("Sent: " + command)
            self.cmdLock.acquire()
            self.FPGAMonitor.execute_command(cmd, cmdType, data)
            self.cmdLock.release()
            self.FPGATextLog.appendPlainText(str(cmd))
        else:
            print("Not Connected")

    @pyqtSlot(bool)
    def pressConnectButton(self):
        """
        Press the Connect Button in the Connection Frame
        """
        if not self.FPGAMonitor.is_connected():
            self.FPGAMonitor.connect_uart()
            if self.FPGAMonitor.is_connected():
                print("Connected!")
                self.FPGATextLog.appendPlainText("Connected to FPGA!")
            else:
                self.FPGATextLog.appendPlainText("Failed to connect to FPGA!")
        else:
            print("Already connected")
            self.FPGATextLog.appendPlainText("Already connected to FPGA!")
    
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
            cmd = self.FPGAMonitor.get_command_by_id(0)
            # self.FPGAMonitor.execute_command(cmd, self.FPGAMonitor.Command.READ)
            self.executeCommand(cmd, self.FPGAMonitor.Command.READ)

        # Write REG0
        elif (command == "Write Reg0"):
            cmd = self.FPGAMonitor.get_command_by_id(0)
            # self.FPGAMonitor.execute_command(cmd, self.FPGAMonitor.Command.WRITE, 
            #     commandVal.encode('utf-8'))
            self.execute_command(cmd, self.FPGAMonitor.Command.WRITE, commandVal.encode('utf-8'))

        # # Read REG1
        # elif (command == "Read Reg1"):
        #     self.FPGATextLog.appendPlainText("Sent: " + command)
        #     cmd = self.FPGAMonitor.get_command_by_id(1)
        #     self.FPGAMonitor.execute_command(cmd, self.FPGAMonitor.Command.READ)
        #     self.FPGATextLog.appendPlainText(str(cmd))

        # # Write REG1
        # elif (command == "Write Reg1"):
        #     self.FPGATextLog.appendPlainText("Sent: " + commandVal + command)
        #     cmd = self.FPGAMonitor.get_command_by_id(1)
        #     self.FPGAMonitor.execute_command(cmd, self.FPGAMonitor.Command.WRITE,
        #         commandVal.encode('utf-8'))
        #     self.FPGATextLog.appendPlainText(str(cmd))
            
        print("Sent: " + commandVal + command)
        # self.FPGATextLog.appendPlainText("Sent: " + commandVal + command)
