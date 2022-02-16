# Imports ######################################################################
from PyQt5 import QtCore, QtGui, QtWidgets

# Globals ######################################################################


# Library ######################################################################
class View(QMainWindow):
    def __init__(self, model, controller):
        super().__init__()

        self.model = model
        self.controller = controller

# Main #########################################################################
def main():
    pass

if __name__ == '__main__':
    main()
