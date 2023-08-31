from PyQt5 import QtWidgets, uic
import sys

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget

from logindialog_one_ui import Ui_LoginDialog
from qt_material import apply_stylesheet

class Ui(QMainWindow, Ui_LoginDialog):
    def __init__(self, parent = None):
        super(Ui, self).__init__(parent)
        self.setupUi(self)

    def center(self):  # 定义一个函数使得窗口居中显示
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(int(newLeft), int(newTop))

app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.center()

apply_stylesheet(app, theme='light_pink.xml')
window.show()
sys.exit(app.exec())
