# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/UI/register.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Register(object):
    def setupUi(self, Register):
        Register.setObjectName("Register")
        Register.resize(400, 300)
        self.RegisterBtn = QtWidgets.QPushButton(Register)
        self.RegisterBtn.setGeometry(QtCore.QRect(160, 240, 89, 25))
        self.RegisterBtn.setObjectName("RegisterBtn")
        self.label = QtWidgets.QLabel(Register)
        self.label.setGeometry(QtCore.QRect(40, 30, 67, 17))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Register)
        self.label_2.setGeometry(QtCore.QRect(40, 80, 67, 17))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Register)
        self.label_3.setGeometry(QtCore.QRect(40, 130, 67, 17))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Register)
        self.label_4.setGeometry(QtCore.QRect(40, 180, 67, 17))
        self.label_4.setObjectName("label_4")
        self.UsernameLineEdit = QtWidgets.QLineEdit(Register)
        self.UsernameLineEdit.setGeometry(QtCore.QRect(130, 30, 181, 25))
        self.UsernameLineEdit.setObjectName("UsernameLineEdit")
        self.NicknameLineEdit = QtWidgets.QLineEdit(Register)
        self.NicknameLineEdit.setGeometry(QtCore.QRect(130, 80, 181, 25))
        self.NicknameLineEdit.setObjectName("NicknameLineEdit")
        self.PasswordLineEdit = QtWidgets.QLineEdit(Register)
        self.PasswordLineEdit.setGeometry(QtCore.QRect(130, 130, 181, 25))
        self.PasswordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.PasswordLineEdit.setObjectName("PasswordLineEdit")
        self.ConfirmLineEdit = QtWidgets.QLineEdit(Register)
        self.ConfirmLineEdit.setGeometry(QtCore.QRect(130, 180, 181, 25))
        self.ConfirmLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ConfirmLineEdit.setObjectName("ConfirmLineEdit")

        self.retranslateUi(Register)
        QtCore.QMetaObject.connectSlotsByName(Register)

    def retranslateUi(self, Register):
        _translate = QtCore.QCoreApplication.translate
        Register.setWindowTitle(_translate("Register", "Dialog"))
        self.RegisterBtn.setText(_translate("Register", "注册"))
        self.label.setText(_translate("Register", "用户名"))
        self.label_2.setText(_translate("Register", "昵称"))
        self.label_3.setText(_translate("Register", "密码"))
        self.label_4.setText(_translate("Register", "确认密码"))


