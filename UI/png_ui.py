# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/UI/png.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Png(object):
    def setupUi(self, Png):
        Png.setObjectName("Png")
        Png.resize(400, 300)
        self.png = QtWidgets.QLabel(Png)
        self.png.setGeometry(QtCore.QRect(160, 120, 67, 17))
        self.png.setObjectName("png")

        self.retranslateUi(Png)
        QtCore.QMetaObject.connectSlotsByName(Png)

    def retranslateUi(self, Png):
        _translate = QtCore.QCoreApplication.translate
        Png.setWindowTitle(_translate("Png", "Dialog"))
        self.png.setText(_translate("Png", "TextLabel"))


