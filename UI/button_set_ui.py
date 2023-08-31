# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/UI/button_set.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(714, 444)
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(140, 120, 160, 120))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.chatBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.chatBtn.setObjectName("chatBtn")
        self.verticalLayout.addWidget(self.chatBtn)
        self.friendBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.friendBtn.setObjectName("friendBtn")
        self.verticalLayout.addWidget(self.friendBtn)
        self.groupBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.groupBtn.setObjectName("groupBtn")
        self.verticalLayout.addWidget(self.groupBtn)
        self.add_friendBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.add_friendBtn.setObjectName("add_friendBtn")
        self.verticalLayout.addWidget(self.add_friendBtn)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.chatBtn.setText(_translate("Dialog", "chat"))
        self.friendBtn.setText(_translate("Dialog", "friend"))
        self.groupBtn.setText(_translate("Dialog", "group"))
        self.add_friendBtn.setText(_translate("Dialog", "add friend"))


