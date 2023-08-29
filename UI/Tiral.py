import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QListWidgetItem, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox
# from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter,QPixmap



from logindialog import Ui_LoginDialog # name problem, I forget "_ui"
from final_ui import Ui_MainWindow
from grouptools import Ui_GroupTools  # name problem, I forget "_ui"
from peoplelist_ui import Ui_PeopleList
from managerlist_ui import Ui_ManagerList
from changepeople_ui import Ui_ChangePeople
from changemanager_ui import Ui_ChangeManager
from register_ui import Ui_Register
from information_ui import Ui_Information
from qt_material import apply_stylesheet

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


class customAddContactItem(QListWidgetItem):
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

        # 添加按钮
        self.addContactBtn = QPushButton()
        self.addContactBtn.setText("Add")
        self.addContactBtn.clicked.connect(self.addContact)

        # 设置item_widget的布局，写成函数便于继承重写
        self.set_distribution()

        # 设置自定义sizehint，否则无法显示 抄来的 不知道为什么
        self.setSizeHint(self.widget.sizeHint())

    def set_distribution(self):
        # 设置布局
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.avatorLabel)
        self.hbox.addWidget(self.nameLabel)
        self.hbox.addWidget(self.addContactBtn)
        self.hbox.addStretch(1)     # 抄来的 不知道什么意思
        # 布局添加到widget
        self.widget.setLayout(self.hbox)
    
    
    def addContact(self):
        pass


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
        

# unfinished
# class customChatQlistWidgetItem(customContactQlistWidgetItem):
    
#     def __init__(self, name, img, lastmsg):
#         super().__init__(name, img)
#         self.lastmsg = lastmsg
#         self.lastMsgLabel = QLabel()
#         self.lastMsgLabel.setText(self.lastmsg)

#     def set_distribution(self):
#         # 尝试box的嵌套
#         self.vbox = QVBoxLayout()
#         self.vbox.addWidget(self.nameLabel)
#         self.vbox.addWidget(self.lastMsgLabel)

#         # vbox 在 hbox的里面
#         self.hbox = QHBoxLayout()
#         self.hbox.addWidget(self.avatorLabel)
#         self.vbox.addWidget(self.vbox)
        
#         # 布局添加到widget
#         self.widget.setLayout(self.hbox)



class mainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(mainWindow, self).__init__(parent)
        self.setupUi(self)
        # 好友列表的设置
        self.contactListStack.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.contactListStack_showPageAdd = False
        # 草函数 使得列表转向搜索or添加
        self.addAccountBtn.clicked.connect(self.contactListStackSwitch)
        # 槽函数 返回搜索结果
        self.searchAccountBtn.clicked.connect(self.searchAccount)
        #草函数 管理好友列表按键
        self.manageContactsOn = False
        self.manageContactsBtn.clicked.connect(self.manageContacts)
        self.ManageGroup.clicked.connect(self.btnClicked)
        self.ChangeInformation.clicked.connect(self.informationClicked)
    
    def informationClicked(self):
        self.information = Information()
        self.information.show()
        self.information.exec_()
    def btnClicked(self): #点击后所发生的事
        self.grouptools = GroupTools()
        self.grouptools.show()
        self.grouptools.exec_()
		
	# self.loadChatList()
	# self.loadContactList()

    def searchAccount(self):
        if self.contactListStack_showPageAdd == True:
            #该if语句下做添加好友返回搜索结果的界面
            ans_sreach = [('A', './pic.jpg')]
            for i in range(len(ans_sreach)):
                item = customAddContactItem(ans_sreach[i][0], ans_sreach[i][1])
                self.addFriendList.addItem(item)
                self.addFriendList.setItemWidget(item, item.widget) 

        else :
            # 该if语句下做搜索已有好友结果的界面
            pass


    def manageContacts(self):
        if self.manageContactsOn == False:
            for index in range(self.contactFriendList.count()):
                item = self.contactFriendList.item(index)
                item.deleteContactBtn.show()
        else :
            for index in range(self.contactFriendList.count()):
                item = self.contactFriendList.item(index)
                item.deleteContactBtn.hide()
        self.manageContactsOn = not self.manageContactsOn
    # do something with item


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


# unfinished
    # def loadChatList(self):
    #     lsFriend = [("A", "./pic.jpg", "hi, what's up"),("B", "./pic.jpg", "hi, what's up")]
        
    #     friend_size = 2

    #     for i in range(friend_size):
    #         item = customChatQlistWidgetItem('')


    def loadContactList(self):
        self.contactFriendList.clear()
        lsFriend = [("A", "./Edge.jpg"),
                    ("B", "./VS Code.jpg")]
        friend_size = 2
        for i in range(friend_size):
            item = customContactQlistWidgetItem("A", img="./pic.jpg")
            self.contactFriendList.addItem(item)
            self.contactFriendList.setItemWidget(item, item.widget)


        

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
            self.accept()
            

        else :
            self.pwdLineEdit.clear()
            self.pwdLineEdit.setFocus()

    

class GroupTools(QDialog, Ui_GroupTools):
    def __init__(self, parent=None):
        super(GroupTools, self).__init__(parent)
        self.setupUi(self)
        self.intoOthers()

    def intoOthers(self):  # 设置槽函数
        self.show()
        self.ManagerList.clicked.connect(self.MLbtnClicked) #管理员列表
        self.PeopleGroup.clicked.connect(self.PGbtnClicked) #群成员列表
        self.ChangeManager.clicked.connect(self.CMbtnClicked) #改变群管理员
        self.ChangePeople.clicked.connect(self.CPbtnClicked) #改变群成员
    def MLbtnClicked(self):  # 点击后所发生的事
        self.managerlist = ManagerList()
        self.managerlist.show()
        self.managerlist.exec_()

    def PGbtnClicked(self):
        self.peoplegroup = PeopleList()
        self.peoplegroup.show()
        self.peoplegroup.exec_()

    def CMbtnClicked(self):
        self.changemanager = ChangeManager()
        self.changemanager.show()
        self.changemanager.exec_()

    def CPbtnClicked(self):
        self.changepeople = ChangePeople()
        self.changepeople.show()
        self.changepeople.exec_()


class PeopleList(QDialog, Ui_PeopleList):
    def __init__(self, parent=None):
        super(PeopleList, self).__init__(parent)
        self.setupUi(self)

class ManagerList(QDialog, Ui_ManagerList):
    def __init__(self, parent=None):
        super(ManagerList, self).__init__(parent)
        self.setupUi(self)

class ChangePeople(QDialog, Ui_ChangePeople):
    def __init__(self, parent=None):
        super(ChangePeople, self).__init__(parent)
        self.setupUi(self)
    #   self.ExecuteBtn.clicked.connect(self.changeP)
#   def changeP(self): #
    #   if self.Choice.currentText() == "减少群成员" : # 减少群成员
    #   else : #添加群成员




class ChangeManager(QDialog, Ui_ChangeManager):
    def __init__(self, parent=None):
        super(ChangeManager, self).__init__(parent)
        self.setupUi(self)
    #   self.ExecuteBtn.clicked.connect(self.changeM)

#   def changeM(self):
    #   if self.Choice.currentText() == "减少管理员" : #减少管理员
    #   else :




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
            # 此处需添加将用户信息录入数据库的函数 !!!
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
            #此处需添加修改数据库中用户信息的函数
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



    app = QApplication(sys.argv)

    mainwindow = mainWindow()
    loginwindow = loginWindow()

    loginwindow.show()

    if (loginwindow.exec_()== QDialog.Accepted):
        mainwindow.show()

    sys.exit(app.exec_())
