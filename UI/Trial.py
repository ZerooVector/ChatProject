import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QDialog
from PyQt5 import uic,
from PyQt5.QtWidgets import QListWidgetItem

from logindialog_ui import Ui_LoginDialog
from untitled_test_basic_ui import Ui_MainWindow

class mainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(mainWindow, self).__init__(parent)
        self.setupUi(self)
        self.loadContactList()

    def loadContactList(self):
        

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
            print(self.exec_())
            print(QDialog.Accepted)
            

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