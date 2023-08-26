import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog
from PyQt5 import uic
from PyQt5.QtWidgets import QListWidgetItem, QLabel, QHBoxLayout, QVBoxLayout
# from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter,QPixmap

from logindialog_ui import Ui_LoginDialog
from untitled_test_basic_ui import Ui_MainWindow
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










# Contact页面好友用户ListWidget的填充 自定义Item
class customContactQlistWidgetItem(QListWidgetItem):
    # 规定头像大小为（50,50）
    img_size = (50, 50)
    def __init__(self, name, img,):
        super().__init__()
        self.widget = QWidget()
        # 显示名字
        self.nameLabel = QLabel()
        self.nameLabel.setText(name)

        print(name, img)
        # 设置图像label
        self.avatorLabel = QLabel()
        #设置图像源于图像大小的函数
        self.avatorLabel.setPixmap(QPixmap(img).scaled(50, 50))
        
        # 设置item_widget的布局，写成函数便于继承重写
        self.set_distribution()

        # 设置自定义sizehint，否则无法显示 抄来的 不知道为什么
        self.setSizeHint(self.widget.sizeHint())

    def set_distribution(self):
        # 设置布局
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.avatorLabel)
        self.hbox.addWidget(self.nameLabel)
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
        # self.loadChatList()
        self.loadContactList()

# unfinished
    # def loadChatList(self):
    #     lsFriend = [("A", "./pic.jpg", "hi, what's up"),("B", "./pic.jpg", "hi, what's up")]
        
    #     friend_size = 2

    #     for i in range(friend_size):
    #         item = customChatQlistWidgetItem('')


    def loadContactList(self):
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
        #     self.accept()
            

        else :
            self.pwdLineEdit.clear()
            self.pwdLineEdit.setFocus()



if __name__ == '__main__':

    # global client_sock

    SERVER_IP = "127.0.0.1" 
    SERVER_PORT = 10020
    BUFFER_SIZE = 1024

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_sock.connect((SERVER_IP, SERVER_PORT))
    except socket.error as e:
        print("Connection failed! Error:", str(e))
        client_sock.close()
        exit()


    app = QApplication(sys.argv)

    mainwindow = mainWindow()
    loginwindow = loginWindow()

    loginwindow.show()

    if (loginwindow.exec_()== QDialog.Accepted):
        mainwindow.show()

    sys.exit(app.exec_())