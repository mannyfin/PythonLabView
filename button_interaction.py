import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider,
                             QVBoxLayout, QApplication)
import functools


def trackcalls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.has_been_called = True
        return func(*args, **kwargs)
    wrapper.has_been_called = False
    return wrapper

class Example2(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        lcd = QLCDNumber(self)
        sld = QSlider(Qt.Horizontal, self)

        vbox = QVBoxLayout()
        vbox.addWidget(lcd)
        vbox.addWidget(sld)

        self.setLayout(vbox)
        sld.valueChanged.connect(lcd.display)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Signal and slot')
        self.show()


class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        btn1 = QPushButton("Button 1", self)
        btn1.move(30, 50)

        btn2 = QPushButton("Button 2", self)
        btn2.move(150, 50)

        btn1.clicked.connect(self.buttonClicked)
        # btn2.clicked.connect(self.buttonClicked)
        btn2.clicked.connect(self.button2clicked)

        exitbutton = QPushButton('Exit', self)
        exitbutton.clicked.connect(app.exit)
        self.statusBar()

        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Event sender')
        # print('hi'+str(a))
        self.show()

    @trackcalls
    def buttonClicked(self):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')
        return

    @trackcalls
    def button2clicked(self, buttonClicked = buttonClicked):
        sender2 = self.sender()
        i=1
        while i < 1:
            print(i + 1)
            i -= 1
            if buttonClicked.has_been_called:
                print('done')
                break
        # return i
        # sys.exit(app.exec_())




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex2 = Example2()
    app.exec_()