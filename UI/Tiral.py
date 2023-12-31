import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog,QFileDialog
from PyQt5 import uic, QtCore , QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QListWidgetItem, QTreeWidgetItem, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QAbstractItemView, QMessageBox
from PyQt5.QtGui import QPixmap
from datetime import datetime
# from PyQt5.QtCore import *QAbstractItemView.SingleSelection
from PyQt5.QtGui import QPainter,QPixmap


from logindialog_ui import Ui_LoginDialog
from untitled_test_basic_ui import Ui_MainWindow
from register_ui import Ui_Register 
from information_ui import Ui_Information
from Voicecall_ui import Ui_Voicecall

###########################
import socket
import time
import threading  # 导入线程模块
import os 
# pause_event = threading.Event()
FILE_PATH = "./filerecieving/"
client_sock = ""



############ tool functions ############## 
def send_msg(sock, msg):
    # 将消息编码为字节流
    msg = msg.encode('utf-8')
    # 创建固定长度的消息头，例如4个字节，包含消息长度
    msg_header = f"{len(msg):<4}".encode('utf-8')
    # 发送消息头和消息主体
    sock.sendall(msg_header + msg)

def recv_msg(sock):
    msg_header = sock.recv(4).decode('utf-8').strip()
    
    # 检查消息头是否为空
    if not msg_header:
        print("Connection closed by the server")
        sock.close()
        return None

    
    msg_len = int(msg_header)
    # 根据消息头指定的长度接收消息主体
    return sock.recv(msg_len).decode('utf-8')

def send_file(sock, file_chunk):
    # 发送文件块大小
    header = f"{len(file_chunk):<4}"
    sock.sendall(header.encode('utf-8'))

    # 发送文件块
    sock.sendall(file_chunk)

def recv_file(sock):
    try:
        # 设置套接字超时为10秒
        sock.settimeout(0.1)

        # 接收文件块大小
        header = sock.recv(4).decode('utf-8').strip()
        chunk_size = int(header)
        
        # 循环接收文件块直到达到期望的大小
        chunks = []
        bytes_received = 0
        while bytes_received < chunk_size:
            chunk = sock.recv(min(chunk_size - bytes_received, 4096))
            if not chunk:
                # Connection closed before receiving expected data
                raise Exception("Connection closed before receiving full data.")
            chunks.append(chunk)
            bytes_received += len(chunk)

        data = b''.join(chunks)

        # 重置套接字为阻塞模式（如果需要）
        sock.setblocking(True)

        return data
    except socket.timeout:
        print("Socket timed out while receiving data.")
        return None
    except Exception as e:
        print(f"Error while receiving data: {e}")
        return None


##########################################################
# 添加好友界面的Item填充
class customAddContactItem(QTreeWidgetItem):
    # 规定头像大小为（50,50）
    img_size = (50, 50)
    def __init__(self, name, img):
        super().__init__()

        self.widget = QWidget()

        # 设置图像label
        self.avatorLabel = QLabel()
        #设置图像源于图像大小的函数
        self.avatorLabel.setPixmap(QPixmap(img).scaled(50, 50))

        # 显示名字
        self.nameLabel = QLabel()
        self.nameLabel.setText(name)

        # 设置删除按钮
        self.addContactBtn = QPushButton()
        self.addContactBtn.setText("add")
        # 槽函数，当按钮被点击时删除该项
        self.addContactBtn.clicked.connect(self.addContact)


        # 设置item_widget的布局，写成函数便于继承重写
        self.set_distribution()

        # 设置自定义sizehint，否则无法显示 抄来的 不知道为什么
        self.setSizeHint(0, self.widget.sizeHint())

    # 写添加好友/群组的逻辑
    def addContact(self):
        pass


    def set_distribution(self):
        # 设置布局
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.avatorLabel)
        self.hbox.addWidget(self.nameLabel)
        self.hbox.addWidget(self.addContactBtn)
        self.hbox.addStretch(1)     # 抄来的 不知道什么意思
        # 布局添加到widget
        self.widget.setLayout(self.hbox)

# 好友以及群组界面的Item填充
class customContactItem(QTreeWidgetItem):
    
    # 规定头像大小为（50,50）
    img_size = (50, 50)
    def __init__(self, name, img):
        super().__init__()

        self.widget = QWidget()

        # 设置图像label
        self.avatorLabel = QLabel()
        #设置图像源于图像大小的函数
        self.avatorLabel.setPixmap(QPixmap(img).scaled(50, 50))

        # 显示名字
        self.nameLabel = QLabel()
        self.nameLabel.setText(name)

        # 设置删除按钮
        self.deleteContactBtn = QPushButton()
        self.deleteContactBtn.setText("Delete")
        # 槽函数，当按钮被点击时删除该项
        self.deleteContactBtn.clicked.connect(self.deleteContact)
        self.deleteContactBtn.hide()


        # 设置item_widget的布局，写成函数便于继承重写
        self.set_distribution()

        # 设置自定义sizehint，否则无法显示 抄来的 不知道为什么
        self.setSizeHint(0, self.widget.sizeHint())

    def deleteContact(self):
        # self.listWidget()可能是内部的一个用于获得当前所在list_widget的一个函数
        parent_item = self.parent()
        tree_widget = self.treeWidget()
        index = -1
        for i in range(parent_item.childCount()):
            if parent_item.child(i) == self:
                index = i
                break
        parent_item.takeChild(index)
        # 发送信号从数据库删除联系人或群组


    def set_distribution(self):
        # 设置布局
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.avatorLabel)
        self.hbox.addWidget(self.nameLabel)
        self.hbox.addWidget(self.deleteContactBtn)
        self.hbox.addStretch(1)     # 抄来的 不知道什么意思
        # 布局添加到widget
        self.widget.setLayout(self.hbox)

# Contact页面,好友用户ListWidget的填充 自定义Item
class customContactQlistWidgetItem(QListWidgetItem):
    
    # 规定头像大小为（50,50）
    img_size = (50, 50)
    def __init__(self, name, img,):
        super().__init__()

        self.widget = QWidget()

        # 设置图像label
        self.avatorLabel = QLabel()
        #设置图像源于图像大小的函数
        self.avatorLabel.setPixmap(QPixmap(img).scaled(50, 50))

        # 显示名字
        self.nameLabel = QLabel()
        self.nameLabel.setText(name)

        # 设置删除按钮
        self.deleteContactBtn = QPushButton()
        self.deleteContactBtn.setText("Delete")
        # 槽函数，当按钮被点击时删除该项
        self.deleteContactBtn.clicked.connect(self.deleteContact)
        self.deleteContactBtn.hide()


        # 设置item_widget的布局，写成函数便于继承重写
        self.set_distribution()

        # 设置自定义sizehint，否则无法显示 抄来的 不知道为什么
        self.setSizeHint(self.widget.sizeHint())

    def deleteContact(self):
        # self.listWidget()可能是内部的一个用于获得当前所在list_widget的一个函数
        list_widget = self.listWidget()
        list_widget.takeItem(list_widget.row(self))

    def set_distribution(self):
        # 设置布局
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.avatorLabel)
        self.hbox.addWidget(self.nameLabel)
        self.hbox.addWidget(self.deleteContactBtn)
        self.hbox.addStretch(1)     # 抄来的 不知道什么意思
        # 布局添加到widget
        self.widget.setLayout(self.hbox)

# 聊天列表界面的Item填充
class customChatItem(QListWidgetItem):
    
    img_size = (50, 50)
    def __init__(self, name, img, all_msg, isGroup = False):
        super().__init__()
        self.all_msg = all_msg
        self.name = name
        self.isGroup = isGroup
        self.widget = QWidget()
        # 设置图像label
        self.avatorLabel = QLabel()
        #设置图像源于图像大小的函数
        self.avatorLabel.setPixmap(QPixmap(img).scaled(50, 50))
        # 显示名字
        self.nameLabel = QLabel()
        self.nameLabel.setText(name)
        # 显示上一条最新消息
        self.lastMsgLabel = QLabel()
        self.last_msg = all_msg[0]
        temp = self.last_msg[2] if len(self.last_msg[2]) < 10 else self.last_msg[2][:10] + "..."
        self.lastMsgLabel.setText(temp)
        # 未睹消息
        if isGroup:
            self.isGourpLabel = QLabel()
            self.isGourpLabel.setText("Group")
        # 设置item_widget的布局，写成函数便于继承重写
        self.set_distribution()
        # 设置自定义sizehint，否则无法显示 抄来的 不知道为什么
        self.setSizeHint(self.widget.sizeHint())

    # 返回未睹消息数
    def numUnread(self):
        size = len(self.all_msg)
        num = 0
        for i in range(size):
            if self.all_msg[ i][4] == True \
                and self.all_msg[i][0] != USERNAME:
                num += 1
            else :
                break
        print(num)
        return num

    # 在有修改时更新item
    def updateChatItem(self,name, img, all_msg):
        if name != None:
            self.nameLabel.setText(name)
        if img != None:
            self.avatorLabel.setPixmap(QPixmap(img).scaled(50, 50))
        if all_msg != None:
            self.all_msg = all_msg.copy()
        self.last_msg = all_msg[0]
        temp = self.last_msg[2] if len(self.last_msg[2]) < 10 else self.last_msg[2][:10] + "..."
        self.lastMsgLabel.setText(temp)


    
    # 设置界面布局
    def set_distribution(self):
        # 尝试box的嵌套
        self.vwidget = QWidget()
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.nameLabel)
        self.vbox.addWidget(self.lastMsgLabel)
        self.vwidget.setLayout(self.vbox)

        # vbox 在 hbox的里面
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.avatorLabel)
        self.hbox.addWidget(self.vwidget)
        if self.isGroup:
            self.hbox.addWidget(self.isGroupLabel)
        
        # 布局添加到widget
        self.widget.setLayout(self.hbox)



# 聊天气泡
class chatBubble(QWidget):
    def __init__(self, content, is_left,  name , date,  \
                 is_unread = False, parent = None, isFile = False, isVoiceMsg = False):
        super().__init__(parent)
        # 美工部分 设置气泡颜色 字体
        self.setStyleSheet("background-color: red;\
                            border-radius: 10px\
                           padding: 10px")
        
        msgTitle = QLabel(name +":  at " + date.strftime("%Y-%m-%d, %H:%M:%S") )
        msgLabel = QLabel(content)
        msgLabel.setWordWrap(True)

        recvFileBtn = QPushButton()
        if isFile :
            recvFileBtn.setText("receiveFILE")
            recvFileBtn.clicked.connect(self.receiveFIle)
            # self.clicked.connect(recvFileBtn.clicked())

        if isVoiceMsg:
            recvFileBtn.setText("Play")
            recvFileBtn.clicked.connect(self.playVoiceMsg)
            # self.clicked.connect(recvFileBtn.clicked())

        contentWidget = QWidget()
        contentWidget_layout = QHBoxLayout()

        if is_left:
            contentWidget_layout.addWidget(msgLabel, alignment = Qt.AlignLeft)
            if isFile or isVoiceMsg:
                contentWidget_layout.addWidget(recvFileBtn, alignment = Qt.AlignLeft)
        else:
            if isFile or isVoiceMsg:
                contentWidget_layout.addWidget(recvFileBtn, alignment = Qt.AlignRight)
            contentWidget_layout.addWidget(msgLabel, alignment  = Qt.AlignRight)
        contentWidget.setLayout(contentWidget_layout)
        
        layout = QVBoxLayout()
        layout.addWidget(msgTitle)
        layout.addWidget(contentWidget)
        self.setLayout (layout)

        # 放弃显示已度消息
        # unread = "unread" if is_unread == True else "read"
        # isUnreadLabel = QLabel(unread)

    # 写收文件的逻辑
    def receiveFIle(self):
        file_dialog = QFileDialog()
        save_path, _ = file_dialog.getSaveFileName(self, "保存文件")
        if save_path:
            # 在这里实现文件接收的逻辑
            print("保存文件的路径：", save_path)
        else :
            pass

    # 需要写进度条还是仅仅返回收取错误或成功
    # 写收文件并且播放的逻辑
    def playVoiceMsg(self):
        file_dialog = QFileDialog()
        save_path, _ = file_dialog.getSaveFileName(self, "保存文件")
        if save_path:
            # 在这里实现文件接收的逻辑
            print("保存文件的路径：", save_path)
            # 接收文件后调用相关播放器播放文件 不会弄
    

# 主窗口
class mainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None, userName = None ):
        super(mainWindow, self).__init__(parent)
        self.setWindowTitle("BlazIngChaT")
        self.setupUi(self)
        # 好友列表的设置
        self.contactListStack.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.contactListStack_showPageAdd = False
        # 限制列表只能单个选择
        # self.addFriendList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.chatMsgList.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.contactFriendList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.contactsList.setSelectionMode(QAbstractItemView.SingleSelection)
        # 设置chatMsgBrowser为气泡聊天界面显示
        self.setChatMsgBrowser()
        # 草函数 使得列表转向搜索or添加
        self.addAccountBtn.clicked.connect(self.contactListStackSwitch)
        # 槽函数 返回搜索结果
        self.searchAccountBtn.clicked.connect(self.searchAccount)
        #草函数 管理好友列表按键
        self.manageContactsOn = False
        self.manageContactsBtn.clicked.connect(self.manageContacts)
        # 槽函数 连接聊天列表与聊天界面
        self.chatMsgList.currentItemChanged.connect(self.showChat)
        self.last_item = None
        # 槽函数 文件发送绑定
        self.sendFileBtn.clicked.connect(self.sendFile)
        # 槽函数 发送已编辑的消息
        self.chatSendBtn.clicked.connect(self.chatSend)
        # 槽函数   修改个人信息
        self.ChangeInformation.clicked.connect(self.informationClicked)
        # 槽函数 上传头像
        self.uploadAvatarBtn.clicked.connect(self.uploadAvatar)
        # 槽函数 同意拒绝好友申请
        #  friend_request_list = []
        #  self.contactFriendList_2.addItems(friend_request_list)
        self.acceptBtn.clicked.connect(self.accept_friend_request)
        self.rejectBtn.clicked.connect(self.reject_friend_request)
        # 槽函数 进入语音聊天
        self.VoiceCallBtn.clicked.connect(self.intoVoicecall)
        # 槽函数 语音转文字
        # self.TransformBtn.clicked.connect(self.transform)
        # 槽函数 发送语音
        # self.sendVoiceBtn.clicked.connect(self.sendvoice)
        self.tabWidget.currentChanged['int'].connect(self.tabfun)
        # ------------以上为Ui设置

        # 获取个人信息
        self.loadUserInfo(userName)
        #展示好友列表和聊天列表 
        self.loadChatList()
        # self.loadContactList()
        self.loadContactsList()
        self.showMsgPage.hide()

    def tabfun(self):
        print("skdfj")
    def informationClicked(self):
        self.information = Information()
        self.information.show()
        self.information.exec_()
    # 关于Browser的一些补充设置
    def setChatMsgBrowser(self):
        self.chatMsgBrowser.setWidgetResizable(True)
        #设置填充widget
        container_widget = QWidget()
        container_layout = QVBoxLayout()
        container_layout.addStretch()
        container_widget.setLayout(container_layout)
        self.chatMsgBrowser.setWidget(container_widget)
        
    # 在新界面清除Browser的内容    
    def chatMsgBrowserClear(self):
        container_layout = self.chatMsgBrowser.widget().layout()
        while container_layout.count() > 1:
            # 有趣的是,给一个widget设置他的layout后再添加子类wigdet，layout在其中添加的是layoutItem而非wigdet
            # 这导致多重连环继承
            widget = container_layout.takeAt(0).widget()
            if widget:
                print("delete one")
                widget.deleteLater()

    # 获取当前用户信息的逻辑    
    def loadUserInfo(self, userName):
        # UserInfo格式 【用户名， 昵称， 密码， 密保问题， 密保答案，ip信息 】
        #还期望获得个人用户头像 set as "avator.jpg" or sth
        
        self.userInfo ={\
            "avatarInfo": "./pic.jpg", \
            "userNameInfo" : "123", \
            "nickNameInfo": "Morningstar", \
            "passwordInfo": "123", \
            "secureQuestionInfo": "question" * 10, \
            "secureAnswerInfo": "ans" * 10, \
            "ipInfo" : "ip"
        }
        self.avatarInfo.setPixmap(QPixmap(self.userInfo["avatarInfo"]).scaled(300, 300))
        self.userNameInfo.setText(self.userInfo["userNameInfo"])
        self.nickNameInfo.setText(self.userInfo["nickNameInfo"])
        self.passwordInfo.setText(self.userInfo["passwordInfo"])
        self.secureQuestionInfo.textCursor().insertText(self.userInfo["secureQuestionInfo"])
        self.secureAnswerInfo.textCursor().insertText(self.userInfo["secureAnswerInfo"])
        self.ipInfo.setText(self.userInfo["ipInfo"])

    # 用户向服务器上传头像
    def uploadAvatar(self):
        file_dialog = QFileDialog()
        file_path , _ = file_dialog.getOpenFileName(self, "选择文件")
        if file_path:
            pass

    # 点击按钮后发送消息
    def chatSend(self):
        msg = self.chatMsgEdit.toPlainText()
        self.chatMsgEdit.clear()
        self.chatMsgEdit.setFocus()
        #写发送消息的逻辑
        pass
    
    def sendFile(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择文件")
        if file_path:
            #写发送文件的逻辑
            pass

    # 展示聊天界面
    def showChat(self,cur_item):
        # 设置聊天头
        self.showMsgPage.setTitle(cur_item.nameLabel.text())
        # 设置显示界面
        # self.chatMsgBrowserClear()
        self.showMsg(cur_item)
        self.showMsgPage.show()


    # 从一个item获得所有消息  或者仅输入一条消息 参数只写一个！！！
    def showMsg(self, item = None, single_msg = None, position = 0):  
        # 尝试用可变参数实现函数重载
        if item != None:# 如果两个是同一个chat，则仅仅更新最新的
            if self.last_item == item:
                size =  len(item.all_msg) - len(self.all_msg) 
                # 先做倒叙，再添加
                print(size)
                print(item.all_msg)
                for msg in item.all_msg[0:size][::-1]:
                    # position一定写-2， 不写-1，防止把自拓展的空白区域‘手齐’(sb输入法)掉
                    print(msg)
                    self.showMsg(single_msg=msg, position = -2)
                self.all_msg = item.all_msg.copy()

            else:
                self.last_item = item
                self.all_msg = item.all_msg.copy()
                self.chatMsgBrowserClear()
                for msg in item.all_msg:
                    print(msg)
                    self.showMsg(single_msg=msg)
        
        elif single_msg != None:
            # 仅仅添加一条消息        
            is_left = True
            if self.userInfo["userNameInfo"] == single_msg[0]:
                is_left = False
            self.chatMsgBrowser.widget().layout()\
                .insertWidget(position, chatBubble(content=single_msg[2],\
                                                                        name=single_msg[0], date=single_msg[3],  isVoiceMsg=True,\
                                                                        is_left=is_left, is_unread= single_msg[4]))
            # QTimer.singleShot(10, 
            #                   self.chatMsgBrowser.verticalScrollBar().\
            #                     setValue(self.chatMsgBrowser.verticalScrollBar().maximum()))
            self.chatMsgBrowser.verticalScrollBar().\
                setValue(self.chatMsgBrowser.verticalScrollBar().maximum())
            
    # 搜索好友并添加
    def searchAccount(self):
        if self.contactListStack_showPageAdd == True:
            #该if语句下做添加好友返回搜索结果的界面
            friendFather = self.addContactList.topLevelItem(0)
            groupFather = self.addContactList.topLevelItem(1)
            friendFather.setExpanded(True)
            groupFather.setExpanded(True)
            # 先晴空
            for i in range(friendFather.childCount()):
                friendFather.takeChild(i)
            for i in range(groupFather.childCount()):
                groupFather.takeChild(i)
            #这两个列表应该是服务器返回的
            ans_searchFriend = [('A', './pic.jpg'), ('Anne', './pic.jpg')]
            ans_searchGroup = [('A', './pic.jpg'), ('Anne', "./pic.jpg")]

            for i in range(len(ans_searchFriend)):
                item = customAddContactItem(name=ans_searchFriend[i][0], img=ans_searchGroup[i][1])
                friendFather.addChild(item)
                self.addContactList.setItemWidget(item, 0, item.widget) 
            for i in range(len(ans_searchGroup)):
                item = customAddContactItem(name=ans_searchGroup[i][0], img=ans_searchGroup[i][1])
                groupFather.addChild(item)
                self.addContactList.setItemWidget(item, 0, item.widget) 

        else :
            # 该if语句下做搜索已有好友结果的界面 取消该功能了
            pass

    # 使得manageContacts按钮按下会显示删除好友
    def manageContacts(self):
        friendFather = self.contactsList.topLevelItem(0)
        groupFather = self.contactsList.topLevelItem(1)

        if self.manageContactsOn == False:
            for i in range(friendFather.childCount()):
                item = friendFather.child(i)
                print(item.nameLabel.text())
                item.deleteContactBtn.show()
                item = groupFather.child(i)
                item.deleteContactBtn.show()
        else :
            for i in range(friendFather.childCount()):
                item = friendFather.child(i)
                item.deleteContactBtn.hide()
                item = groupFather.child(i)
                item.deleteContactBtn.hide()
        self.manageContactsOn = not self.manageContactsOn

    # 使得好友列表可以在搜索和显示中切换，通过bool参数showPageAdd
    def contactListStackSwitch(self):
        _translate = QtCore.QCoreApplication.translate
        if self.contactListStack_showPageAdd == True:
            self.contactListStack.setCurrentWidget(self.contactFriendPage)
            self.contactSearchEdit.setPlaceholderText(_translate("LoginDialog", "用户名/id 搜索好友"))
        else :
            self.contactListStack.setCurrentWidget(self.addFriendPage)
            self.contactSearchEdit.setPlaceholderText(_translate("LoginDialog", "用户名/id 搜索添加好友"))

        self.contactListStack_showPageAdd = not self.contactListStack_showPageAdd

    # 期望在这个函数获得所所有的聊天记录 all_msg
    def loadChatList(self):
        # msg格式   [发送者 接受者 内容 时间 是否已读]
        dt1 = datetime(2023, 8 , 20,12,32, 50 )
        dt2 = datetime(2000,1,1,1,1,1)
        all_msg = [("A", "123", "hellollllllllllllllllllllllllllllll\
                    llllllllllllllllllllllllllllllllllllllllll\
                    lllllllllllllllllllllllllllllllllllllllll\
                    ;\lllllllllllllllllllllllllllllllllllllll", dt1, True), ("123", "A", "hey", dt2, False )]

        lsFriend = [("A", "./pic.jpg", all_msg),("B", "pic.jpg", all_msg)]
        
        # 以上为测试 生成lsFriend即可
        for i in range(len(lsFriend)):
            item = customChatItem(lsFriend[i][0], lsFriend[i][1], lsFriend[i][2])
            self.chatMsgList.addItem(item)
            self.chatMsgList.setItemWidget(item, item.widget)

    # 期望在这个函数获得新的聊天记录形成items，与原来的比较后，更新
    def reLoadChatList(self, names): 
        dt1 = datetime(2023, 8 , 20,12,32, 50 )
        dt2 = datetime(2000,1,1,1,1,1)
        all_msg = [("123", "A", "nononononononono", dt2, False ), \
                   ("A", "123", "hellollllllllllllllllllllllllllllll\
                    llllllllllllllllllllllllllllllllllllllllll\
                    lllllllllllllllllllllllllllllllllllllllll\
                    ;\lllllllllllllllllllllllllllllllllllllll", dt1, True), ("123", "A", "hey", dt2, False )]
        all_msg_A  = all_msg_B = all_msg_C = all_msg.copy()
        lsFriend = [{"name": "A", "img":  "./pic.jpg","new_msg":  all_msg_A}, \
                    {"name": "B", "img": "./pic.jpg", "new_msg": all_msg_B}, \
                    {"name": "C", "img":  './pic.jpg',"new_msg": all_msg_C}]

        # 以上为测试 生成lsFriend 即可
        #  all_msg处只用写入新的消息!!!!!!!!! 
        # 获得现有的items
        last_items = self.chatMsgList.findItems("", Qt.MatchContains)
        # 用于返回指定name的字典
        def matchNames(lsFriend, name):
                for i in range(len(lsFriend)):
                    if lsFriend[i]["name"] == name:
                        return i
        # visited
        updated = [0 for _ in range(len(names))]
        updated_items = []
        # 匹配现有的item并更新
        for item in last_items:
            if item.name in names:
                i = matchNames(lsFriend, item.name)
                # print(lsFriend[i])
                lsFriend[i]["all_msg"] = lsFriend[i]["new_msg"] + item.all_msg

                del lsFriend[i]["new_msg"]
                item.updateChatItem(**lsFriend[i])
                updated[i] = 1
                updated_items.append(item)

        # 若有新的item则加入
        for i in range(len(names)):
            if updated[i] == 0:
                lsFriend[i]["all_msg"] = lsFriend[i]["new_msg"]
                del lsFriend[i]["new_msg"]
                item = customChatItem(**lsFriend[i])
                self.chatMsgList.addItem(item)
                self.chatMsgList.setItemWidget(item, item.widget)
                updated_items.append(item)

        # 这傻逼库不能调用sorted方法排序,只能自己写
        def returnTime(item):
            dt = item.last_msg[3]
            return dt
        # print(updated_items)
        updated_items = sorted(updated_items, key=returnTime)

        for item in updated_items:
            print(self.chatMsgList == None)
            self.chatMsgList.insertItem(0, item)
            if item.isSelected() == True:
                print(item.name)
                self.showMsg(item)

        # items = [self.chatMsgList.item(i) for i in range(self.chatMsgList.count())]
        # self.chatMsgList.clear()
        # def returnTime(item):
        #     dt = item.last_msg[3]
        #     return dt
        # sorted_items = sorted(items, key=returnTime)
        # # 根据排序结果重新设置 QListWidget 中的项的顺序
        # for item in sorted_items:
            
        #     self.chatMsgList.addItem(item)
        # # self.chatMsgList.sortItems(key=lambda item: returnTime(item) )

    #在这个函数获得所有的好友
    def loadContactsList(self):
        friendFather= self.contactsList.topLevelItem(0)
        groupFather= self.contactsList.topLevelItem(1)
        friendFather.setExpanded(True)
        groupFather.setExpanded(True)
        #清空所有现有的内容
        while friendFather.childCount() > 0:
            friendFather.child(0).deleteContact()
        while groupFather.childCount() > 0:
            groupFather.child(0).deleteContact()

        # 以下ls需要从服务器获得，要求是全部的
        lsFriend = [("A", "./Edge.jpg"),
                    ("B", "./VS Code.jpg")]
        lsGroup = [("A", "./Edge.jpg"),
                    ("B", "./VS Code.jpg")]
        for i in range(len(lsFriend)):
            item = customContactItem(name=lsFriend[i][0], img=lsFriend[i][1])
            friendFather.addChild(item)
            self.contactsList.setItemWidget(item, 0, item.widget)
        
        for i in range(len(lsGroup)):
            item = customContactItem(name=lsGroup[i][0], img=lsGroup[i][1])
            groupFather.addChild(item) 
            self.contactsList.setItemWidget(item, 0, item.widget)

    def accept_friend_request(self):
        selected_item = self.contactFriendList_2.currentItem()
        if selected_item:
            friend_request = selected_item.text()
            # 从列表框和列表中移除好友申请
            self.contactFriendList_2.takeItem(self.contactFriendList_2.row(selected_item))
            # self.friend_requests.remove(friend_request)
            # TODO: 执行同意操作的逻辑
    def reject_friend_request(self):
        selected_item = self.contactFriendList_2.currentItem()
        if selected_item:
            friend_request = selected_item.text()
            # 从列表框和列表中移除好友申请
            self.contactFriendList_2.takeItem(self.contactFriendList_2.row(selected_item))
            # self.friend_requests.remove(friend_request)
            # TODO: 执行拒绝操作的逻辑

    def intoVoicecall(self): #进入语音聊天
        self.call = Voicecall()
        str = "用户名" # TODO str为你所对话的用户名
        # TODO add voice
        self.call.name.setText("您正在与"+str+"语音通话中")
        self.call.show()
        self.call.exec_()

    # def transform(self): # 语音转文字
        # if start_end :
            # 开始录音
            # start_end = False
        # else :
            # 结束录音
            # start_end = True
            # str = "转换后的文字" # TODO str 为转换后结果
            # self.chatMsgEdit.setText(str)

    # def sendvoice(self): # 发送语音
        # if start_end :
            # 开始录音
            # start_end = False
        # else :
            # 结束录音
            # start_end = True
            # 发送语音   # TODO 发送语音

class Voicecall(QDialog, Ui_Voicecall):
    def __init__(self, parent=None):
        super(Voicecall, self).__init__(parent)
        self.setupUi(self)
        self.DownBtn.clicked.connect(self.stopcall)

    def stopcall(self):
        # TODO 添加挂断电话的逻辑
        self.close()



# 更新窗口的触发器
class mainWindowUpdater:
    def __init__(self, mainwindow:mainWindow) -> None:
        self.mainwindow = mainwindow
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateMainWindow)
        self.timer.start(5000)# 5 s

    def updateMainWindow(self):
        print("updateCalled")
        # 在这里写更新的接口，接收服务端的某个信号，说明该用户与某些用户的消息更新了，给定参数names
        # if updeteChats():
        names = ["A", "B", "C"]
        self.mainwindow.reLoadChatList(names)
        
        # if updateContacts():
        
        self.mainwindow.loadContactsList()

        print("updateClosed")

        
# 登录界面
class loginWindow(QDialog, Ui_LoginDialog):
    def __init__(self, parent=None):
        super(loginWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("BlazIngChaT")
        self.loginBtn.clicked.connect(self.match)
        self.registerBtn.clicked.connect(self.intoRegister)
        pix = QPixmap("./title.png")
        self.label_3.setPixmap(pix)
        self.label_3.setScaledContents(True)
   #    self.faceBtn.clicked.connect(self.useface)

   # def useface(self):
        # self.usrLineEdit.text() 是用户名
        # TODO 人脸识别
        # if self.usrLineEdit.text() == "":
        #  msg_box = QMessageBox(QMessageBox.Critical, '错误', '用户名不得为空')
        #  msg_box.exec_()
        # elif 未录入人脸 :
        #  msg_box = QMessageBox(QMessageBox.Critical, '错误', '用户未录入人脸')
        #  msg_box.exec_()
        # elif 人脸识别失败 :
        #  msg_box = QMessageBox(QMessageBox.Critical, '错误', '人脸识别失败')
        #  msg_box.exec_()
        # else:
        #   self.accept()
    def intoRegister(self):
        self.regist = Register()
        self.regist.show()
        self.regist.exec_()
    
    def match(self):
        # userid = self.usrLineEdit.text() 
        # password = self.pwdLineEdit.text() 
        # msg = "L01+"
        # msg = msg + userid + "||-||" + password
        # send_msg(client_sock,msg)
        # response = recv_msg(client_sock)
        # print(response)
        # if response == "L01+SUCCESS":
        #     # self.matched = True
        #     self.accept()

        
        if self.usrLineEdit.text() == "123" and \
            self.pwdLineEdit.text() == "123":
            self.matched = True
            global USERNAME
            USERNAME = self.usrLineEdit.text()
            self.accept()
            self.userName = USERNAME

        else :
            self.pwdLineEdit.clear()
            self.pwdLineEdit.setFocus()

# 注册界面
class Register(QDialog, Ui_Register):
    def __init__(self, parent=None):
        super(Register, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("BlazIngchaT")
        self.RegisterBtn.clicked.connect(self.RBtnClicked)

    def RBtnClicked(self):
        if self.UsernameLineEdit.text() == "" or self.PasswordLineEdit.text() == "" or \
            self.NicknameLineEdit.text() == "" or self.ConfirmLineEdit.text() == "" :
            msg_box = QMessageBox(QMessageBox.Critical, '错误', '所填内容不得为空')
            msg_box.exec_()
        elif self.PasswordLineEdit.text() != self.ConfirmLineEdit.text():
            msg_box = QMessageBox(QMessageBox.Critical, '错误', '两次输入的密码不一致')
            msg_box.exec_()
        else:
            # 此处需添加将用户信息录入数据库的函数 !!!
            msg_box = QMessageBox(QMessageBox.Critical, '正确', '注册成功')
            msg_box.exec_()

            self.close()

class Information(QDialog, Ui_Information):
    def __init__(self, parent = None):
        super(Information, self).__init__(parent)
        self.setWindowTitle("BlazIngChaT")
        self.setupUi(self)
        self.ChangeNickname.setPlaceholderText("旧昵称")
        self.GoBtn.clicked.connect(self.GoClicked)

    def GoClicked(self):
        if self.OldPassword.text() == "" or self.NewPassword.text() == "" or self.ConfirmLineEdit.text() == "" :
            msg_box = QMessageBox(QMessageBox.Critical, '错误', '所填密码不得为空')
            msg_box.exec_()
        elif self.OldPassword.text() != "123":
            msg_box = QMessageBox(QMessageBox.Critical, '错误', '所填旧密码错误')
            msg_box.exec_()
        elif self.NewPassword.text() != self.ConfirmLineEdit.text() :
            msg_box = QMessageBox(QMessageBox.Critical, '错误', '新的密码两次输入不一致')
            msg_box.exec_()
        else :
            # 处需添加修改数据库中用户信息的函数
            msg_box = QMessageBox(QMessageBox.Information, '正确', '修改成功')
            msg_box.exec_()
            self.close()

if __name__ == '__main__':
    # # global client_sock
    # SERVER_IP = "127.0.0.1" 
    # SERVER_PORT = 10020
    # BUFFER_SIZE = 1024

    # client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # try:
    #     client_sock.connect((SERVER_IP, SERVER_PORT))
    # except socket.error as e:
    #     print("Connection failed! Error:", str(e))
    #     client_sock.close()
    #     exit()

    start_end=True #控制发送语音开始结束
    app = QApplication(sys.argv)

    loginwindow = loginWindow()
    loginwindow.setObjectName("BlazIngChaT")
    loginwindow.setStyleSheet("#BlazIngChaT{border-image:url(./picture/BlazIngChaT.png);}")
    loginwindow.loginBtn.setIcon(QtGui.QIcon("./picture/login.png"))
    loginwindow.loginBtn.setIconSize(QtCore.QSize(40, 40))
    loginwindow.loginBtn.setStyleSheet("border:none;")
    loginwindow.faceBtn.setIcon(QtGui.QIcon("./picture/face.png"))
    loginwindow.faceBtn.setStyleSheet("border:none;")
    loginwindow.faceBtn.setIconSize(QtCore.QSize(40, 40))
    loginwindow.exitBtn.setIcon(QtGui.QIcon("./picture/exit.png"))
    loginwindow.exitBtn.setStyleSheet("border:none;")
    loginwindow.exitBtn.setIconSize(QtCore.QSize(40, 40))
    loginwindow.registerBtn.setIcon(QtGui.QIcon("./picture/register.png"))
    loginwindow.registerBtn.setStyleSheet("border:none;")
    loginwindow.registerBtn.setIconSize(QtCore.QSize(40,40))
    loginwindow.show()

    if (loginwindow.exec_()== QDialog.Accepted):
        
        mainwindow = mainWindow(userName=loginwindow.userName)
        updater = mainWindowUpdater(mainwindow)
        mainwindow.show()
        
    voicecall = Voicecall()

    sys.exit(app.exec_())

   # 新消息在前，旧消息在后 