import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog,QFileDialog
from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QListWidgetItem, QTreeWidgetItem, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QAbstractItemView, QMessageBox

from datetime import datetime
# from PyQt5.QtCore import *QAbstractItemView.SingleSelection
from PyQt5.QtGui import QPainter,QPixmap


from logindialog_ui import Ui_LoginDialog
from untitled_test_basic_ui import Ui_MainWindow
from register_ui import Ui_Register 
from information_ui import Ui_Information



###########################
import socket
import time
import threading  # 导入线程模块
import os 
import ast 
# pause_event = threading.Event()
FILE_PATH = "/home/syh/MyProjects/chatsavefile/"
AVATAR_PATH = "/home/syh/MyProjects/avatarsave/"
client_sock = ""
STOP_UPDATE  = False
AVATAR_DICT = {}


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
    
#################### Secondary functions ###############

def clientsendfile(client_sock,msg_to_send):
    
    msg = msg_to_send[4:]
    msg = msg.split("||-||")
    target = msg[0] 
    address = msg[1]
    
    if not os.path.exists(address):
        print(f"File {address} does not exist!")  # client checks the file is or not exist 
        return
    # pause_event.clear()
    
    
    send_msg(client_sock,msg_to_send)

    with open(address,"rb") as file :
    
        file_chunk = file.read(4096*2)
        while file_chunk:
            send_file(client_sock,file_chunk)
            file_chunk = file.read(4096*2)


def clientrecievefile(client_sock,data):
    data = data[4:]
    name = data 
    savepath = FILE_PATH 
    if not os.path.exists(savepath):
        while True :
            file_chunk = recv_file(client_sock)  # recieve a chunk
            if not file_chunk:
                file_chunk = ""
                break
        print(f"File {savepath} does not exist!")  # client checks the file is or not exist 
        return
    savepath = FILE_PATH + name 
    with open(savepath,"wb") as file :
        while True :
            file_chunk = recv_file(client_sock)  # recieve a chunk
            if not file_chunk:
                break
            file.write(file_chunk)
            # print("recieving...")
    print("Finish recieve file!")

def ClientDownloadAvatar(client_sock,data,avatarname):
    data = data[4:]
    name = data 
    savepath = AVATAR_PATH
    if not os.path.exists(savepath):
        while True :
            file_chunk = recv_file(client_sock)  # recieve a chunk
            if not file_chunk:
                file_chunk = ""
                break
        print(f"File {savepath} does not exist!")  # client checks the file is or not exist 
        return
    savepath = AVATAR_PATH + avatarname
    with open(savepath,"wb") as file :
        while True :
            file_chunk = recv_file(client_sock)  # recieve a chunk
            if not file_chunk:
                break
            file.write(file_chunk)
            # print("recieving...")
    print("Finish recieve file!")

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
        # self.isGroup 

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
        self.name = name 

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

        self.isGroup = False
        if  index == 1:
            self.isGroup = True

        # if isGroup == False :
        #     msg_str = "F06+" + self.name 
        #     send_msg(client_sock,msg_str)
        # elif isGroup == True :
        #     msg_str = "G21+" + self.name 
            # send_msg(client_sock,msg_str)

        pass
    
    def clearContact(self):
        
        parent_item = self.parent()
        tree_widget = self.treeWidget()
        index = -1
        for i in range(parent_item.childCount()):
            if parent_item.child(i) == self:
                index = i
                break
        parent_item.takeChild(index)
    

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
            self.isGroupLabel = QLabel()
            self.isGroupLabel.setText("Group")
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
        self.content = content 
        self.name = name 
        self.date = date 
        self.is_unread = is_unread
        self.isFile = isFile 
        self.isVoiceMsg = isVoiceMsg 


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
        global STOP_UPDATE
        STOP_UPDATE = True
        file_dialog = QFileDialog()
        # save_path, _ = file_dialog.getSaveFileName(self, "保存文件")
        
            # 先跟服务器打招呼，说我要接受文件
        send_msg(client_sock,"T03+"+self.content)
        response = recv_msg(client_sock)
        if response != "T03+ERROR":
            clientrecievefile(client_sock,response)


            # 在这里实现文件接收的逻辑
            print("保存文件的路径：", FILE_PATH)
        else :
            pass
        STOP_UPDATE = False

    # 需要写进度条还是仅仅返回收取错误或成功
    # 写收文件并且播放的逻辑
    def playVoiceMsg(self):
        global STOP_UPDATE 
        STOP_UPDATE = True 
        file_dialog = QFileDialog()
        send_msg(client_sock,"T03+"+self.content)
        response = recv_msg(client_sock)
        if response != "T03+ERROR":
            clientrecievefile(client_sock,response)


            # 在这里实现文件接收的逻辑
            print("保存文件的路径：", FILE_PATH)
        else :
            pass
        
            # 在这里实现文件接收的逻辑

            # 接收文件后调用相关播放器播放文件 不会弄
        STOP_UPDATE = False 

# 主窗口
class mainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None, userName = None ):
        super(mainWindow, self).__init__(parent)
        
        self.setupUi(self)
        # 好友列表的设置
        self.userName = userName
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
        #槽函数 上传头像
        self.uploadAvatarBtn.clicked.connect(self.uploadAvatar)
        # ------------以上为Ui设置

        # 获取个人信息
        self.loadUserInfo(userName)
        #展示好友列表和聊天列表 
        self.loadChatList()
        # self.loadContactList()
        self.loadContactsList()
        self.showMsgPage.hide()
    
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
        send_msg(client_sock,"U00+")
        user_response = ast.literal_eval(recv_msg(client_sock))

        msg_str = "U01+"
        send_msg(client_sock,msg_str)
        response = ast.literal_eval(recv_msg(client_sock))
        print(response)
        friends = response["friends"]
        friends.append(user_response[0][0])
        groups = response["groups"]
        send_msg(client_sock,"T21+")
        response = ast.literal_eval(recv_msg(client_sock))
        # print("---------------------------")
        # print(response["A00"][0][0])


        for item in friends:
            if item in response:
                send_msg(client_sock,"T03+" + response[item][0][0])
                info = recv_msg(client_sock)
                addname = os.path.splitext(response[item][0][0])[1]
                avatar_name = str(item) + "avatar" + addname
                ClientDownloadAvatar(client_sock,info,avatar_name)
                AVATAR_DICT[item] = AVATAR_PATH + avatar_name
            else :
                avatar_name = "defaultavatar.png"
                AVATAR_DICT[item] = AVATAR_PATH + avatar_name


        for item in groups :
            if item in response:
                send_msg(client_sock,"T03+" + response[item][0][0])
                info = recv_msg(client_sock)
                print(info)
                addname = os.path.splitext(response[item][0][0])[1]
                avatar_name = str(item) + "avatar" + addname
                ClientDownloadAvatar(client_sock,info,avatar_name)
                AVATAR_DICT[item] = AVATAR_PATH + avatar_name
            else :
                avatar_name = "defaultavatar.png"
                AVATAR_DICT[item] = AVATAR_PATH + avatar_name
        

        
        
        
        
        self.userInfo ={\
            "avatarInfo": AVATAR_DICT[user_response[0][0]], \
            "userNameInfo" : user_response[0][0], \
            "nickNameInfo": user_response[0][1], \
            "passwordInfo": user_response[0][2], \
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
        global STOP_UPDATE
        STOP_UPDATE = True
        file_dialog = QFileDialog()
        file_path , _ = file_dialog.getOpenFileName(self, "选择文件")
        if file_path:
            str_msg = "T20+" + self.userName + "||-||" + file_path + "||-||" + "avatar"
            clientsendfile(client_sock,str_msg)
            pass
        print("FInish upload")
        STOP_UPDATE = False

    # 点击按钮后发送消息
    def chatSend(self):
        global STOP_UPDATE
        STOP_UPDATE = True
        items = self.chatMsgList.selectedItems()
        item = items[0] 
        # item.isGroup
        print(item.isGroup)
        msg = self.chatMsgEdit.toPlainText()
        if item.isGroup == 0:
            str_msg = "C00+" + str(item.name) + "||-||" + msg 
            send_msg(client_sock,str_msg)

        if item.isGroup == 1:
            str_msg = "C03+" + str(item.name) + "||-||" + msg 
            send_msg(client_sock,str_msg)

        self.chatMsgEdit.clear()
        self.chatMsgEdit.setFocus()
        #写发送消息的逻辑
        pass 
        STOP_UPDATE = False 
    
    def sendFile(self):
        global STOP_UPDATE
        STOP_UPDATE  = True  # 发送文件时停止更新
        items = self.chatMsgList.selectedItems()
        item = items[0]
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择文件")
        if file_path:
            if item.isGroup == 0:
                str_msg = "T02+" + str(item.name) + "||-||" + str(file_path) + "||-||" + "chatfile"
                clientsendfile(client_sock,str_msg)
            else :
                str_msg = "T04+" + str(item.name) + "||-||" + str(file_path) + "||-||" + "groupchatfile"
                clientsendfile(client_sock,str_msg)
            pass

        STOP_UPDATE = False 

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
                # print(size)
                # print(item.all_msg)
                for msg in item.all_msg[0:size][::-1]:
                    # position一定写-2， 不写-1，防止把自拓展的空白区域‘手齐’(sb输入法)掉
                    # print(msg)
                    self.showMsg(single_msg=msg, position = -2)
                self.all_msg = item.all_msg.copy()

            else:
                self.last_item = item
                self.all_msg = item.all_msg.copy()
                self.chatMsgBrowserClear()
                for msg in item.all_msg:
                    # print(msg)
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

    # 期望在这个函数获得所所有的聊天记录 all_msg3
    def loadChatList(self):
        # msg格式   [发送者 接受者 内容 时间 是否已读]
        send_msg(client_sock,"U01+") # 先获取用户列表和群组列表
        friend_and_group_dict = ast.literal_eval(recv_msg(client_sock))
        friend_list = friend_and_group_dict["friends"] 
        group_list = friend_and_group_dict["groups"]

        # 接下来开始逐个人拉取信息，生成对应的消息列表
        lsFriend = [] 
        for item in friend_list:
            send_msg(client_sock,"U02+"+item)
            response = ast.literal_eval(recv_msg(client_sock))
            all_msg = [] 
            # print(response)
            for thing in response:
                
                all_msg.append((thing[0],thing[2],thing[3],datetime.strptime(thing[4], '%Y-%m-%d %H:%M:%S.%f'),thing[5],))
            if len(all_msg) > 0:
                if item in AVATAR_DICT:
                    mypath = AVATAR_DICT[item]
                else :
                    mypath = AVATAR_PATH + "defaultavatar.png"
                lsFriend.append((item,mypath,all_msg,False))

        for item in group_list:
            send_msg(client_sock,"U03+"+item)
            response = ast.literal_eval(recv_msg(client_sock))
            all_msg = [] 
            # print(response)
            for thing in response:
                all_msg.append((thing[0],thing[2],thing[3],datetime.strptime(thing[4], '%Y-%m-%d %H:%M:%S.%f'),thing[5],))
            if len(all_msg) > 0:
                if item in AVATAR_DICT:
                    mypath = AVATAR_DICT[item]
                else :
                    mypath = AVATAR_PATH + "defaultavatar.png"
                lsFriend.append((item,mypath,all_msg,True))

            # print(response)
            
            # break 


        # dt1 = datetime(2023, 8 , 20,12,32, 50 )
        # dt2 = datetime(2000,1,1,1,1,1)
        # all_msg = [("A", "123", "hellollllllllllllllllllllllllllllll\
        #             llllllllllllllllllllllllllllllllllllllllll\
        #             lllllllllllllllllllllllllllllllllllllllll\
        #             ;\lllllllllllllllllllllllllllllllllllllll", dt1, True), ("123", "A", "hey", dt2, False )]

        # lsFriend = [("A", "./pic.jpg", all_msg),("B", "pic.jpg", all_msg)]
        
        # 以上为测试 生成lsFriend即可
        for i in range(len(lsFriend)):
            item = customChatItem(lsFriend[i][0], lsFriend[i][1], lsFriend[i][2], lsFriend[i][3])
            self.chatMsgList.addItem(item)
            self.chatMsgList.setItemWidget(item, item.widget)

    # 期望在这个函数获得新的聊天记录形成items，与原来的比较后，更新
    def reLoadChatList(self, friends,groups): 
        print("___________________________UPDATE START__________________________")
        names = friends + groups
        lsFriend = []
        if len(friends) > 0:
            for item in friends:
                send_msg(client_sock,"U05+"+item)
                response = ast.literal_eval(recv_msg(client_sock))
                all_msg = [] 
                print(response)
                for thing in response:
                    
                    all_msg.append((thing[0],thing[2],thing[3],datetime.strptime(thing[4], '%Y-%m-%d %H:%M:%S.%f'),thing[5],))
                if len(all_msg) > 0:
                    lsFriend.append({"name":item,"img":None,"new_msg":all_msg})

        if len(groups) > 0:
            for item in groups:
                send_msg(client_sock,"U06+"+item)
                response = ast.literal_eval(recv_msg(client_sock))
                all_msg = [] 
                print(response)
                for thing in response:
                    all_msg.append((thing[0],thing[2],thing[3],datetime.strptime(thing[4], '%Y-%m-%d %H:%M:%S.%f'),thing[5],))
                if len(all_msg) > 0:
                    lsFriend.append({"name":item,"img":None,"new_msg":all_msg})
        print("___________________________UPDATE END__________________________")
        # print(lsFriend)

        # dt1 = datetime(2023, 8 , 20,12,32, 50 )
        # dt2 = datetime(2000,1,1,1,1,1)
        # all_msg = [("123", "A", "nononononononono", dt2, False ), \
        #            ("A", "123", "hellollllllllllllllllllllllllllllll\
        #             llllllllllllllllllllllllllllllllllllllllll\
        #             lllllllllllllllllllllllllllllllllllllllll\
        #             ;\lllllllllllllllllllllllllllllllllllllll", dt1, True), ("123", "A", "hey", dt2, False )]
        # all_msg_A  = all_msg_B = all_msg_C = all_msg.copy()
        # lsFriend = [{"name": "A", "img":  "./pic.jpg","new_msg":  all_msg_A}, \
        #             {"name": "B", "img": "./pic.jpg", "new_msg": all_msg_B}, \
        #             {"name": "C", "img":  './pic.jpg',"new_msg": all_msg_C}]

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
            friendFather.child(0).clearContact()
        while groupFather.childCount() > 0:
            groupFather.child(0).clearContact()

        # 以下ls需要从服务器获得，要求是全部的
        # 先拉取一次全部头像


        msg_str = "U01+"
        send_msg(client_sock,msg_str)
        response = ast.literal_eval(recv_msg(client_sock))
        print(response)
        friends = response["friends"]
        groups = response["groups"]
        lsFriend = [] 
        lsGroup = [] 
        
        print(response)
        for item in friends:
            lsFriend.append((item,AVATAR_DICT[item]))
        for item in groups :
            lsGroup.append((item,AVATAR_DICT[item]))


        # lsFriend = [("A", "./Edge.jpg"),
        #             ("B", "./VS Code.jpg")]
        # lsGroup = [("A", "./Edge.jpg"),
        #             ("B", "./VS Code.jpg")]
        for i in range(len(lsFriend)):
            item = customContactItem(name=lsFriend[i][0], img=lsFriend[i][1])
            friendFather.addChild(item)
            self.contactsList.setItemWidget(item, 0, item.widget)
        
        for i in range(len(lsGroup)):
            item = customContactItem(name=lsGroup[i][0], img=lsGroup[i][1])
            groupFather.addChild(item) 
            self.contactsList.setItemWidget(item, 0, item.widget)



# 更新窗口的触发器
class mainWindowUpdater():
    def __init__(self, mainwindow:mainWindow) -> None:
        self.mainwindow = mainwindow
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateMainWindow)
        self.timer.start(5000)# 5 s

    def updateMainWindow(self):
        
        if STOP_UPDATE == False:
            print("updateCalled")
            # 在这里写更新的接口，接收服务端的某个信号，说明该用户与某些用户的消息更新了，给定参数names
            if STOP_UPDATE == False:
                if self.updateChats():
                    # if STOP_UPDATE == False :

                    str_msg = "U04+"
                    send_msg(client_sock,str_msg)
                    response = ast.literal_eval(recv_msg(client_sock))
                    friends = response["friends"]
                    groups = response["groups"]
                    self.mainwindow.reLoadChatList(friends,groups)
                
                if self.updateContacts():
                
                    self.mainwindow.loadContactsList()

            print("updateClosed")

        

    def updateChats(self) :
        # msg_str = ""
        if STOP_UPDATE == False:
            str_msg = "U04+"
            send_msg(client_sock,str_msg)
            response = ast.literal_eval(recv_msg(client_sock))
            print(response)
            if len(response["friends"]) > 0 or len(response["groups"]) >0 :

                return True 
            else :
                return False 
        else :
            return False
        
    def updateContacts(self):
        if STOP_UPDATE == False :
            str_msg = "F30+"
            send_msg(client_sock,str_msg)
            response = recv_msg(client_sock)
            if response == "F30+UPDATE":
                return True 
            else :
                return False
        else :
            return False 


        
# 登录界面
class loginWindow(QDialog, Ui_LoginDialog):
    def __init__(self, parent=None):
        super(loginWindow, self).__init__(parent)
        self.setupUi(self)
        self.loginBtn.clicked.connect(self.match)
        self.registerBtn.clicked.connect(self.intoRegister)
        
    def intoRegister(self):
        self.regist = Register()
        self.regist.show()
        self.regist.exec_()
    
    def match(self):
        userid = self.usrLineEdit.text() 
        password = self.pwdLineEdit.text() 
        msg = "L01+"
        msg = msg + userid + "||-||" + password
        send_msg(client_sock,msg)
        response = recv_msg(client_sock)
        print(response)
        if response == "L01+SUCCESS":
            # self.matched = True
            self.accept()

        
        # if self.usrLineEdit.text() == "123" and \
        #     self.pwdLineEdit.text() == "123":
        #     self.matched = True
            global USERNAME
            USERNAME = self.usrLineEdit.text()
        #     self.accept()
            self.userName = USERNAME

        else :
            self.pwdLineEdit.clear()
            self.pwdLineEdit.setFocus()

# 注册界面
class Register(QDialog, Ui_Register):
    def __init__(self, parent=None):
        super(Register, self).__init__(parent)
        self.setupUi(self)
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
            msg_str = "L00+" + self.UsernameLineEdit.text() + "||-||" + self.NicknameLineEdit.text() + "||-||" + self.PasswordLineEdit.text() 
            send_msg(client_sock,msg_str)
            response = recv_msg(client_sock)
            if response == "L00+SUCCESS":
                msg_box = QMessageBox(QMessageBox.Critical, '正确', '注册成功')
                msg_box.exec_()

            self.close()

class Information(QDialog, Ui_Information):
    def __init__(self, parent = None):
        super(Information, self).__init__(parent)
        self.setupUi(self)
        self.ChangeNickname.setPlaceholderText("旧昵称")
        self.GoBtn.clicked.connect(self.GoClicked)

    def GoClicked(self):
        global STOP_UPDATE
        if self.OldPassword.text() == "" or self.NewPassword.text() == "" or self.ConfirmLineEdit.text() == "" :
            msg_box = QMessageBox(QMessageBox.Critical, '错误', '所填密码不得为空')
            msg_box.exec_()
        elif self.NewPassword.text() != self.ConfirmLineEdit.text() :
                msg_box = QMessageBox(QMessageBox.Critical, '错误', '新的密码两次输入不一致')
                msg_box.exec_()
        else:
            STOP_UPDATE = True
            str_msg = "U10+" + self.OldPassword.text() + "||-||" +self.ChangeNickname.text() + "||-||" + self.NewPassword.text()
            send_msg(client_sock,str_msg)
            response = recv_msg(client_sock)
            STOP_UPDATE = False 
            if response == "U10+ERROR":
                msg_box = QMessageBox(QMessageBox.Critical, '错误', '所填旧密码错误')
                msg_box.exec_()
            elif response == "U10+SUCCESS":
                msg_box = QMessageBox(QMessageBox.Information, '正确', '修改成功')
                msg_box.exec_()
                self.close()


if __name__ == '__main__':
    # global client_sock
    SERVER_IP = "127.0.0.1" 
    SERVER_PORT = 12345
    BUFFER_SIZE = 1024

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_sock.connect((SERVER_IP, SERVER_PORT))
    except socket.error as e:
        print("Connection failed! Error:", str(e))
        client_sock.close()
        exit()



    app = QApplication(sys.argv)

    loginwindow = loginWindow()

    loginwindow.show()

    if (loginwindow.exec_()== QDialog.Accepted):
        
        mainwindow = mainWindow(userName=loginwindow.userName)
        updater = mainWindowUpdater(mainwindow)
        mainwindow.show()

    sys.exit(app.exec_())

   # 新消息在前，旧消息在后 