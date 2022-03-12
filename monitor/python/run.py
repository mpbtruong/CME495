# Imports ######################################################################
from ast import Mod
import subprocess
import sys

from PyQt5.QtWidgets import QApplication

from gui.controller import Controller
from gui.model import Model
from gui.view import View


# Globals ######################################################################


# Library ######################################################################
def setup():
    """
    Install packages needed.

    pip3 install pipreqs
    pipreqs .

    pip3 install -r requirements.txt

    TODO: IMPLEMENT ME
    """
    pass

# Main #########################################################################
def main():
    """
    Main entrance point to the monitor/controller.
    """
    try:
        app = QApplication(sys.argv)
        model = Model()
        controller = Controller(model)
        view = View(model, controller)
        # setup the client GUI
        view.show()
        rc = app.exec_()
        sys.exit(rc)
        # sys.exit(app.exec_())
    # kill the subscriber
    except KeyboardInterrupt:
        print(f'Stopped!')

if __name__ == '__main__':
    main()
