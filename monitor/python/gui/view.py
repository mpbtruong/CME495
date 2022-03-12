# Imports ######################################################################
from re import S
import sys

from PyQt5.QtWidgets import QMainWindow

from .MainWindow import Ui_MainWindow

# Globals ######################################################################

# Library ######################################################################
class View(QMainWindow):
    def __init__(self, model, controller):
        super().__init__()

        self._model = model
        self._controller = controller

        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        # connect widgets to controller
        self._ui.ConnectButton.clicked.connect(self._controller.pressConnectButton)
        self._ui.DisconnectButton.clicked.connect(self._controller.pressDisconnectButton)

        # TODO: listen for model event signals to update

    def setupUI(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(490, 663)
