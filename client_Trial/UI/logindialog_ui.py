# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/client_Trial/logindialog.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName("LoginDialog")
        LoginDialog.resize(651, 368)
        self.label = QtWidgets.QLabel(LoginDialog)
        self.label.setGeometry(QtCore.QRect(60, 180, 81, 24))
        font = QtGui.QFont()
        font.setFamily("Noto Sans CJK SC")
        font.setItalic(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.pwdLineEdit = QtWidgets.QLineEdit(LoginDialog)
        self.pwdLineEdit.setGeometry(QtCore.QRect(170, 230, 321, 32))
        self.pwdLineEdit.setText("")
        self.pwdLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pwdLineEdit.setObjectName("pwdLineEdit")
        self.exitBtn = QtWidgets.QPushButton(LoginDialog)
        self.exitBtn.setGeometry(QtCore.QRect(450, 290, 97, 32))
        self.exitBtn.setObjectName("exitBtn")
        self.label_2 = QtWidgets.QLabel(LoginDialog)
        self.label_2.setGeometry(QtCore.QRect(60, 230, 72, 24))
        font = QtGui.QFont()
        font.setFamily("Noto Sans CJK SC")
        font.setItalic(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.loginBtn = QtWidgets.QPushButton(LoginDialog)
        self.loginBtn.setGeometry(QtCore.QRect(90, 290, 97, 32))
        self.loginBtn.setObjectName("loginBtn")
        self.usrLineEdit = QtWidgets.QLineEdit(LoginDialog)
        self.usrLineEdit.setGeometry(QtCore.QRect(170, 180, 321, 32))
        self.usrLineEdit.setObjectName("usrLineEdit")
        self.registerBtn = QtWidgets.QPushButton(LoginDialog)
        self.registerBtn.setGeometry(QtCore.QRect(270, 290, 91, 31))
        self.registerBtn.setObjectName("registerBtn")
        self.faceBtn = QtWidgets.QPushButton(LoginDialog)
        self.faceBtn.setGeometry(QtCore.QRect(510, 230, 89, 31))
        self.faceBtn.setObjectName("faceBtn")
        self.label_3 = QtWidgets.QLabel(LoginDialog)
        self.label_3.setGeometry(QtCore.QRect(100, 40, 441, 101))
        self.label_3.setObjectName("label_3")

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
        self.registerBtn.setText(_translate("LoginDialog", "Register"))
        self.faceBtn.setText(_translate("LoginDialog", "人脸"))
        self.label_3.setText(_translate("LoginDialog", "TITLE"))


