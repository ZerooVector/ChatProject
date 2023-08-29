from PyQt5 import QtWidgets, uic
import sys

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget,QDialog

from mainwindow_ui import Ui_MainWindow
from grouptools import Ui_GroupTools  # name problem, I forget "_ui"
from peoplelist_ui import Ui_PeopleList
from managerlist_ui import Ui_ManagerList
from changepeople_ui import Ui_ChangePeople
from changemanager_ui import Ui_ChangeManager
from qt_material import apply_stylesheet

class GroupManager(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(GroupManager, self).__init__(parent)
        self.setupUi(self)
        self.intoGroupTools()
    def intoGroupTools(self): #设置槽函数
        self.show()
        self.ManageGroup.clicked.connect(self.btnClicked)

    def btnClicked(self): #点击后所发生的事
        self.grouptools = GroupTools()
        self.grouptools.show()
        self.grouptools.exec_()

    def center(self):  # 定义一个函数使得窗口居中显示
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(int(newLeft), int(newTop))



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

class ChangeManager(QDialog, Ui_ChangeManager):
    def __init__(self, parent=None):
        super(ChangeManager, self).__init__(parent)
        self.setupUi(self)


app = QtWidgets.QApplication(sys.argv)
window = GroupManager()
window.center()

apply_stylesheet(app, theme='light_pink.xml')
window.show()
sys.exit(app.exec())
