# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/UI/changepeople.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ChangePeople(object):
    def setupUi(self, ChangePeople):
        ChangePeople.setObjectName("ChangePeople")
        ChangePeople.resize(400, 207)
        self.ExecuteBtn = QtWidgets.QPushButton(ChangePeople)
        self.ExecuteBtn.setGeometry(QtCore.QRect(260, 140, 89, 25))
        self.ExecuteBtn.setObjectName("ExecuteBtn")
        self.label = QtWidgets.QLabel(ChangePeople)
        self.label.setGeometry(QtCore.QRect(170, 70, 67, 17))
        self.label.setObjectName("label")
        self.UserId = QtWidgets.QLineEdit(ChangePeople)
        self.UserId.setGeometry(QtCore.QRect(240, 70, 113, 25))
        self.UserId.setObjectName("UserId")
        self.Choice = QtWidgets.QComboBox(ChangePeople)
        self.Choice.setGeometry(QtCore.QRect(30, 70, 111, 25))
        self.Choice.setObjectName("Choice")
        self.Choice.addItem("")
        self.Choice.addItem("")

        self.retranslateUi(ChangePeople)
        QtCore.QMetaObject.connectSlotsByName(ChangePeople)

    def retranslateUi(self, ChangePeople):
        _translate = QtCore.QCoreApplication.translate
        ChangePeople.setWindowTitle(_translate("ChangePeople", "Dialog"))
        self.ExecuteBtn.setText(_translate("ChangePeople", "执行"))
        self.label.setText(_translate("ChangePeople", "用户名"))
        self.Choice.setItemText(0, _translate("ChangePeople", "减少群成员"))
        self.Choice.setItemText(1, _translate("ChangePeople", "添加群成员"))


