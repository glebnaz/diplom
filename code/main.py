# -*- coding: utf-8 -*-
import sys
from PySide import QtGui
from PySide.QtGui import QApplication, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle(u'Главное окно')    # если устанавливать значение не unicode, то будут печататься крокозябры
        self.resize(300, 200)
        self.cw = QtGui.QWidget()  # на главном окне нужно определить central widget
        self.layout = QtGui.QGridLayout()  # у central widget должна быть определена разметка, чтобы добавлять в неё gui-элементы
        self.cw.setLayout(self.layout)
        self.setCentralWidget(self.cw)
        self.pushButton = QtGui.QPushButton()
        self.pushButton.setText('Test')
        self.pushButton.clicked.connect(self.buttonTest)
        self.layout.addWidget(self.pushButton, 0, 0)

    def buttonTest(self):
        print ('Test OK')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    sys.exit( app.exec_() )
