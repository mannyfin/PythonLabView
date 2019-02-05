import sys
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow, QApplication,QPushButton


class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.button1 = QPushButton('Button1', self)
        # self.button1.move(30, 50)

        self.button2 = QPushButton('Button2', self)
        self.button2.move(0,30)


        self.show()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())