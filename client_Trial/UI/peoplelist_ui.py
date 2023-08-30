# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/client_Trial/UI/peoplelist.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PeopleList(object):
    def setupUi(self, PeopleList):
        PeopleList.setObjectName("PeopleList")
        PeopleList.resize(400, 300)
        self.People = QtWidgets.QListWidget(PeopleList)
        self.People.setGeometry(QtCore.QRect(0, 0, 401, 301))
        self.People.setObjectName("People")

        self.retranslateUi(PeopleList)
        QtCore.QMetaObject.connectSlotsByName(PeopleList)

    def retranslateUi(self, PeopleList):
        _translate = QtCore.QCoreApplication.translate
        PeopleList.setWindowTitle(_translate("PeopleList", "Dialog"))


