# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'remote_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        MainWindow.setMinimumSize(QtCore.QSize(1920, 1080))
        MainWindow.setMouseTracking(True)
        self.remote_window = QtWidgets.QWidget(MainWindow)
        self.remote_window.setMinimumSize(QtCore.QSize(1920, 1080))
        self.remote_window.setMouseTracking(True)
        self.remote_window.setObjectName("remote_window")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.remote_window)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 1922, 1082))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.display_label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.display_label.setMinimumSize(QtCore.QSize(1920, 1080))
        self.display_label.setMouseTracking(True)
        self.display_label.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.display_label.setStyleSheet("QLabel{\n"
"    border: 1px solid red;\n"
"}")
        self.display_label.setText("")
        self.display_label.setObjectName("display_label")
        self.horizontalLayout.addWidget(self.display_label)
        MainWindow.setCentralWidget(self.remote_window)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))