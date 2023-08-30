# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/UI/Voicecall.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Voicecall(object):
    def setupUi(self, Voicecall):
        Voicecall.setObjectName("Voicecall")
        Voicecall.resize(355, 241)
        self.DownBtn = QtWidgets.QPushButton(Voicecall)
        self.DownBtn.setGeometry(QtCore.QRect(150, 150, 51, 51))
        self.DownBtn.setMinimumSize(QtCore.QSize(0, 0))
        self.DownBtn.setMaximumSize(QtCore.QSize(99, 99))
        self.DownBtn.setSizeIncrement(QtCore.QSize(99, 99))
        self.DownBtn.setBaseSize(QtCore.QSize(99, 99))
        self.DownBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.DownBtn.setObjectName("DownBtn")
        self.name = QtWidgets.QLabel(Voicecall)
        self.name.setGeometry(QtCore.QRect(20, 20, 81, 17))
        self.name.setObjectName("name")

        self.retranslateUi(Voicecall)
        QtCore.QMetaObject.connectSlotsByName(Voicecall)

    def retranslateUi(self, Voicecall):
        _translate = QtCore.QCoreApplication.translate
        Voicecall.setWindowTitle(_translate("Voicecall", "语音通话"))
        self.DownBtn.setText(_translate("Voicecall", "挂断"))
        self.name.setText(_translate("Voicecall", "对方的名字"))


