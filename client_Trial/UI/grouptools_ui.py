# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/client_Trial/UI/grouptools.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_GroupTools(object):
    def setupUi(self, GroupTools):
        GroupTools.setObjectName("GroupTools")
        GroupTools.resize(220, 270)
        self.verticalLayoutWidget = QtWidgets.QWidget(GroupTools)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(30, 30, 160, 218))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.GroupTools_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.GroupTools_2.setContentsMargins(0, 0, 0, 0)
        self.GroupTools_2.setObjectName("GroupTools_2")
        self.ManagerList = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.ManagerList.setObjectName("ManagerList")
        self.GroupTools_2.addWidget(self.ManagerList)
        self.AddManager = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.AddManager.setObjectName("AddManager")
        self.GroupTools_2.addWidget(self.AddManager)
        self.DecreaseManager = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.DecreaseManager.setObjectName("DecreaseManager")
        self.GroupTools_2.addWidget(self.DecreaseManager)
        self.PeopleGroup = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.PeopleGroup.setObjectName("PeopleGroup")
        self.GroupTools_2.addWidget(self.PeopleGroup)
        self.AddPeople = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.AddPeople.setObjectName("AddPeople")
        self.GroupTools_2.addWidget(self.AddPeople)
        self.DecreasePeople = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.DecreasePeople.setObjectName("DecreasePeople")
        self.GroupTools_2.addWidget(self.DecreasePeople)

        self.retranslateUi(GroupTools)
        QtCore.QMetaObject.connectSlotsByName(GroupTools)

    def retranslateUi(self, GroupTools):
        _translate = QtCore.QCoreApplication.translate
        GroupTools.setWindowTitle(_translate("GroupTools", "Dialog"))
        self.ManagerList.setText(_translate("GroupTools", "管理员名单"))
        self.AddManager.setText(_translate("GroupTools", "添加管理员"))
        self.DecreaseManager.setText(_translate("GroupTools", "减少管理员 "))
        self.PeopleGroup.setText(_translate("GroupTools", "群成员名单"))
        self.AddPeople.setText(_translate("GroupTools", "添加群成员"))
        self.DecreasePeople.setText(_translate("GroupTools", "移除群成员"))


