# Imports ######################################################################
from PyQt5.QtCore import QObject, pyqtSignal

# Globals ######################################################################


# Library ######################################################################
class Model(QObject):
    # TODO: Add model variables (buttons?)

    def __init__(self):
        super().__init__()

        # TODO: set model default values
        self.connectStatus = False
        