# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project/logindialog.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName("LoginDialog")
        LoginDialog.resize(651, 309)
        self.label = QtWidgets.QLabel(LoginDialog)
        self.label.setGeometry(QtCore.QRect(70, 100, 81, 24))
        font = QtGui.QFont()
        font.setFamily("Noto Sans CJK SC")
        font.setItalic(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.pwdLineEdit = QtWidgets.QLineEdit(LoginDialog)
        self.pwdLineEdit.setGeometry(QtCore.QRect(180, 150, 321, 32))
        self.pwdLineEdit.setText("")
        self.pwdLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pwdLineEdit.setObjectName("pwdLineEdit")
        self.exitBtn = QtWidgets.QPushButton(LoginDialog)
        self.exitBtn.setGeometry(QtCore.QRect(250, 260, 97, 32))
        self.exitBtn.setObjectName("exitBtn")
        self.label_2 = QtWidgets.QLabel(LoginDialog)
        self.label_2.setGeometry(QtCore.QRect(70, 150, 72, 24))
        font = QtGui.QFont()
        font.setFamily("Noto Sans CJK SC")
        font.setItalic(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.loginBtn = QtWidgets.QPushButton(LoginDialog)
        self.loginBtn.setGeometry(QtCore.QRect(250, 220, 97, 32))
        self.loginBtn.setObjectName("loginBtn")
        self.usrLineEdit = QtWidgets.QLineEdit(LoginDialog)
        self.usrLineEdit.setGeometry(QtCore.QRect(180, 100, 321, 32))
        self.usrLineEdit.setObjectName("usrLineEdit")

        self.retranslateUi(LoginDialog)
        self.exitBtn.clicked.connect(LoginDialog.close)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)

    def retranslateUi(self, LoginDialog):
        _translate = QtCore.QCoreApplication.translate
        LoginDialog.setWindowTitle(_translate("LoginDialog", "Dialog"))
        self.label.setText(_translate("LoginDialog", "UserName"))
        self.pwdLineEdit.setPlaceholderText(_translate("LoginDialog", "请输入密码"))
        self.exitBtn.setText(_translate("LoginDialog", "Exit"))
        self.label_2.setText(_translate("LoginDialog", "Password"))
        self.loginBtn.setText(_translate("LoginDialog", "Login"))
        self.usrLineEdit.setPlaceholderText(_translate("LoginDialog", "请输入用户名"))


