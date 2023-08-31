# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/UI/changemanager.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ChangeManager(object):
    def setupUi(self, ChangeManager):
        ChangeManager.setObjectName("ChangeManager")
        ChangeManager.resize(400, 184)
        self.UserId = QtWidgets.QLineEdit(ChangeManager)
        self.UserId.setGeometry(QtCore.QRect(230, 50, 113, 25))
        self.UserId.setObjectName("UserId")
        self.ExecuteBtn = QtWidgets.QPushButton(ChangeManager)
        self.ExecuteBtn.setGeometry(QtCore.QRect(250, 120, 89, 25))
        self.ExecuteBtn.setObjectName("ExecuteBtn")
        self.label = QtWidgets.QLabel(ChangeManager)
        self.label.setGeometry(QtCore.QRect(160, 50, 67, 17))
        self.label.setObjectName("label")
        self.Choice = QtWidgets.QComboBox(ChangeManager)
        self.Choice.setGeometry(QtCore.QRect(20, 50, 111, 25))
        self.Choice.setObjectName("Choice")
        self.Choice.addItem("")
        self.Choice.addItem("")

        self.retranslateUi(ChangeManager)
        QtCore.QMetaObject.connectSlotsByName(ChangeManager)

    def retranslateUi(self, ChangeManager):
        _translate = QtCore.QCoreApplication.translate
        ChangeManager.setWindowTitle(_translate("ChangeManager", "Dialog"))
        self.ExecuteBtn.setText(_translate("ChangeManager", "执行"))
        self.label.setText(_translate("ChangeManager", "用户名"))
        self.Choice.setItemText(0, _translate("ChangeManager", "减少管理员"))
        self.Choice.setItemText(1, _translate("ChangeManager", "添加管理员"))


