import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog
from PyQt5 import uic
from PyQt5.QtWidgets import QListWidgetItem, QLabel, QHBoxLayout, QVBoxLayout
# from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter,QPixmap

from logindialog_ui import Ui_LoginDialog
from untitled_test_basic_ui import Ui_MainWindow




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

        if self.usrLineEdit.text() == "123" and \
            self.pwdLineEdit.text() == "123":
            self.matched = True
            self.accept()
            

        else :
            self.pwdLineEdit.clear()
            self.pwdLineEdit.setFocus()



if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainwindow = mainWindow()
    loginwindow = loginWindow()

    loginwindow.show()

    if (loginwindow.exec_()== QDialog.Accepted):
        mainwindow.show()

    sys.exit(app.exec_())