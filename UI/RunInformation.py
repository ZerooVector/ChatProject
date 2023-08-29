from PyQt5 import QtWidgets, uic
import sys

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget,QDialog, QMessageBox
from information_ui import Ui_Information

from qt_material import apply_stylesheet


class Information(QDialog, Ui_Information):
    def __init__(self, parent = None):
        super(Information, self).__init__(parent)
        self.setupUi(self)
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
            msg_box = QMessageBox(QMessageBox.Information, '正确', '修改成功')
            msg_box.exec_()
            self.close()

app = QtWidgets.QApplication(sys.argv)
window = Information()
apply_stylesheet(app, theme='light_pink.xml')
window.show()
sys.exit(app.exec())