import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog,QFileDialog
from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QListWidgetItem, QTableWidgetItem,QTreeWidgetItem, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QAbstractItemView, QMessageBox

from datetime import datetime
# from PyQt5.QtCore import *QAbstractItemView.SingleSelection
from PyQt5.QtGui import QPainter,QPixmap

from UI.createGroupDialog_ui import Ui_createGroupDialog
from UI.logindialog_ui import Ui_LoginDialog
from UI.untitled_test_basic_ui import Ui_MainWindow
from UI.register_ui import Ui_Register 
from UI.information_ui import Ui_Information
from UI.Voicecall_ui import Ui_Voicecall

import sounddevice as sd
import soundfile as sf
import numpy as np 
import speech_recognition as sr
import cv2 

###########################
import socket
import time
import threading  # 导入线程模块
import os 
import ast 
# pause_event = threading.Event()
FILE_PATH = "E:/2023-2024 # 1(now)/finaltest/filesave/"
AVATAR_PATH = "E:/2023-2024 # 1(now)/finaltest/avatarsave/"
client_sock = ""
STOP_UPDATE  = False
AVATAR_DICT = {}
IP_DICT = {}
RECORDING = False 
stream = None 
audio_data = None
RECORDING2 = False 
stream2 = None 
audio_data2 = None 
FACE_UPLOAD_FLAG = 0
dataset_path = './face_dataset/' 
testset_path = './test/'
import shutil

############ tool functions ############## 
def send_msg(sock, msg):
    # 将消息编码为字节流
    msg = msg.encode('utf-8')
    # 创建固定长度的消息头，例如4个字节，包含消息长度
    msg_header = f"{len(msg):<4}".encode('utf-8')
    # 发送消息头和消息主体
    sock.sendall(msg_header + msg)

def recv_msg(sock):
    sock.setblocking(True)
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

def voice2wordchat():
    # target = msg[4:]
    global RECORDING, STOP_UPDATE, stream ,audio_data
    if RECORDING == False :
        STOP_UPDATE = True #
        RECORDING = True  
        sample_rate = 44100
        # is_recording = False
        audio_data = []
        def callback(indata, frames, time, status):
            # nonlocal audio_data
            audio_data.append(indata.copy())
        stream = sd.InputStream(callback=callback, channels=1, samplerate=sample_rate)
        stream.start()
        RECORDING = True 
        print("Recording Start!")
        return 

    if RECORDING == True:
        print("Recording Stop!")
        RECORDING = False 
        stream.stop()
        stream.close()
        file_name = 'voice2word.wav'
        audio_data = [data.flatten() for data in audio_data]
        audio_data = np.concatenate(audio_data)
        sf.write(file_name, audio_data, 44100)
        STOP_UPDATE = False 
        return
    
def voicechat():
    global RECORDING2, STOP_UPDATE, stream2 ,audio_data2
    if RECORDING2 == False :
        STOP_UPDATE = True 
        RECORDING2 = True 
        audio_data2 = []
        def callback(indata, frames, time, status):
        # nonlocal audio_data
            audio_data2.append(indata.copy())
        stream2 = sd.InputStream(callback=callback, channels=1, samplerate=44100)
        stream2.start()
        RECORDING2 = True 
        print("Start Recording")
        return 
    else :
        print("Stop Recording !")
        RECORDING2 = False 
        stream2.stop()
        stream2.close()
        file_name = 'voicechat.wav'
        audio_data2 = [data.flatten() for data in audio_data2]
        audio_data2 = np.concatenate(audio_data2)
        sf.write(file_name, audio_data2, 44100)


def CatchUsbVideo(window_name, camera_idx,dataset_path):
    face_cascade = cv2.CascadeClassifier('E:/2023-2024 # 1(now)/finaltest/haarcascade_frontalface_alt2.xml')
    cap = cv2.VideoCapture(camera_idx)
    while cap.isOpened():
        # 截取保存这一帧
        for i in range(50):
        # 持续读取新帧
            ret,frame = cap.read()
        # 显示新帧 
        cv2.imshow(window_name, frame)
        cv2.waitKey(5)
        if (i+1)%5 == 0:
            img_name = "test_{}.jpg".format(int((i-4)/5))
            cv2.imwrite(os.path.join(dataset_path, img_name), frame)
        break
    
def getAllPath(dirpath, *suffix): # tool function 
    PathArray = []
    for r, ds, fs in os.walk(dirpath):
        for fn in fs:
            if os.path.splitext(fn)[1] in suffix:
                fname = os.path.join(r, fn)
                PathArray.append(fname)
    return PathArray

def readPicSaveFace(sourcePath, targetPath,  *suffix):
    try:
        ImagePaths = getAllPath(sourcePath, *suffix)

        # 对list中图片逐一进行检查,找出其中的人脸然后写到目标文件夹下
        count = 1
        # haarcascade_frontalface_alt2.xml为库训练好的分类器文件，下载opencv，安装目录中可找到
        path = "haarcascade_frontalface_alt2.xml" # 级联分类器的地址，换成自己的
        face_cascade = cv2.CascadeClassifier(path)
        for imagePath in ImagePaths:
            # 读灰度图，减少计算
            filename = os.path.split(imagePath)[1]
            img = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)
            if type(img) != str:
                faces = face_cascade.detectMultiScale(img)
                # (x, y)代表人脸区域左上角坐标；
                # w代表人脸区域的宽度(width)；
                # h代表人脸区域的高度(height)。
                for (x, y, w, h) in faces:

                     # 设置人脸宽度大于128像素，去除较小的人脸
                     if w >= 128 and h >= 128:
                        # 扩大图片，可根据坐标调整
                        X = int(x)
                        Y = int(y)
                        W = min(int((x + w)), img.shape[1])
                        H = min(int((y + h)), img.shape[0])
                        f = cv2.resize(img[Y:H, X:W], (W - X, H - Y))
                        f = cv2.resize(f, (200, 200))
                        cv2.imwrite(targetPath + os.sep + filename, f)
                        count += 1

    except IOError:
        print("Error")

    #当try块没有出现异常的时候执行
    else:
        print('Find ' + str(count - 1) + ' faces to Destination ' + targetPath)
        
def empty_folder(folder_path):  # tool function
    shutil.rmtree(folder_path)
    # 重新创建空文件夹
    os.makedirs(folder_path)
    
def clientsendface(client_sock,address):
    if not os.path.exists(address):
        print(f"File {address} does not exist!")  # client checks the file is or not exist 
        return

    with open(address,"rb") as file :
    
        file_chunk = file.read(4096*2)
        while file_chunk:
            send_file(client_sock,file_chunk)
            file_chunk = file.read(4096*2)

def clientuploadface(sock,data,dataset_path):
    global FACE_UPLOAD_FLAG,STOP_UPDATE
    STOP_UPDATE = True 
    if not os.path.exists(dataset_path):
        os.mkdir(dataset_path)
    camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    ret, frame = camera.read()
    CatchUsbVideo("camera", 0,dataset_path)
    # 5秒后关闭窗口   
    camera.release()
    cv2.destroyAllWindows() 
    sourcePath = './face_dataset/'
    targetPath = './face_dataset_gray/'
    readPicSaveFace(sourcePath, targetPath, '.jpg', '.JPG', 'png', 'PNG')
    global FACE_UPLOAD_FLAG
    FACE_UPLOAD_FLAG = 0
    send_msg(sock,data)
    all_facefile_list = os.listdir(targetPath)
    for item in all_facefile_list:
        while FACE_UPLOAD_FLAG == 1:
            pass # 直到标记消失，则上传另一张图
        if FACE_UPLOAD_FLAG == 0:
            FACE_UPLOAD_FLAG = 1
            clientsendface(sock,targetPath + str(item))
        # response = recv_msg(sock)
        # if response == "T10+SUCCESS":
            # FACE_UPLOAD_FLAG = 0 
        break 
    empty_folder("face_dataset")
    empty_folder("face_dataset_gray")
    STOP_UPDATE = False 
    
def clientcheckface(sock,data,testset_path):
    global FACE_UPLOAD_FLAG ,STOP_UPDATE 
    STOP_UPDATE = True
    if not os.path.exists(testset_path):
        os.mkdir(testset_path)
    camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    ret, frame = camera.read()

    # 展示摄像头画面  
    CatchUsbVideo("camera", 0,testset_path)
    # 2秒后关闭窗口   
    camera.release()
    cv2.destroyAllWindows() 
    sourcePath = './test/'# 原始测试数据文件地址，换成自己的
    targetPath = './test_gray/'# 处理后的测试图片的文件存储地址
    readPicSaveFace(sourcePath, targetPath, '.jpg', '.JPG', 'png', 'PNG')
    all_facefile_list = os.listdir(targetPath)
    send_msg(sock,data)
    for item in all_facefile_list:
        while FACE_UPLOAD_FLAG == 1:
            pass # 直到标记消失，则上传另一张图
        if FACE_UPLOAD_FLAG == 0:
            FACE_UPLOAD_FLAG = 1
            clientsendface(sock,targetPath + str(item))
        # response = recv_msg(sock)
        # if response == "T10+SUCCESS":
            # FACE_UPLOAD_FLAG = 0 
        break 
    empty_folder("test")
    empty_folder("test_gray")
    STOP_UPDATE = False 
    

##########################################################
# 添加好友界面的Item填充
class customAddContactItem(QTreeWidgetItem):
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

        self.isGroup = False
        parent_item = self.parent()
        tree_widget = self.treeWidget()
        index = -1
        self.nameLabel.text()
        
        for i in range(tree_widget.topLevelItemCount()):
            if parent_item == tree_widget.topLevelItem(i):
                index = i
                break
        
        if index == 1:
            self.isGroup = True
        

        # print(self.isGroupGroup == True)
        if self.isGroup == False :
            str_msg = "F01+" + self.name 
            send_msg(client_sock,str_msg)
        else :
            str_msg = "G04+" + self.name 
            send_msg(client_sock,str_msg)




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
        self.name = name
        self.img = img
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
        self.deleteContactBtn.setStyleSheet("border: none; \
                                            background-color: white;\
                                             background-image: url(/home/jh/code/QtDemo/Project_Github/ChatProject/client_Trial/backgroundImg/deleteContactBtn.png);")
        self.deleteContactBtn.setText("Delete")
        # 槽函数，当按钮被点击时删除该项
        self.deleteContactBtn.clicked.connect(self.deleteContact)
        self.deleteContactBtn.hide()

        # 设置邀请好友按钮
        self.inviteFriendBtn = QPushButton()
        self.inviteFriendBtn.setText("Invite")
        self.inviteFriendBtn.clicked.connect(self.inviteFriend)
        self.inviteFriendBtn.hide()
        self.inviteGroupName = None

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
    


        self.isGroup =False
        if  index == 1:
            self.isGroup = True
        # 发送信号从数据库删除联系人或群组

    def inviteFriend(self):
        # self.name self.inviteGroupName 可用
        str_msg = "G24+" + self.inviteGroupName + "||-||" + self.name 
        send_msg(client_sock,str_msg)
        pass


    def set_distribution(self):
        # 设置布局
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.avatorLabel)
        self.hbox.addWidget(self.nameLabel)
        self.hbox.addWidget(self.deleteContactBtn)
        self.hbox.addWidget(self.inviteFriendBtn)
        self.hbox.addStretch(1)     # 抄来的 不知道什么意思
        # 布局添加到widget
        self.widget.setLayout(self.hbox)

class customGroupMemberItem(QWidget):
    def __init__(self, name, img, isManager = False, isBoss = False, parent = None):
        super().__init__(parent)
        
        button_style = """
            QPushButton {
                background-color: #AD8B73;
                color: white;
                border-radius: 5px;
                padding: 3px;
            }
            
            QPushButton:hover {
                background-color: #9E8B8E;}
            """
        self.name = name
        self.img = img
        self.isManager = isManager
        self.isBoss = isBoss
        self.groupName = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.avatarLabel  = QLabel()
        self.avatarLabel.setPixmap(QPixmap(img).scaledToWidth(100))
        self.layout.addWidget(self.avatarLabel)

        self.nameLabel = QLabel(name)
        self.layout.addWidget(self.nameLabel)
        
        self.addManagerBtn = QPushButton("addManager")
        self.addManagerBtn.setStyleSheet(button_style)
        self.addManagerBtn.clicked.connect(self.addManager)
        self.addManagerBtn.hide()
        self.removeMemberBtn = QPushButton("removeMember")
        self.removeMemberBtn.setStyleSheet(button_style)
        self.removeMemberBtn.clicked.connect(self.removeMember)
        self.removeMemberBtn.hide()
        self.addManagerBtn.setEnabled(False)
        self.removeMemberBtn.setEnabled(False)
        
        self.layout.addWidget(self.addManagerBtn)
        self.layout.addWidget(self.removeMemberBtn)


        # self.setSizeHint(self.widget.sizeHint())
        # self.setData(Qt.displayRole, widget)

    # 融合了添加管理者和删除管理者
    def addManager(self):
        # 添加
        if self.addManagerBtn.text() == "addManager":
            str_msg = "G22+" + self.groupName + "||-||" + self.name 
            send_msg(client_sock,str_msg)
            pass
        
        # 删除
        else:
            str_msg = "G23+" + self.groupName + "||-||" + self.name 
            send_msg(client_sock,str_msg)
            
            pass
        # 如果成功了 将UPDATEGROUP全局变量设置为TRUE
        global UPDATEGROUP
        UPDATEGROUP = True
        
    # 写删除群成员的逻辑
    def removeMember(self):
        # self.name 成员名字 self.groupName群名字
        str_msg = "G08+" + self.groupName + "||-||" + self.name 
        send_msg(client_sock,str_msg)
        # 如果成功了 将UPDATEGROUP全局变量设置为TRUE
        global UPDATEGROUP
        UPDATEGROUP = True
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

class customGroupValidationItem(QListWidgetItem):
    def __init__(self, name, dateTime, isSolved = False, isAccepted = None):
        super().__init__()

        button_style = """
            QPushButton {
                background-color: #AD8B73;
                color: white;
                border-radius: 5px;
                padding: 7px;
            }
            
            QPushButton:hover {
                background-color: #9E8B8E;
            }
            
            QPushButton:pressed {
                background-color: #379683;
            }
        """
        self.name = name
        self.dateTime = dateTime
        self.isSolved = isSolved 
        self.isAccepted = isAccepted
        self.groupName = None

        self.timeLabel = QLabel(self.dateTime.strftime("%Y-%m-%d, %H:%M:%S"))
        self.validationMsgLabel = QLabel(
            "\"{}\" wants to join your group" .format(self.name)
        )
        self.validationMsgLabel.setStyleSheet("background-color : #CEAB93;\
                                            border-radius: 10px;\
                                            padding: 10px")
        self.allowJoinBtn = QPushButton()
        self.allowJoinBtn.setStyleSheet(button_style)
        self.allowJoinBtn.setText("Allow")
        self.allowJoinBtn.clicked.connect(self.allowJoin)
        self.rejectJoinBtn = QPushButton()
        self.rejectJoinBtn.setStyleSheet(button_style)
        self.rejectJoinBtn.setText("Reject")
        self.rejectJoinBtn.clicked.connect(self.rejectJoin)
        self.stateBtn = QPushButton()
        self.stateBtn.setStyleSheet(button_style)
        self.stateBtn.setEnabled(False)
        self.stateBtn.hide()
        if self.isSolved :
            if self.isAccepted:
                self.stateBtn.setText("Already Accpeted")
            else:
                self.stateBtn.setText("Already Rejected")
        
        # 设置item_widget的布局，写成函数便于继承重写
        self.setDistribution()
        # 设置自定义sizehint，否则无法显示 抄来的 不知道为什么
        self.setSizeHint(self.widget.sizeHint())

    def setDistribution(self):
        self.widget = QWidget()
        self.layout = QVBoxLayout()

        self.downWidget = QWidget()
        self.downLayout = QHBoxLayout()
        self.downLayout.addWidget(self.validationMsgLabel)
        self.downLayout.addWidget(self.allowJoinBtn)
        self.downLayout.addWidget(self.rejectJoinBtn)
        self.downLayout.addWidget(self.stateBtn)
        # 默认为显示未解决验证，若给已验证的信息，则如下
        if self.isSolved:
            self.allowJoinBtn.hide()
            self.rejectJoinBtn.hide()
            self.stateBtn.show()
        self.downWidget.setLayout(self.downLayout)

        self.layout.addWidget(self.timeLabel)
        self.layout.addWidget(self.downWidget)
        self.widget.setLayout(self.layout)

    # 拒绝加入
    def rejectJoin(self):
        str_msg = "G06+"+  self.groupName + "||-||" + self.name + "||-||" +"N"
        send_msg(client_sock,str_msg)
        # self.name self.groupName 可用
        # 如果成功了 将UPDATEGROUP全局变量设置为TRUE
        global UPDATEGROUP
        UPDATEGROUP = True
        pass

    def allowJoin(self):
        str_msg = "G06+"+  self.groupName + "||-||" + self.name + "||-||" +"Y"
        send_msg(client_sock,str_msg)
        # self.name self.groupName 可用
        # 如果成功了 将UPDATEGROUP全局变量设置为TRUE
        global UPDATEGROUP
        UPDATEGROUP = True
        pass

# 聊天列表界面的Item填充
class customChatItem(QListWidgetItem):
    
    img_size = (50, 50)
    def __init__(self, name, img, all_msg, isGroup = False):
        super().__init__()

        # self.setStyleSheet()

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
        if isFile:
            if content[-3: ] in ["WAV", "wav", "Wav"]:
                isVoiceMsg = True

        self.content = content 
        self.name = name 
        self.date = date 
        self.is_unread = is_unread
        self.isFile = isFile 
        self.isVoiceMsg = isVoiceMsg 



        # self.setStyleSheet("background-color: red;\
        #                     border-radius: 10px\
        #                    padding: 10px")


        
        msgTitle = QLabel(name +":  at " + date.strftime("%Y-%m-%d, %H:%M:%S") )
        
        msgLabel = QLabel(content)
        msgLabel.setStyleSheet("background-color: #CEAB93;\
                            border-radius: 10px;\
                           padding: 10px")
        msgLabel.setWordWrap(True)

        recvFileBtn = QPushButton()
        if isFile :
            if isVoiceMsg:
                recvFileBtn.setText("Play")
                recvFileBtn.clicked.connect(self.playVoiceMsg)
            else:   
                recvFileBtn.setText("receiveFILE")
                recvFileBtn.clicked.connect(self.receiveFIle)

            # self.clicked.connect(recvFileBtn.clicked())

        # if isVoiceMsg:
            
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
            # USERNAME
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
        global UPDATEGROUP

        send_msg(client_sock,"F03+")
        response = recv_msg(client_sock)
        response = ast.literal_eval(response)
        print(response)
        friend_list = []
        for item in response:
            friend_list.append(response[0][0])
        if len(friend_list) > 0:
            self.contactFriendList_2.addItems(friend_list)
        
        # 设置标题
        self.setWindowTitle("BlazIngChaT")
        # 好友列表的设置
        self.userName = userName
        self.contactListStack.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.contactListStack_showPageAdd = False
        # 限制列表只能单个选择
        # self.addFriendList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.chatMsgList.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.contactFriendList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.contactsList.setSelectionMode(QAbstractItemView.SingleSelection)
        # showContactPage配置
        self.showContactPage.hide()
        #  createGrpouBtn配置
        self.setCreateGroupBtn()
        self.createGroupBtn.clicked.connect(self.createGroup)
        # groupMemberPage的配置
        self.setGroupMemberPage()
        # 设置chatMsgBrowser为气泡聊天界面显示
        self.setChatMsgBrowser()
        # GPT人物设置界面的配置
        self.characterSettingPage.hide()
        self.confirmCharacterBtn.clicked.connect(self.setCharacter)
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
        # 槽函数 上传人脸
        self.uploadFaceBtn.clicked.connect(self.uploadFace)

        #---
        # 槽函数 同意拒绝好友申请
        self.acceptBtn.clicked.connect(self.accept_friend_request)
        self.rejectBtn.clicked.connect(self.reject_friend_request)
        # 槽函数 进入语音聊天
        # self.VoiceCallBtn.clicked.connect(self.intoVoicecall)
        # 槽函数 语音转文字
        self.TransformBtn.clicked.connect(self.transform)
        # 槽函数 发送语音
        self.sendVoiceBtn.clicked.connect(self.sendvoice)
        self.tabWidget.currentChanged['int'].connect(self.tabfun)
        #---


        # 槽函数 显示群信息界面
        self.contactsList.itemSelectionChanged.connect(self.showGroupInfo)
        # cao函数 显示群管理界面
        self.manageGroupMemberOn = False
        self.manageGroupMemberBtn.clicked.connect(self.manageGroupMember)
        # 槽函数 群聊邀请好友
        self.inviteFriendOn = False
        self.members = None
        self.inviteGroupMemberBtn.clicked.connect(self.inviteGroupMember)
        # 槽函数 退出群聊
        self.quitGroupBtn.clicked.connect(self.quitGroup)

        self.setMainWindow()
        # ------------以上为Ui设置

        # 获取个人信息
        self.loadUserInfo(userName)
        #展示好友列表和聊天列表 
        self.loadChatList()
        # self.loadContactList()
        self.loadContactsList()
        self.showMsgPage.hide()
    def tabfun(self):
        global STOP_UPDATE
        STOP_UPDATE = True 
        self.contactFriendList_2.clear()
        send_msg(client_sock,"F03+")
        response = recv_msg(client_sock)
        response = ast.literal_eval(response)
        print(response)
        friend_list = []
        for item in response:
            friend_list.append(item[0])
        if len(friend_list) > 0:
            # print(friend_list)
            self.contactFriendList_2.addItems(friend_list)
        STOP_UPDATE = False
        # self.contactFriendList_2.addItems(friend_list)
        
    # 在这个函数完成大部分的样式设置
    def setMainWindow(self):
        # self.centralwidget.setStyleSheet ("\
        #                         background-image: url(/home/jh/code/QtDemo/Project_Github/ChatProject/client_Trial/backgroundImg/BGMainWindow.png)\
        #                     ")
        button_style = """
            QPushButton {
                background-color: #AD8B73;
                color: white;
                border-radius: 5px;
                padding: 7px;
            }
            
            QPushButton:hover {
                background-color: #9E8B8E;
            }
            
            QPushButton:pressed {
                background-color: #379683;
            }
        """
        list_widget_style = """
            QListWidget {
                background-color: #fffbe9;
                border: none;
            }
            
            QListWidget::item {
                background-color: #CEAB93;
                color: #333333;
                padding: 5px;
                border-bottom: 1px solid #DDDDDD;
            }
            
            QListWidget::item:selected {
                background-color: #FFFBE9;
                color: white;
            }
        """
        tree_widget_style = """
            QTreeWidget {
                background-color: #fffbe9;
                border: none;
            }
            
            QTreeWidget::item {
                background-color: #CEAB93;
                color: white;
                padding: 5px;
            }
            
            QTreeWidget::item:selected {
                background-color: #fffbe9;
                color: black;
            }
        """
        
        self.searchAccountBtn.setStyleSheet("border: none; \
                                            background-color: white;\
                                             background-image: url(/home/jh/code/QtDemo/Project_Github/ChatProject/client_Trial/backgroundImg/searchAccountBtn.png);")
        self.addAccountBtn.setStyleSheet("border: none; \
                                            background-color: white;\
                                             background-image: url(/home/jh/code/QtDemo/Project_Github/ChatProject/client_Trial/backgroundImg/addAccountBtn.png);")
        self.pushButton.setStyleSheet(button_style)
        self.sendFileBtn.setStyleSheet(button_style)
        self.sendVoiceBtn.setStyleSheet(button_style)
        self.TransformBtn.setStyleSheet(button_style)
        self.VoiceCallBtn.setStyleSheet(button_style)
        self.chatSendBtn.setStyleSheet(button_style)
        self.manageGroupMemberBtn.setStyleSheet(button_style)
        self.quitGroupBtn.setStyleSheet(button_style)
        self.inviteGroupMemberBtn.setStyleSheet(button_style)
        self.manageContactsBtn.setStyleSheet(button_style)
        self.uploadAvatarBtn.setStyleSheet(button_style)
        self.ChangeInformation.setStyleSheet(button_style)
        self.uploadFaceBtn.setStyleSheet(button_style)
        self.rejectBtn.setStyleSheet(button_style)
        self.acceptBtn.setStyleSheet(button_style)
        self.manageContactsBtn_2.setStyleSheet(button_style)


        self.chatMsgList.setStyleSheet(list_widget_style)
        self.contactsList.setStyleSheet(tree_widget_style)
        self.addContactList.setStyleSheet(tree_widget_style)
        # self.contactsList.topLevelItem(0).setStyleSheet("\
        #         QTreeWidgetItem::item:selected {\
        #         background-color: #fffbe9;\
        #         color: black;\
        #     }")
        self.groupMemberPage.setStyleSheet("background-color: #FFFBE9")
        self.groupValidationPage.setStyleSheet("background-color: #FFFBE9")



    # 上传人脸信息
    def uploadFace(self):
        print("uploadFace")
        str_msg = "R00+"
        clientuploadface(client_sock,str_msg,dataset_path) 
        # self.userInfo["userNameInfo"]
        pass


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
    
    # groupMemberPage的一些补充设置
    def setGroupMemberPage(self):
        self.groupMemberPage\
            .verticalHeader().setDefaultSectionSize(150)
        self.groupMemberPage\
            .horizontalHeader().setDefaultSectionSize(120)
        self.groupMemberPage\
            .verticalHeader().setVisible(False)
        self.groupMemberPage\
            .horizontalHeader().setVisible(False)
        self.groupMemberPage\
            .setStyleSheet("QTableWidget { border: none; }")

    # 管理群组按键的槽函数
    def manageGroupMember(self):
        if self.manageGroupMemberOn == False:
            for row in range(self.groupMemberPage.rowCount()):
                for column in range(self.groupMemberPage.columnCount()):
                    item = self.groupMemberPage.cellWidget(row, column)
                    if item == None:
                        break
                    else :
                        item.addManagerBtn.show()
                        item.removeMemberBtn.show()
        else:
            for row in range(self.groupMemberPage.rowCount()):
                for column in range(self.groupMemberPage.columnCount()):
                    item = self.groupMemberPage.cellWidget(row, column)
                    if item == None:
                        break
                    else :
                        item.addManagerBtn.hide()
                        item.removeMemberBtn.hide()
        self.manageGroupMemberOn = not self.manageGroupMemberOn

    # 显示群信息界面
    def showGroupInfo(self):
        items:customContactItem = self.contactsList.selectedItems()
        item = items[0]
        self.manageContactsOn = False
        # 当所选择的是群组时，显示群信息界面
        if item.parent() == self.contactsList.topLevelItem(1):
            self.showContactPage.show()
            self.showContactPage.setTitle(item.name)

            
            # self.groupApplyPage.clear()
            self.loadGroupMember()
            self.loadGroupValidation()

        else :
            self.showContactPage.hide()

    # 显示群成员界面
    def loadGroupMember(self ):
        global STOP_UPDATE
        STOP_UPDATE = True 
        # 在此处获服务器信息 希望得到的信息类似如下 并且无脑设了整个类上的全局变量
        groupName = self.showContactPage.title()
        send_msg(client_sock,"G20+"+groupName)
        response = ast.literal_eval(recv_msg(client_sock))
        bosses = [] 
        managers = [] 
        for item in response:
            if item["isBoss"] == True :
                bosses.append(item["name"])
            if item["isManager"] == True :
                managers.append(item["name"])
            item["img"] = AVATAR_DICT[item["name"]]
        STOP_UPDATE = False 
            
        boss = bosses[0] 
        members = response 
        print("---------------------GROUP---------------------")
        print(boss)
        print(managers)

        # members = [member1, member2, member3]
        self.members = members
        self.managers = managers
        self.boss = boss
        
        self.groupMemberPage.clear()
        self.groupMemberPage.setColumnCount(5)
        size = len(members)
        self.groupMemberPage.setRowCount(size // 5 if size % 5 == 0 else size //5 + 1 )
        for row in range(self.groupMemberPage.rowCount()):
            for column in range(self.groupMemberPage.columnCount()):
                index = row*5 + column
                if index >= size:
                    break
                item = customGroupMemberItem(** members[index])
                item.groupName = self.showContactPage.title()

                # 删除逻辑
                # 若用户是管理者，则可以删除非管理者
                if self.userInfo["userNameInfo"] in managers:
                    # 若是群主 所有人随便删
                    if self.userInfo["userNameInfo"] == boss and index > 0:
                        item.removeMemberBtn.setEnabled(True)
                    # 单纯的管理者只能删普通用户
                    else:
                        if  members[index]["name"] not in managers and \
                            self.userInfo["userNameInfo"] != members[index]["name"]:
                            item.removeMemberBtn.setEnabled(True)
                # 若用户是群主，管理员设置
                if self.userInfo["userNameInfo"] == boss:
                    if members[index]["name"] in managers and index > 0:
                        item.addManagerBtn.setText("removeManager")
                        item.addManagerBtn.setEnabled(True)
                    elif index > 0:
                        item.addManagerBtn.setEnabled(True)

                self.groupMemberPage.setCellWidget(row, column, item)

    # 邀请群成员的switch函数
    def inviteGroupMember(self):
        member_names = [d.get('name') for d in self.members]
        friendFather = self.contactsList.topLevelItem(0)
        for i in range(friendFather.childCount()):
            item =  friendFather.child(i)
            item.inviteGroupName = self.showContactPage.title()
            if self.inviteFriendOn == False: 
                item.inviteGourpName = self.showContactPage.title()
                if item.name in member_names:
                    item.inviteFriendBtn.setEnabled(False)
                else:
                    item.inviteFriendBtn.setEnabled(True)
                item.inviteFriendBtn.show()
            else:
                item.inviteFriendBtn.hide()
        self.inviteFriendOn = not self.inviteFriendOn

    # 载入群聊的验证消息
    def  loadGroupValidation(self):
        global STOP_UPDATE
        STOP_UPDATE  = True 
        self.groupValidationPage.clear()
        # 期望在此处获得信息如下
        groupName = self.showContactPage.title()
        str_msg = "G21+" + groupName 
        send_msg(client_sock,str_msg)
        response = ast.literal_eval(recv_msg(client_sock))
        for item in response:
            item["dateTime"] = datetime.strptime(item["dateTime"], '%Y-%m-%d %H:%M:%S.%f')
        validations = response
        STOP_UPDATE = False 
        # validations = [validation1, validation2]

        self.groupName = self.showContactPage.title()
        size = len(validations)
        for i in range(size):
            item = customGroupValidationItem(**validations[i])
            item.groupName = self.showContactPage.title()
            self.groupValidationPage.insertItem(-1, item)
            self.groupValidationPage.setItemWidget(item, item.widget)

    # 发送退群消息给服务器
    def quitGroup(self):
        self.groupName = self.showContactPage.title()
        str_msg = "G41+" + self.groupName 
        send_msg(client_sock,str_msg)
        pass
    
    def createGroup(self):
        print("clicked")
        dialog = createGroupDialog()
        
        dialog.show()
        dialog.exec_()

    # 设置创建群按钮的样式
    def setCreateGroupBtn(self):
        self.createGroupBtn.setStyleSheet("QPushButton { border: none; \
                                    color: blue; \
                                    text-decoration: underline; }")

    # 在新界面清除Browser的内容    
    def chatMsgBrowserClear(self):
        container_layout = self.chatMsgBrowser.widget().layout()
        while container_layout.count() > 0:
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

        msg_str = "U99+"
        send_msg(client_sock,msg_str)
        response = ast.literal_eval(recv_msg(client_sock))
        print(response)
        friends = response["friends"]
        # friends.append(user_response[0][0])
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

    # 用户向服务器上传文件
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


    # 设置人设
    def setCharacter(self):
        # 可能用的参数 self.userInfo["userNameInfo"]
        msg = self.characterSettingEdit.text()
        # 可以沿用发送消息


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
            if item.name not in ["Customized GPT","Little OP","Crazy Dave"] :
                str_msg = "C00+" + str(item.name) + "||-||" + msg 
                send_msg(client_sock,str_msg)
            else :
                str_msg = "A02+" + str(item.name) + "||-||" + msg 
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


        #GPT人设的特殊功能
        if cur_item.nameLabel.text() == "Customized GPT" :
            self.characterSettingPage.show()

        if self.last_item != None and self.last_item.nameLabel.text() == "Customized GPT"\
            and cur_item.nameLabel.text() != "Customized GPT":
            self.characterSettingPage.hide()

        # 设置显示界面
        # self.chatMsgBrowserClear()
        self.showMsg(cur_item)
        self.showMsgPage.show()
        self.last_item = cur_item

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
                                                                        name=single_msg[0], date=single_msg[3],\
                                                                        is_left=is_left, isFile= single_msg[4]))
            # QTimer.singleShot(10, 
            #                   self.chatMsgBrowser.verticalScrollBar().\
            #                     setValue(self.chatMsgBrowser.verticalScrollBar().maximum()))
            self.chatMsgBrowser.verticalScrollBar().\
                setValue(self.chatMsgBrowser.verticalScrollBar().maximum())
            
    # 搜索好友并添加
    def searchAccount(self):
        if self.contactListStack_showPageAdd == True:
            #该if语句下做添加好友返回搜索结果的界面
            STOP_UPDATE = True
            friendFather = self.addContactList.topLevelItem(0)
            groupFather = self.addContactList.topLevelItem(1)
            friendFather.setExpanded(True)
            groupFather.setExpanded(True)
            # 先晴空
            str_msg  = "F00+" + self.contactSearchEdit.text() 
            send_msg(client_sock,str_msg)
            respond = recv_msg(client_sock)
            print(respond)
            respond = ast.literal_eval(respond)
            ans_searchFriend = []
            for item in respond["friends"]:
                ans_searchFriend.append((item,AVATAR_DICT[item]))
            
            ans_searchGroup = [] 
            for item in respond["groups"]:
                ans_searchGroup.append((item,AVATAR_DICT[item]))
            STOP_UPDATE = False 

            for i in range(friendFather.childCount()):
                friendFather.takeChild(i)
            for i in range(groupFather.childCount()):
                groupFather.takeChild(i)
            #这两个列表应该是服务器返回的
            # ans_searchFriend = [('A', './pic.jpg'), ('Anne', './pic.jpg')]
            # ans_searchGroup = [('A', './pic.jpg'), ('Anne', "./pic.jpg")]

            for i in range(len(ans_searchFriend)):
                item = customAddContactItem(name=ans_searchFriend[i][0], img=ans_searchFriend[i][1])
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
        friend_list = friend_and_group_dict["friends"] + ["Customized GPT","Little OP","Crazy Dave"] 
        group_list = friend_and_group_dict["groups"]

        # 接下来开始逐个人拉取信息，生成对应的消息列表
        lsFriend = [] 
        for item in friend_list:
            send_msg(client_sock,"U02+"+item)
            response = ast.literal_eval(recv_msg(client_sock))
            all_msg = [] 
            print(response)
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
            print(response)
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

        item = QTreeWidgetItem()

    # send_msg(client_sock,"F03+")
    # response = recv_msg(client_sock)
    # responce = ast.literal_eval(response)
    # if len(response) > 0:
    #     self.contactFriendList_2.addItems(response)

    # 接受好友请求
    def accept_friend_request(self):
        selected_item = self.contactFriendList_2.currentItem()
        if selected_item:
            friend_request = selected_item.text()
            # 从列表框和列表中移除好友申请
            self.contactFriendList_2.takeItem(self.contactFriendList_2.row(selected_item))
            str_msg = "F05+" + friend_request + "||-||" + "Y"
            send_msg(client_sock,str_msg)
            
            # self.friend_requests.remove(friend_request)
            # TODO: 执行同意操作的逻辑
    #拒拒绝好友请求
    def reject_friend_request(self):
        selected_item = self.contactFriendList_2.currentItem()
        if selected_item:
            friend_request = selected_item.text()
            # 从列表框和列表中移除好友申请
            self.contactFriendList_2.takeItem(self.contactFriendList_2.row(selected_item))
            
            str_msg = "F05+" + friend_request + "||-||" + "N"
            send_msg(client_sock,str_msg)
            # self.friend_requests.remove(friend_request)
            # TODO: 执行拒绝操作的逻辑
    # 打开语音通话
    def intoVoicecall(self): #进入语音聊天
        self.call = Voicecall()
        str = "用户名" # TODO str为你所对话的用户名
        self.call.name.setText("您正在与"+str+"语音通话中")
        self.call.show()
        self.call.exec_()
    #语音转文字
    def transform(self):
        print("button pressed")
        global RECORDING 
        if RECORDING == False :
            voice2wordchat() 
        else :
            voice2wordchat()
            recognizer = sr.Recognizer()
            file_path = "voice2word.wav"  # 音频文件路径
            with sr.AudioFile(file_path) as source:
                audio = recognizer.record(source)  # 从音频文件中读取音频数据
                try:
                    text = recognizer.recognize_google(audio,language='zh-CN')  # 将语言设置为中文
                    print("Text from audio: {}".format(text))
                except sr.UnknownValueError:
                    print("Unable to recognize speech")
                    text = ""
                except sr.RequestError as e:
                    print("Error: {}".format(e))
                    text = ""

            self.chatMsgEdit.setText(text)

    def sendvoice(self): # 发送语音
        print("Button Pressed")
        if RECORDING2 == False :
            voicechat()
        else :
            voicechat()
            global STOP_UPDATE
            STOP_UPDATE = True
            items = self.chatMsgList.selectedItems()
            item = items[0] 
            if item.isGroup == True :
                str_msg = "T04+" + str(item.name) + "||-||" + str("./voicechat.wav") + "||-||" + "groupaudiofile"
                clientsendfile(client_sock,str_msg)
            else :
                str_msg = "T02+" + str(item.name) + "||-||" + str("./voicechat.wav") + "||-||" + "audiofile"
                clientsendfile(client_sock,str_msg)
            STOP_UPDATE = False 
            


class Voicecall(QDialog, Ui_Voicecall):
    def __init__(self, parent=None):
        super(Voicecall, self).__init__(parent)
        self.setupUi(self)
        self.DownBtn.clicked.connect(self.stopcall)

    def stopcall(self):
        # TODO 添加挂断电话的逻辑
        self.close()





# 更新窗口的触发器
class mainWindowUpdater():
    def __init__(self, mainwindow:mainWindow) -> None:
        self.mainwindow = mainwindow
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateMainWindow)
        self.timer.start(5000)# 5 s

    def updateMainWindow(self):
        global IP_DICT

        if STOP_UPDATE == False:
            # print("updateCalled")
            # send_msg(client_sock,"IPGT")
            # ip_res = ast.literal_eval(recv_msg(client_sock))
            # IP_DICT = ip_res

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

        # if updateContacts():
        global UPDATEGROUP
        if UPDATEGROUP:
            mainwindow.showGroupInfo()
            UPDATEGROUP = False

        self.mainwindow.loadContactsList()



        
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

        self.faceBtn.clicked.connect(self.useface)

   #    self.faceBtn.clicked.connect(self.useface)
        self.setLoginDialog()


#     def setLoginDialog(self):
#             line_edit_style = """
#             QLineEdit {
#                 border: 2px solid #DF7163;
#                 border-radius: 5px;
#                 padding: 5px;
#             }
            
#             QLineEdit:focus {
#                 border-color: #45a049;
#             }
#             """ 
#             button_style = """
#                         QPushButton {
#                             background-color: #A6A5C4;
#                             color: white;
#                             border-radius: 5px;
#                             padding: 10px;
#                         }
                        
#                         QPushButton:hover {
#                             background-color: #9E8B8E;
#                         }
                        
#                         QPushButton:pressed {
#                             background-color: #379683;
#                         }
#                 """
#             self.usrLineEdit.setStyleSheet(line_edit_style)
#             self.pwdLineEdit.setStyleSheet(line_edit_style)

#             self.loginBtn.setStyleSheet(button_style)


    def useface(self):
        str_msg = "R01+"+ self.usrLineEdit.text()
        clientcheckface(client_sock,str_msg,testset_path)
        response = recv_msg(client_sock)
        pass
        # self.usrLineEdit.text() 是用户名
        # TODO 人脸识别
        if self.usrLineEdit.text() == "":
         msg_box = QMessageBox(QMessageBox.Critical, '错误', '用户名不得为空')
         msg_box.exec_()
        elif response == "RECOERR":
         msg_box = QMessageBox(QMessageBox.Critical, '错误', '用户未录入人脸')
         msg_box.exec_()
        elif response == "RECOFAIL":
         msg_box = QMessageBox(QMessageBox.Critical, '错误', '人脸识别失败')
         msg_box.exec_()
        else:
          self.userName = self.usrLineEdit.text()
          self.accept()
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


class createGroupDialog(QDialog, Ui_createGroupDialog):
    def __init__(self, parent = None):
        super(createGroupDialog, self).__init__(parent)
        self.setupUi(self)
        self.confirmBtn.setEnabled(False)
        self.confirmBtn.clicked.connect(self.createGroup)
        self.lineEdit.textEdited.connect(self.enableConfirm)

    def enableConfirm(self):
        self.confirmBtn.setEnabled(True)

    def createGroup(self):
        groupName = self.lineEdit.text()
        str_msg = "G00+" + groupName + "||-||" + groupName + "||-||" + "[]"
        send_msg(client_sock,str_msg)




if __name__ == '__main__':
    # global client_sock
    SERVER_IP = "192.168.43.4" 
    SERVER_PORT = 12345
    BUFFER_SIZE = 1024

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_sock.connect((SERVER_IP, SERVER_PORT))
    except socket.error as e:
        print("Connection failed! Error:", str(e))
        client_sock.close()
        exit()



    UPDATEGROUP =False

    app = QApplication(sys.argv)

    loginwindow = loginWindow()

    loginwindow.show()

    if (loginwindow.exec_()== QDialog.Accepted):
        
        mainwindow = mainWindow(userName=loginwindow.userName)
        updater = mainWindowUpdater(mainwindow)
        mainwindow.show()

    sys.exit(app.exec_())

   # 新消息在前，旧消息在后 