# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jh/code/QtDemo/Project_Github/ChatProject/client_Trial/UI/untitled_test_basic.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(996, 600)
        MainWindow.setStyleSheet("background-color: rgb(227, 202, 165);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 1000, 600))
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setTabBarAutoHide(False)
        self.tabWidget.setObjectName("tabWidget")
        self.chatTab = QtWidgets.QWidget()
        self.chatTab.setObjectName("chatTab")
        self.widget_3 = QtWidgets.QWidget(self.chatTab)
        self.widget_3.setGeometry(QtCore.QRect(0, 0, 841, 561))
        self.widget_3.setObjectName("widget_3")
        self.showMsgPage = QtWidgets.QGroupBox(self.widget_3)
        self.showMsgPage.setGeometry(QtCore.QRect(274, 0, 621, 550))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.showMsgPage.sizePolicy().hasHeightForWidth())
        self.showMsgPage.setSizePolicy(sizePolicy)
        self.showMsgPage.setMinimumSize(QtCore.QSize(200, 150))
        self.showMsgPage.setObjectName("showMsgPage")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.showMsgPage)
        self.horizontalLayout_4.setContentsMargins(10, -1, -1, -1)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.widget = QtWidgets.QWidget(self.showMsgPage)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.chatFuncList = QtWidgets.QListWidget(self.widget)
        self.chatFuncList.setGeometry(QtCore.QRect(0, 320, 631, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(5)
        sizePolicy.setHeightForWidth(self.chatFuncList.sizePolicy().hasHeightForWidth())
        self.chatFuncList.setSizePolicy(sizePolicy)
        self.chatFuncList.setFlow(QtWidgets.QListView.LeftToRight)
        self.chatFuncList.setObjectName("chatFuncList")
        self.chatMsgEdit = QtWidgets.QTextEdit(self.widget)
        self.chatMsgEdit.setGeometry(QtCore.QRect(0, 350, 631, 141))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.chatMsgEdit.sizePolicy().hasHeightForWidth())
        self.chatMsgEdit.setSizePolicy(sizePolicy)
        self.chatMsgEdit.setStyleSheet("background-color: rgb(255, 251, 233);")
        self.chatMsgEdit.setObjectName("chatMsgEdit")
        self.chatSendBtn = QtWidgets.QPushButton(self.widget)
        self.chatSendBtn.setGeometry(QtCore.QRect(450, 440, 97, 32))
        self.chatSendBtn.setObjectName("chatSendBtn")
        self.chatMsgBrowser = QtWidgets.QScrollArea(self.widget)
        self.chatMsgBrowser.setGeometry(QtCore.QRect(0, 0, 551, 321))
        self.chatMsgBrowser.setStyleSheet("\n"
"background-color: rgb(255, 251, 233);")
        self.chatMsgBrowser.setWidgetResizable(True)
        self.chatMsgBrowser.setObjectName("chatMsgBrowser")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 549, 319))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.chatMsgBrowser.setWidget(self.scrollAreaWidgetContents)
        self.pushButton = QtWidgets.QPushButton(self.widget)
        self.pushButton.setGeometry(QtCore.QRect(10, 320, 50, 32))
        self.pushButton.setObjectName("pushButton")
        self.sendFileBtn = QtWidgets.QPushButton(self.widget)
        self.sendFileBtn.setGeometry(QtCore.QRect(80, 320, 97, 32))
        self.sendFileBtn.setObjectName("sendFileBtn")
        self.VoiceCallBtn = QtWidgets.QPushButton(self.widget)
        self.VoiceCallBtn.setGeometry(QtCore.QRect(420, 320, 89, 31))
        self.VoiceCallBtn.setObjectName("VoiceCallBtn")
        self.TransformBtn = QtWidgets.QPushButton(self.widget)
        self.TransformBtn.setGeometry(QtCore.QRect(310, 320, 89, 31))
        self.TransformBtn.setObjectName("TransformBtn")
        self.sendVoiceBtn = QtWidgets.QPushButton(self.widget)
        self.sendVoiceBtn.setGeometry(QtCore.QRect(200, 320, 89, 31))
        self.sendVoiceBtn.setObjectName("sendVoiceBtn")
        self.chatMsgEdit.raise_()
        self.chatFuncList.raise_()
        self.chatSendBtn.raise_()
        self.chatMsgBrowser.raise_()
        self.pushButton.raise_()
        self.sendFileBtn.raise_()
        self.VoiceCallBtn.raise_()
        self.TransformBtn.raise_()
        self.sendVoiceBtn.raise_()
        self.horizontalLayout_4.addWidget(self.widget)
        self.widget_4 = QtWidgets.QWidget(self.widget_3)
        self.widget_4.setGeometry(QtCore.QRect(0, 0, 274, 550))
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.chatMsgList = QtWidgets.QListWidget(self.widget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(20)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chatMsgList.sizePolicy().hasHeightForWidth())
        self.chatMsgList.setSizePolicy(sizePolicy)
        self.chatMsgList.setMinimumSize(QtCore.QSize(100, 75))
        self.chatMsgList.setStyleSheet("\n"
"background-color: rgb(255, 251, 233);")
        self.chatMsgList.setObjectName("chatMsgList")
        self.horizontalLayout_3.addWidget(self.chatMsgList)
        self.characterSettingPage = QtWidgets.QWidget(self.chatTab)
        self.characterSettingPage.setGeometry(QtCore.QRect(477, 309, 331, 50))
        self.characterSettingPage.setObjectName("characterSettingPage")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.characterSettingPage)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.characterSettingEdit = QtWidgets.QLineEdit(self.characterSettingPage)
        self.characterSettingEdit.setObjectName("characterSettingEdit")
        self.horizontalLayout_2.addWidget(self.characterSettingEdit)
        self.confirmCharacterBtn = QtWidgets.QPushButton(self.characterSettingPage)
        self.confirmCharacterBtn.setObjectName("confirmCharacterBtn")
        self.horizontalLayout_2.addWidget(self.confirmCharacterBtn)
        self.tabWidget.addTab(self.chatTab, "")
        self.contactTab = QtWidgets.QWidget()
        self.contactTab.setObjectName("contactTab")
        self.contactSearchEdit = QtWidgets.QLineEdit(self.contactTab)
        self.contactSearchEdit.setGeometry(QtCore.QRect(8, 12, 201, 31))
        self.contactSearchEdit.setObjectName("contactSearchEdit")
        self.searchAccountBtn = QtWidgets.QPushButton(self.contactTab)
        self.searchAccountBtn.setGeometry(QtCore.QRect(213, 11, 21, 32))
        self.searchAccountBtn.setText("")
        self.searchAccountBtn.setObjectName("searchAccountBtn")
        self.contactListStack = QtWidgets.QStackedWidget(self.contactTab)
        self.contactListStack.setGeometry(QtCore.QRect(0, 50, 274, 491))
        self.contactListStack.setObjectName("contactListStack")
        self.contactFriendPage = QtWidgets.QWidget()
        self.contactFriendPage.setObjectName("contactFriendPage")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.contactFriendPage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.manageContactsBtn = QtWidgets.QPushButton(self.contactFriendPage)
        self.manageContactsBtn.setObjectName("manageContactsBtn")
        self.verticalLayout.addWidget(self.manageContactsBtn)
        self.widget_2 = QtWidgets.QWidget(self.contactFriendPage)
        self.widget_2.setObjectName("widget_2")
        self.createGroupBtn = QtWidgets.QPushButton(self.widget_2)
        self.createGroupBtn.setGeometry(QtCore.QRect(20, 374, 216, 32))
        self.createGroupBtn.setObjectName("createGroupBtn")
        self.contactsList = QtWidgets.QTreeWidget(self.widget_2)
        self.contactsList.setGeometry(QtCore.QRect(0, 0, 256, 435))
        self.contactsList.setObjectName("contactsList")
        item_0 = QtWidgets.QTreeWidgetItem(self.contactsList)
        item_0 = QtWidgets.QTreeWidgetItem(self.contactsList)
        self.contactsList.raise_()
        self.createGroupBtn.raise_()
        self.verticalLayout.addWidget(self.widget_2)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)
        self.contactListStack.addWidget(self.contactFriendPage)
        self.addFriendPage = QtWidgets.QWidget()
        self.addFriendPage.setObjectName("addFriendPage")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.addFriendPage)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.addContactList = QtWidgets.QTreeWidget(self.addFriendPage)
        self.addContactList.setObjectName("addContactList")
        item_0 = QtWidgets.QTreeWidgetItem(self.addContactList)
        item_0 = QtWidgets.QTreeWidgetItem(self.addContactList)
        self.verticalLayout_2.addWidget(self.addContactList)
        self.contactListStack.addWidget(self.addFriendPage)
        self.addAccountBtn = QtWidgets.QPushButton(self.contactTab)
        self.addAccountBtn.setGeometry(QtCore.QRect(238, 11, 31, 32))
        self.addAccountBtn.setText("")
        self.addAccountBtn.setObjectName("addAccountBtn")
        self.showContactPage = QtWidgets.QGroupBox(self.contactTab)
        self.showContactPage.setGeometry(QtCore.QRect(274, 0, 621, 550))
        self.showContactPage.setObjectName("showContactPage")
        self.groupMemberPage2 = QtWidgets.QScrollArea(self.showContactPage)
        self.groupMemberPage2.setGeometry(QtCore.QRect(0, 30, 621, 212))
        self.groupMemberPage2.setWidgetResizable(True)
        self.groupMemberPage2.setObjectName("groupMemberPage2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 619, 210))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupMemberPage = QtWidgets.QTableWidget(self.scrollAreaWidgetContents_2)
        self.groupMemberPage.setStyleSheet("background-color: rgb(255, 251, 233);")
        self.groupMemberPage.setObjectName("groupMemberPage")
        self.groupMemberPage.setColumnCount(0)
        self.groupMemberPage.setRowCount(0)
        self.horizontalLayout.addWidget(self.groupMemberPage)
        self.groupMemberPage2.setWidget(self.scrollAreaWidgetContents_2)
        self.manageGroupMemberBtn = QtWidgets.QPushButton(self.showContactPage)
        self.manageGroupMemberBtn.setGeometry(QtCore.QRect(70, 250, 400, 32))
        self.manageGroupMemberBtn.setObjectName("manageGroupMemberBtn")
        self.quitGroupBtn = QtWidgets.QPushButton(self.showContactPage)
        self.quitGroupBtn.setGeometry(QtCore.QRect(510, 483, 97, 32))
        self.quitGroupBtn.setObjectName("quitGroupBtn")
        self.inviteGroupMemberBtn = QtWidgets.QPushButton(self.showContactPage)
        self.inviteGroupMemberBtn.setGeometry(QtCore.QRect(480, 250, 97, 32))
        self.inviteGroupMemberBtn.setObjectName("inviteGroupMemberBtn")
        self.groupValidationPage = QtWidgets.QListWidget(self.showContactPage)
        self.groupValidationPage.setGeometry(QtCore.QRect(0, 290, 621, 171))
        self.groupValidationPage.setStyleSheet("background-color: rgb(255, 251, 233);")
        self.groupValidationPage.setObjectName("groupValidationPage")
        self.tabWidget.addTab(self.contactTab, "")
        self.userInfoTable = QtWidgets.QWidget()
        self.userInfoTable.setObjectName("userInfoTable")
        self.ChangeInformation = QtWidgets.QPushButton(self.userInfoTable)
        self.ChangeInformation.setGeometry(QtCore.QRect(140, 420, 131, 25))
        self.ChangeInformation.setObjectName("ChangeInformation")
        self.avatarInfo = QtWidgets.QLabel(self.userInfoTable)
        self.avatarInfo.setGeometry(QtCore.QRect(60, 52, 300, 300))
        self.avatarInfo.setStyleSheet("background-color: rgb(170, 255, 255);")
        self.avatarInfo.setText("")
        self.avatarInfo.setObjectName("avatarInfo")
        self.uploadAvatarBtn = QtWidgets.QPushButton(self.userInfoTable)
        self.uploadAvatarBtn.setGeometry(QtCore.QRect(139, 374, 131, 32))
        self.uploadAvatarBtn.setObjectName("uploadAvatarBtn")
        self.label_2 = QtWidgets.QLabel(self.userInfoTable)
        self.label_2.setGeometry(QtCore.QRect(470, 50, 91, 24))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.userInfoTable)
        self.label_3.setGeometry(QtCore.QRect(470, 150, 81, 24))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.userInfoTable)
        self.label_4.setGeometry(QtCore.QRect(470, 200, 51, 24))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.userInfoTable)
        self.label_5.setGeometry(QtCore.QRect(470, 250, 131, 24))
        self.label_5.setObjectName("label_5")
        self.userNameInfo = QtWidgets.QLabel(self.userInfoTable)
        self.userNameInfo.setGeometry(QtCore.QRect(670, 50, 201, 24))
        self.userNameInfo.setObjectName("userNameInfo")
        self.passwordInfo = QtWidgets.QLabel(self.userInfoTable)
        self.passwordInfo.setGeometry(QtCore.QRect(670, 150, 221, 24))
        self.passwordInfo.setObjectName("passwordInfo")
        self.ipInfo = QtWidgets.QLabel(self.userInfoTable)
        self.ipInfo.setGeometry(QtCore.QRect(670, 200, 121, 24))
        self.ipInfo.setObjectName("ipInfo")
        self.label_12 = QtWidgets.QLabel(self.userInfoTable)
        self.label_12.setGeometry(QtCore.QRect(470, 350, 121, 24))
        self.label_12.setObjectName("label_12")
        self.label_6 = QtWidgets.QLabel(self.userInfoTable)
        self.label_6.setGeometry(QtCore.QRect(470, 100, 91, 24))
        self.label_6.setObjectName("label_6")
        self.nickNameInfo = QtWidgets.QLabel(self.userInfoTable)
        self.nickNameInfo.setGeometry(QtCore.QRect(670, 100, 171, 24))
        self.nickNameInfo.setObjectName("nickNameInfo")
        self.secureQuestionInfo = QtWidgets.QTextBrowser(self.userInfoTable)
        self.secureQuestionInfo.setGeometry(QtCore.QRect(670, 250, 200, 70))
        self.secureQuestionInfo.setObjectName("secureQuestionInfo")
        self.secureAnswerInfo = QtWidgets.QTextBrowser(self.userInfoTable)
        self.secureAnswerInfo.setGeometry(QtCore.QRect(670, 350, 200, 70))
        self.secureAnswerInfo.setObjectName("secureAnswerInfo")
        self.uploadFaceBtn = QtWidgets.QPushButton(self.userInfoTable)
        self.uploadFaceBtn.setGeometry(QtCore.QRect(139, 454, 131, 32))
        self.uploadFaceBtn.setObjectName("uploadFaceBtn")
        self.tabWidget.addTab(self.userInfoTable, "")
        self.groupContactTab = QtWidgets.QWidget()
        self.groupContactTab.setObjectName("groupContactTab")
        self.contactSearchEdit_2 = QtWidgets.QLineEdit(self.groupContactTab)
        self.contactSearchEdit_2.setGeometry(QtCore.QRect(8, 13, 251, 31))
        self.contactSearchEdit_2.setObjectName("contactSearchEdit_2")
        self.stackedWidget = QtWidgets.QStackedWidget(self.groupContactTab)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 50, 274, 491))
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.manageContactsBtn_2 = QtWidgets.QPushButton(self.page)
        self.manageContactsBtn_2.setObjectName("manageContactsBtn_2")
        self.verticalLayout_3.addWidget(self.manageContactsBtn_2)
        self.contactFriendList_2 = QtWidgets.QListWidget(self.page)
        self.contactFriendList_2.setObjectName("contactFriendList_2")
        item = QtWidgets.QListWidgetItem()
        self.contactFriendList_2.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.contactFriendList_2.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.contactFriendList_2.addItem(item)
        self.verticalLayout_3.addWidget(self.contactFriendList_2)
        self.acceptBtn = QtWidgets.QPushButton(self.page)
        self.acceptBtn.setObjectName("acceptBtn")
        self.verticalLayout_3.addWidget(self.acceptBtn)
        self.rejectBtn = QtWidgets.QPushButton(self.page)
        self.rejectBtn.setObjectName("rejectBtn")
        self.verticalLayout_3.addWidget(self.rejectBtn)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.stackedWidget.addWidget(self.page_2)
        self.tabWidget.addTab(self.groupContactTab, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 996, 29))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        self.contactListStack.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.showMsgPage.setTitle(_translate("MainWindow", "Contact Name"))
        self.chatSendBtn.setText(_translate("MainWindow", "send"))
        self.pushButton.setText(_translate("MainWindow", "表情"))
        self.sendFileBtn.setText(_translate("MainWindow", "发送文件"))
        self.VoiceCallBtn.setText(_translate("MainWindow", "语音通话"))
        self.TransformBtn.setText(_translate("MainWindow", "语音转文字"))
        self.sendVoiceBtn.setText(_translate("MainWindow", "语音"))
        self.chatMsgList.setSortingEnabled(True)
        self.characterSettingEdit.setPlaceholderText(_translate("MainWindow", "Chatacter Setting"))
        self.confirmCharacterBtn.setText(_translate("MainWindow", "Confirm"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.chatTab), _translate("MainWindow", "Chat"))
        self.contactSearchEdit.setPlaceholderText(_translate("MainWindow", "用户名/id 搜索好友"))
        self.manageContactsBtn.setText(_translate("MainWindow", "ManageContacts"))
        self.createGroupBtn.setText(_translate("MainWindow", "i want to be group OWENR!"))
        self.contactsList.headerItem().setText(0, _translate("MainWindow", "Contacts"))
        __sortingEnabled = self.contactsList.isSortingEnabled()
        self.contactsList.setSortingEnabled(False)
        self.contactsList.topLevelItem(0).setText(0, _translate("MainWindow", "联系人"))
        self.contactsList.topLevelItem(1).setText(0, _translate("MainWindow", "群聊天"))
        self.contactsList.setSortingEnabled(__sortingEnabled)
        self.addContactList.headerItem().setText(0, _translate("MainWindow", "ADD Contacts/Group"))
        __sortingEnabled = self.addContactList.isSortingEnabled()
        self.addContactList.setSortingEnabled(False)
        self.addContactList.topLevelItem(0).setText(0, _translate("MainWindow", "联系人"))
        self.addContactList.topLevelItem(1).setText(0, _translate("MainWindow", "群聊天"))
        self.addContactList.setSortingEnabled(__sortingEnabled)
        self.showContactPage.setTitle(_translate("MainWindow", "Contact Info"))
        self.manageGroupMemberBtn.setText(_translate("MainWindow", "ManageGroupMember"))
        self.quitGroupBtn.setText(_translate("MainWindow", "QuitGroup"))
        self.inviteGroupMemberBtn.setText(_translate("MainWindow", "Invite"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.contactTab), _translate("MainWindow", "Contact"))
        self.ChangeInformation.setText(_translate("MainWindow", "alterPersonInfo"))
        self.uploadAvatarBtn.setText(_translate("MainWindow", "uploadAvatar"))
        self.label_2.setText(_translate("MainWindow", "UserName:"))
        self.label_3.setText(_translate("MainWindow", "Password:"))
        self.label_4.setText(_translate("MainWindow", "IP:"))
        self.label_5.setText(_translate("MainWindow", "SecureQuestion:"))
        self.userNameInfo.setText(_translate("MainWindow", "TextLabel"))
        self.passwordInfo.setText(_translate("MainWindow", "TextLabel"))
        self.ipInfo.setText(_translate("MainWindow", "TextLabel"))
        self.label_12.setText(_translate("MainWindow", "SecureAnswer:"))
        self.label_6.setText(_translate("MainWindow", "NickName"))
        self.nickNameInfo.setText(_translate("MainWindow", "TextLabel"))
        self.uploadFaceBtn.setText(_translate("MainWindow", "uploadFace"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.userInfoTable), _translate("MainWindow", "Info"))
        self.contactSearchEdit_2.setPlaceholderText(_translate("MainWindow", "用户名/id 搜索好友"))
        self.manageContactsBtn_2.setText(_translate("MainWindow", "ManageContacts"))
        self.contactFriendList_2.setSortingEnabled(True)
        __sortingEnabled = self.contactFriendList_2.isSortingEnabled()
        self.contactFriendList_2.setSortingEnabled(False)
        item = self.contactFriendList_2.item(0)
        item.setText(_translate("MainWindow", "friend1"))
        item = self.contactFriendList_2.item(1)
        item.setText(_translate("MainWindow", "friend2"))
        item = self.contactFriendList_2.item(2)
        item.setText(_translate("MainWindow", "friend3"))
        self.contactFriendList_2.setSortingEnabled(__sortingEnabled)
        self.acceptBtn.setText(_translate("MainWindow", "accept"))
        self.rejectBtn.setText(_translate("MainWindow", "reject"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.groupContactTab), _translate("MainWindow", "addFriend"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))


