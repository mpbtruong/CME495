# Imports ######################################################################
from re import T
from PyQt5.QtCore import QObject, pyqtSlot

# Globals ######################################################################


# Library ######################################################################
class Controller(QObject):
    def __init__(self, model):
        super().__init__()

        self._model = model

    @pyqtSlot(bool)
    def pressConnectButton(self):
        """
        Press the Connect Button in the Connection Frame
        """
        # TODO
        self._model.connectStatus = True
        print("Connected!")
    
    @pyqtSlot(bool)
    def pressDisconnectButton(self):
        """
        Press the Disconnect Button in the Connection Frame
        """
        # TODO
        self._model.connectStatus = False
        print("Disconnected!")

    @pyqtSlot(int)
    def sendCommand(self, commandNum):
        """
        Send a command to the FPGA
        """
        # TODDO
        print("Sent: " + commandNum)
