# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/UI/managerlist.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ManagerList(object):
    def setupUi(self, ManagerList):
        ManagerList.setObjectName("ManagerList")
        ManagerList.resize(400, 300)
        self.Manager = QtWidgets.QListWidget(ManagerList)
        self.Manager.setGeometry(QtCore.QRect(0, 0, 401, 301))
        self.Manager.setObjectName("Manager")

        self.retranslateUi(ManagerList)
        QtCore.QMetaObject.connectSlotsByName(ManagerList)

    def retranslateUi(self, ManagerList):
        _translate = QtCore.QCoreApplication.translate
        ManagerList.setWindowTitle(_translate("ManagerList", "Dialog"))


