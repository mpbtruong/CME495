# Imports ######################################################################
from ast import Mod
import subprocess
import sys

from PyQt5.QtWidgets import QApplication

from MonitorFPGA import MonitorFPGA
from MonitorGPSReceiver import MonitorGPSReceiver
from MonitorConfigUART import *
from view import View


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
        FPGAMonitor = MonitorFPGA()
        GPSMonitor = MonitorGPSReceiver()
        print(FPGAMonitor)
        print(GPSMonitor)
        app = QApplication(sys.argv)
        view = View(FPGAMonitor, GPSMonitor)
        # setup the client GUI
        view.show()
        rc = app.exec_()
        sys.exit(rc)
        # sys.exit(app.exec_())
    # kill the subscriber
    except KeyboardInterrupt:
        print('Stopped!')

if __name__ == '__main__':
    main()
