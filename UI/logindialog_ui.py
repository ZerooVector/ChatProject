# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/UI/logindialog.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName("LoginDialog")
<<<<<<< HEAD
        LoginDialog.setEnabled(True)
        LoginDialog.resize(651, 651)
        LoginDialog.setAcceptDrops(False)
        LoginDialog.setAccessibleDescription("")
        self.label = QtWidgets.QLabel(LoginDialog)
        self.label.setGeometry(QtCore.QRect(60, 290, 81, 24))
=======
        LoginDialog.resize(651, 309)
        self.label = QtWidgets.QLabel(LoginDialog)
        self.label.setGeometry(QtCore.QRect(70, 100, 81, 24))
>>>>>>> origin/main
        font = QtGui.QFont()
        font.setFamily("Noto Sans CJK SC")
        font.setItalic(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.pwdLineEdit = QtWidgets.QLineEdit(LoginDialog)
<<<<<<< HEAD
        self.pwdLineEdit.setGeometry(QtCore.QRect(170, 420, 321, 32))
=======
        self.pwdLineEdit.setGeometry(QtCore.QRect(180, 150, 321, 32))
>>>>>>> origin/main
        self.pwdLineEdit.setText("")
        self.pwdLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pwdLineEdit.setObjectName("pwdLineEdit")
        self.exitBtn = QtWidgets.QPushButton(LoginDialog)
<<<<<<< HEAD
        self.exitBtn.setGeometry(QtCore.QRect(450, 530, 97, 32))
        self.exitBtn.setObjectName("exitBtn")
        self.label_2 = QtWidgets.QLabel(LoginDialog)
        self.label_2.setGeometry(QtCore.QRect(60, 420, 72, 24))
=======
        self.exitBtn.setGeometry(QtCore.QRect(460, 210, 97, 32))
        self.exitBtn.setObjectName("exitBtn")
        self.label_2 = QtWidgets.QLabel(LoginDialog)
        self.label_2.setGeometry(QtCore.QRect(70, 150, 72, 24))
>>>>>>> origin/main
        font = QtGui.QFont()
        font.setFamily("Noto Sans CJK SC")
        font.setItalic(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.loginBtn = QtWidgets.QPushButton(LoginDialog)
<<<<<<< HEAD
        self.loginBtn.setGeometry(QtCore.QRect(80, 530, 97, 32))
        self.loginBtn.setAutoDefault(True)
        self.loginBtn.setObjectName("loginBtn")
        self.usrLineEdit = QtWidgets.QLineEdit(LoginDialog)
        self.usrLineEdit.setGeometry(QtCore.QRect(170, 290, 321, 32))
        self.usrLineEdit.setObjectName("usrLineEdit")
        self.registerBtn = QtWidgets.QPushButton(LoginDialog)
        self.registerBtn.setGeometry(QtCore.QRect(260, 530, 91, 31))
        self.registerBtn.setObjectName("registerBtn")
        self.faceBtn = QtWidgets.QPushButton(LoginDialog)
        self.faceBtn.setEnabled(True)
        self.faceBtn.setGeometry(QtCore.QRect(510, 420, 89, 31))
        self.faceBtn.setObjectName("faceBtn")
        self.label_3 = QtWidgets.QLabel(LoginDialog)
        self.label_3.setGeometry(QtCore.QRect(100, 100, 441, 101))
        self.label_3.setObjectName("label_3")

        self.retranslateUi(LoginDialog)
=======
        self.loginBtn.setGeometry(QtCore.QRect(100, 210, 97, 32))
        self.loginBtn.setObjectName("loginBtn")
        self.usrLineEdit = QtWidgets.QLineEdit(LoginDialog)
        self.usrLineEdit.setGeometry(QtCore.QRect(180, 100, 321, 32))
        self.usrLineEdit.setObjectName("usrLineEdit")
        self.registerBtn = QtWidgets.QPushButton(LoginDialog)
        self.registerBtn.setGeometry(QtCore.QRect(280, 210, 91, 31))
        self.registerBtn.setObjectName("registerBtn")

        self.retranslateUi(LoginDialog)
        self.exitBtn.clicked.connect(LoginDialog.close)
>>>>>>> origin/main
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)

    def retranslateUi(self, LoginDialog):
        _translate = QtCore.QCoreApplication.translate
        LoginDialog.setWindowTitle(_translate("LoginDialog", "Dialog"))
        self.label.setText(_translate("LoginDialog", "UserName"))
        self.pwdLineEdit.setPlaceholderText(_translate("LoginDialog", "请输入密码"))
        self.exitBtn.setText(_translate("LoginDialog", ""))
        self.label_2.setText(_translate("LoginDialog", "Password"))
        self.loginBtn.setText(_translate("LoginDialog", ""))
        self.usrLineEdit.setPlaceholderText(_translate("LoginDialog", "请输入用户名"))
<<<<<<< HEAD
        self.registerBtn.setText(_translate("LoginDialog", ""))
        self.faceBtn.setText(_translate("LoginDialog", ""))
        self.label_3.setText(_translate("LoginDialog", "TITLE"))
=======
        self.registerBtn.setText(_translate("LoginDialog", "Register"))


>>>>>>> origin/main
