# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/client_Trial/createGroupDialog.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_createGroupDialog(object):
    def setupUi(self, createGroupDialog):
        createGroupDialog.setObjectName("createGroupDialog")
        createGroupDialog.resize(358, 156)
        self.horizontalLayout = QtWidgets.QHBoxLayout(createGroupDialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget_2 = QtWidgets.QWidget(createGroupDialog)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget_3 = QtWidgets.QWidget(self.widget_2)
        self.widget_3.setObjectName("widget_3")
        self.verticalLayout.addWidget(self.widget_3)
        self.lineEdit = QtWidgets.QLineEdit(self.widget_2)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.widget_4 = QtWidgets.QWidget(self.widget_2)
        self.widget_4.setObjectName("widget_4")
        self.verticalLayout.addWidget(self.widget_4)
        self.widget = QtWidgets.QWidget(self.widget_2)
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.widget_6 = QtWidgets.QWidget(self.widget)
        self.widget_6.setObjectName("widget_6")
        self.horizontalLayout_2.addWidget(self.widget_6)
        self.confirmBtn = QtWidgets.QPushButton(self.widget)
        self.confirmBtn.setObjectName("confirmBtn")
        self.horizontalLayout_2.addWidget(self.confirmBtn)
        self.widget_5 = QtWidgets.QWidget(self.widget)
        self.widget_5.setObjectName("widget_5")
        self.horizontalLayout_2.addWidget(self.widget_5)
        self.exitBtn = QtWidgets.QPushButton(self.widget)
        self.exitBtn.setObjectName("exitBtn")
        self.horizontalLayout_2.addWidget(self.exitBtn)
        self.widget_7 = QtWidgets.QWidget(self.widget)
        self.widget_7.setObjectName("widget_7")
        self.horizontalLayout_2.addWidget(self.widget_7)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 5)
        self.horizontalLayout_2.setStretch(2, 4)
        self.horizontalLayout_2.setStretch(3, 5)
        self.horizontalLayout_2.setStretch(4, 1)
        self.verticalLayout.addWidget(self.widget)
        self.horizontalLayout.addWidget(self.widget_2)
        self.horizontalLayout.setStretch(0, 3)

        self.retranslateUi(createGroupDialog)
        QtCore.QMetaObject.connectSlotsByName(createGroupDialog)

    def retranslateUi(self, createGroupDialog):
        _translate = QtCore.QCoreApplication.translate
        createGroupDialog.setWindowTitle(_translate("createGroupDialog", "Dialog"))
        self.lineEdit.setPlaceholderText(_translate("createGroupDialog", "Edit GourpName"))
        self.confirmBtn.setText(_translate("createGroupDialog", "I AM OWNER!"))
        self.exitBtn.setText(_translate("createGroupDialog", "never mind"))


