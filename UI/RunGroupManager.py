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
