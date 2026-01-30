import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont
from PyQt5 import QtCore,QtGui,QtWidgets
from first import MainWindow2
from second import MainWindow3

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # 设置窗口大小和标题
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2560, 1600)   #选择窗口大小

        # 设置背景图片
        
        palette = QtGui.QPalette()
        pixmap = QtGui.QPixmap("07.jpg")
        pixmap = pixmap.scaled(MainWindow.size(), QtCore.Qt.IgnoreAspectRatio)
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        MainWindow.setPalette(palette)
        self.label_image = QtWidgets.QLabel(MainWindow)
        self.label_image.setGeometry(QtCore.QRect(1100, 260, 300, 341))   #设置位置
        self.label_image.setObjectName("label_image")
        self.label_image.setText("进行图像选择")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(25)
        self.label_image.setFont(font)
        # 添加一个按钮
        self.pushButton_first = QtWidgets.QPushButton(MainWindow)
        self.pushButton_first.setGeometry(QtCore.QRect(900, 690, 170, 130))  #设置位置
        self.pushButton_first.setText("选择一张图像")

        self.pushButton_second = QtWidgets.QPushButton(MainWindow)
        self.pushButton_second.setGeometry(QtCore.QRect(1300, 690, 170, 130))  #设置位置
        self.pushButton_second.setText("选择两张图像")

        A = MainWindow2()
        B = MainWindow3()
        # 绑定按钮的点击事件到槽函数
        self.pushButton_first.clicked.connect(lambda:{MainWindow.close(), A.show()})
        self.pushButton_second.clicked.connect(lambda:{MainWindow.close(), B.show()})




class MainWindow_hello(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow_hello, self).__init__(parent)
        self.setupUi(self)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_hello()
    window.show()
    sys.exit(app.exec_())
