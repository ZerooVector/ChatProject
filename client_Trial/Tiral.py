import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog,QFileDialog
from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QListWidgetItem, QTreeWidgetItem, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QAbstractItemView
from datetime import datetime
# from PyQt5.QtCore import *QAbstractItemView.SingleSelection
from PyQt5.QtGui import QPainter,QPixmap


from logindialog_ui import Ui_LoginDialog
from untitled_test_basic_ui import Ui_MainWindow

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
        self.hbox.addWidget(self.deleteContactBtn)
        self.hbox.addStretch(1)     # 抄来的 不知道什么意思
        # 布局添加到widget
        self.widget.setLayout(self.hbox)


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
    
    mg_size = (50, 50)
    def __init__(self, name, img, all_msg):
        super().__init__()
        self.all_msg = all_msg
        self.name = name
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
        self.unreadMsgLabel = QLabel()
        self.unreadMsgLabel.setText(str(self.numUnread()))
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
        self.hbox.addWidget(self.unreadMsgLabel)
        
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
        # ------------以上为Ui设置

        # 获取个人信息
        self.loadUserInfo(userName)
        #展示好友列表和聊天列表 
        self.loadChatList()
        # self.loadContactList()
        self.loadContactsList()
        self.showMsgPage.hide()
    
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
        self.userInfo = ["123", "Moriningstar", "123", "question", "ans", "ip"]

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
            if self.userInfo[0] == single_msg[0]:
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

    def loadContactsList(self):
        friendFather= self.contactsList.topLevelItem(0)
        groupFather= self.contactsList.topLevelItem(1)
        friendFather.setExpanded(True)
        groupFather.setExpanded(True)

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

    #在这个函数获得所有的好友
    def loadContactList(self):
        self.contactFriendList.clear()
        lsFriend = [("A", "./Edge.jpg"),
                    ("B", "./VS Code.jpg")]
        friend_size = 2
        for i in range(friend_size):
            item = customContactQlistWidgetItem("A", img="./pic.jpg")
            self.contactFriendList.addItem(item)
            self.contactFriendList.setItemWidget(item, item.widget)

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
        names = ["A", "B", "C"]
        self.mainwindow.reLoadChatList(names)
        print("updateClosed")

        

class loginWindow(QDialog, Ui_LoginDialog):
    def __init__(self, parent=None):
        super(loginWindow, self).__init__(parent)
        
        self.setupUi(self)
        self.loginBtn.clicked.connect(self.match)

    def match(self):
        self.userName = self.usrLineEdit.text()

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
            

        else :
            self.pwdLineEdit.clear()
            self.pwdLineEdit.setFocus()



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



    app = QApplication(sys.argv)

    loginwindow = loginWindow()

    loginwindow.show()

    if (loginwindow.exec_()== QDialog.Accepted):
        
        mainwindow = mainWindow(userName=loginwindow.userName)
        updater = mainWindowUpdater(mainwindow)
        mainwindow.show()

    sys.exit(app.exec_())

   # 新消息在前，旧消息在后 