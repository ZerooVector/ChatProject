import sys
import PyQt5
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 创建一个QWidget
    w = QWidget()
    # 设置标题
    w.setWindowTitle("看看我图标帅吗")
    # 设置图标
    w.setWindowIcon(QIcon('img.png'))
    # 显示QWidget
    w.show()

    app.exec()
