# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/client_Trial/UI/register.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Register(object):
    def setupUi(self, Register):
        Register.setObjectName("Register")
        Register.resize(718, 490)
        self.widget = QtWidgets.QWidget(Register)
        self.widget.setGeometry(QtCore.QRect(60, 80, 541, 311))
        self.widget.setObjectName("widget")
        self.UsernameLineEdit = QtWidgets.QLineEdit(self.widget)
        self.UsernameLineEdit.setGeometry(QtCore.QRect(240, 10, 181, 25))
        self.UsernameLineEdit.setObjectName("UsernameLineEdit")
        self.label_4 = QtWidgets.QLabel(self.widget)
        self.label_4.setGeometry(QtCore.QRect(150, 160, 67, 17))
        self.label_4.setObjectName("label_4")
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setGeometry(QtCore.QRect(150, 110, 67, 17))
        self.label_3.setObjectName("label_3")
        self.ConfirmLineEdit = QtWidgets.QLineEdit(self.widget)
        self.ConfirmLineEdit.setGeometry(QtCore.QRect(240, 160, 181, 25))
        self.ConfirmLineEdit.setObjectName("ConfirmLineEdit")
        self.NicknameLineEdit = QtWidgets.QLineEdit(self.widget)
        self.NicknameLineEdit.setGeometry(QtCore.QRect(240, 60, 181, 25))
        self.NicknameLineEdit.setObjectName("NicknameLineEdit")
        self.RegisterBtn = QtWidgets.QPushButton(self.widget)
        self.RegisterBtn.setGeometry(QtCore.QRect(270, 270, 89, 25))
        self.RegisterBtn.setObjectName("RegisterBtn")
        self.PasswordLineEdit = QtWidgets.QLineEdit(self.widget)
        self.PasswordLineEdit.setGeometry(QtCore.QRect(240, 110, 181, 25))
        self.PasswordLineEdit.setObjectName("PasswordLineEdit")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setGeometry(QtCore.QRect(150, 10, 67, 17))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setGeometry(QtCore.QRect(150, 60, 67, 17))
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Register)
        QtCore.QMetaObject.connectSlotsByName(Register)

    def retranslateUi(self, Register):
        _translate = QtCore.QCoreApplication.translate
        Register.setWindowTitle(_translate("Register", "Dialog"))
        self.label_4.setText(_translate("Register", "确认密码"))
        self.label_3.setText(_translate("Register", "密码"))
        self.RegisterBtn.setText(_translate("Register", "注册"))
        self.label.setText(_translate("Register", "用户名"))
        self.label_2.setText(_translate("Register", "昵称"))


