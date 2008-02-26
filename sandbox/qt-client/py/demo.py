#!/usr/bin/python

import sys
from uploadui import QtGui, Ui_MainWindow

app = QtGui.QApplication(sys.argv)
gen = Ui_MainWindow()
main = QtGui.QMainWindow()
gen.setupUi(main)
main.show()
app.exec_()
