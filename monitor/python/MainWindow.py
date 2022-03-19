# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import PlotWidget, plot, graphicsItems


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1260, 990)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.Graph1Frame = QtWidgets.QFrame(self.centralwidget)
        self.Graph1Frame.setGeometry(QtCore.QRect(0, 410, 620, 291))
        self.Graph1Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Graph1Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Graph1Frame.setObjectName("Graph1Frame")
        self.Graph1Label = QtWidgets.QLabel(self.Graph1Frame)
        self.Graph1Label.setGeometry(QtCore.QRect(10, 10, 47, 13))
        self.Graph1Label.setObjectName("Graph1Label")
        self.Graph1Widget = PlotWidget(self.Graph1Frame)
        self.Graph1Widget.setObjectName('Graph1')
        self.Graph1Widget.setGeometry(QtCore.QRect(10, 30, 620, 251))
        self.Graph1Widget.setBackground('w')
        # time = [1,2,3,4,5,6,7,8,9,10]
        # voltage = [30,32,34,32,33,31,29,32,35,45]
        # self.Graph1Widget.plot(time, voltage)

        self.Graph2Frame = QtWidgets.QFrame(self.centralwidget)
        self.Graph2Frame.setGeometry(QtCore.QRect(0, 690, 620, 291))
        self.Graph2Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Graph2Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Graph2Frame.setObjectName("Graph2Frame")
        self.Graph2Label = QtWidgets.QLabel(self.Graph2Frame)
        self.Graph2Label.setGeometry(QtCore.QRect(10, 10, 47, 13))
        self.Graph2Label.setObjectName("Graph2Label")
        self.Graph2Widget = PlotWidget(self.Graph2Frame)
        self.Graph2Widget.setObjectName('Graph2')
        self.Graph2Widget.setGeometry(QtCore.QRect(10, 30, 620, 251))
        self.Graph2Widget.setBackground('w')

        self.Graph3Frame = QtWidgets.QFrame(self.centralwidget)
        self.Graph3Frame.setGeometry(QtCore.QRect(630, 410, 620, 291))
        self.Graph3Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Graph3Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Graph3Frame.setObjectName("Graph3Frame")
        self.Graph3Label = QtWidgets.QLabel(self.Graph3Frame)
        self.Graph3Label.setGeometry(QtCore.QRect(10, 10, 47, 13))
        self.Graph3Label.setObjectName("Graph3Label")
        self.Graph3Widget = PlotWidget(self.Graph3Frame)
        self.Graph3Widget.setObjectName('Graph3')
        self.Graph3Widget.setGeometry(QtCore.QRect(10, 30, 620, 251))
        self.Graph3Widget.setBackground('w')

        self.Graph4Frame = QtWidgets.QFrame(self.centralwidget)
        self.Graph4Frame.setGeometry(QtCore.QRect(630, 690, 620, 291))
        self.Graph4Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Graph4Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Graph4Frame.setObjectName("Graph4Frame")
        self.Graph4Label = QtWidgets.QLabel(self.Graph4Frame)
        self.Graph4Label.setGeometry(QtCore.QRect(10, 10, 47, 13))
        self.Graph4Label.setObjectName("Graph4Label")
        self.Graph4Widget = PlotWidget(self.Graph4Frame)
        self.Graph4Widget.setObjectName('Graph4')
        self.Graph4Widget.setGeometry(QtCore.QRect(10, 30, 620, 251))
        self.Graph4Widget.setBackground('w')
        
        self.GPSFrame = QtWidgets.QFrame(self.centralwidget)
        self.GPSFrame.setGeometry(QtCore.QRect(0, 130, 600, 291))
        self.GPSFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.GPSFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.GPSFrame.setObjectName("GPSFrame")
        self.GPSTextLog = QtWidgets.QPlainTextEdit(self.GPSFrame)
        self.GPSTextLog.setGeometry(QtCore.QRect(10, 30, 590, 251))
        self.GPSTextLog.setObjectName("GPSTextLog")
        self.GPSTextLog.setReadOnly(True)
        self.GPSLabel = QtWidgets.QLabel(self.GPSFrame)
        self.GPSLabel.setGeometry(QtCore.QRect(10, 10, 47, 13))
        self.GPSLabel.setObjectName("GPSLabel")

        self.FPGAFrame = QtWidgets.QFrame(self.centralwidget)
        self.FPGAFrame.setGeometry(QtCore.QRect(610, 130, 600, 291))
        self.FPGAFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FPGAFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FPGAFrame.setObjectName("FPGAFrame")
        self.FPGATextLog = QtWidgets.QPlainTextEdit(self.FPGAFrame)
        self.FPGATextLog.setGeometry(QtCore.QRect(10, 30, 590, 251))
        self.FPGATextLog.setObjectName("FPGATextLog")
        self.FPGATextLog.setReadOnly(True)
        self.FPGALabel = QtWidgets.QLabel(self.FPGAFrame)
        self.FPGALabel.setGeometry(QtCore.QRect(10, 10, 47, 13))
        self.FPGALabel.setObjectName("FPGALabel")

        self.ConnectFrame = QtWidgets.QFrame(self.centralwidget)
        self.ConnectFrame.setGeometry(QtCore.QRect(500, 20, 101, 91))
        self.ConnectFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ConnectFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ConnectFrame.setObjectName("ConnectFrame")
        self.ConnectionLabel = QtWidgets.QLabel(self.ConnectFrame)
        self.ConnectionLabel.setGeometry(QtCore.QRect(10, 10, 101, 16))
        self.ConnectionLabel.setObjectName("ConnectionLabel")
        self.ConnectButton = QtWidgets.QPushButton(self.ConnectFrame)
        self.ConnectButton.setGeometry(QtCore.QRect(10, 30, 75, 23))
        self.ConnectButton.setObjectName("ConnectButton")
        self.DisconnectButton = QtWidgets.QPushButton(self.ConnectFrame)
        self.DisconnectButton.setGeometry(QtCore.QRect(10, 60, 75, 23))
        self.DisconnectButton.setObjectName("DisconnectButton")

        self.CommandFrame = QtWidgets.QFrame(self.centralwidget)
        self.CommandFrame.setGeometry(QtCore.QRect(10, 19, 500, 91))
        self.CommandFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.CommandFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.CommandFrame.setObjectName("CommandFrame")
        self.CommandLabel = QtWidgets.QLabel(self.CommandFrame)
        self.CommandLabel.setGeometry(QtCore.QRect(10, 10, 81, 16))
        self.CommandLabel.setObjectName("CommandLabel")
        self.CommandTextInput = QtWidgets.QPlainTextEdit(self.CommandFrame)
        self.CommandTextInput.setGeometry(QtCore.QRect(10, 30, 150, 31))
        self.CommandTextInput.setObjectName("CommandTextInput")
        self.CommandComboBox = QtWidgets.QComboBox(self.CommandFrame)
        self.CommandComboBox.setGeometry(QtCore.QRect(160, 30, 150, 31))
        self.CommandComboBox.setObjectName("CommandComboBox")
        self.CommandComboLabel = QtWidgets.QLabel(self.CommandFrame)
        self.CommandComboLabel.setGeometry(QtCore.QRect(160, 10, 81, 16))
        self.CommandComboLabel.setObjectName("CommandComboLabel")
        self.CommandButton = QtWidgets.QPushButton(self.CommandFrame)
        self.CommandButton.setGeometry(QtCore.QRect(310, 30, 75, 31))
        self.CommandButton.setObjectName("CommandButton")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Graph1Label.setText(_translate("MainWindow", "Phase Error vs Time"))
        self.Graph2Label.setText(_translate("MainWindow", "DAC vs Time"))
        self.Graph3Label.setText(_translate("MainWindow", "PID vs Time"))
        # self.Graph4Label.setText(_translate("MainWindow", "Graph4"))
        self.GPSLabel.setText(_translate("MainWindow", "GPS"))
        self.FPGALabel.setText(_translate("MainWindow", "FPGA"))
        self.ConnectionLabel.setText(_translate("MainWindow", "FPGA Connection"))
        self.ConnectButton.setText(_translate("MainWindow", "Connect"))
        self.DisconnectButton.setText(_translate("MainWindow", "Disconnect"))
        self.CommandLabel.setText(_translate("MainWindow", "Write Value"))
        self.CommandComboLabel.setText(_translate("MainWindow", "Command List"))
        self.CommandButton.setText(_translate("MainWindow", "Enter CMD"))
