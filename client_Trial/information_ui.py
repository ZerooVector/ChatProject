# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/client_Trial/information.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Information(object):
    def setupUi(self, Information):
        Information.setObjectName("Information")
        Information.resize(400, 300)
        self.label = QtWidgets.QLabel(Information)
        self.label.setGeometry(QtCore.QRect(30, 50, 67, 17))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Information)
        self.label_2.setGeometry(QtCore.QRect(30, 90, 67, 17))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Information)
        self.label_3.setGeometry(QtCore.QRect(30, 130, 67, 17))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Information)
        self.label_4.setGeometry(QtCore.QRect(30, 170, 67, 17))
        self.label_4.setObjectName("label_4")
        self.GoBtn = QtWidgets.QPushButton(Information)
        self.GoBtn.setGeometry(QtCore.QRect(160, 220, 89, 25))
        self.GoBtn.setObjectName("GoBtn")
        self.ChangeNickname = QtWidgets.QLineEdit(Information)
        self.ChangeNickname.setGeometry(QtCore.QRect(122, 50, 161, 25))
        self.ChangeNickname.setObjectName("ChangeNickname")
        self.OldPassword = QtWidgets.QLineEdit(Information)
        self.OldPassword.setGeometry(QtCore.QRect(120, 90, 161, 25))
        self.OldPassword.setObjectName("OldPassword")
        self.NewPassword = QtWidgets.QLineEdit(Information)
        self.NewPassword.setGeometry(QtCore.QRect(122, 130, 161, 25))
        self.NewPassword.setObjectName("NewPassword")
        self.ConfirmLineEdit = QtWidgets.QLineEdit(Information)
        self.ConfirmLineEdit.setGeometry(QtCore.QRect(120, 170, 161, 25))
        self.ConfirmLineEdit.setObjectName("ConfirmLineEdit")

        self.retranslateUi(Information)
        QtCore.QMetaObject.connectSlotsByName(Information)

    def retranslateUi(self, Information):
        _translate = QtCore.QCoreApplication.translate
        Information.setWindowTitle(_translate("Information", "Dialog"))
        self.label.setText(_translate("Information", "昵称"))
        self.label_2.setText(_translate("Information", "旧密码"))
        self.label_3.setText(_translate("Information", "新密码"))
        self.label_4.setText(_translate("Information", "确认密码"))
        self.GoBtn.setText(_translate("Information", "确认修改"))


