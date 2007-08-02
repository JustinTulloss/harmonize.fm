#Making a PyQt App to rock some serious socks

import sys
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QApplication

#Load the Gui from a file. Once it's more finalized, we'll compile
#it into actual code
uiForms = uic.loadUiType('serverprefs.ui')

class prefChanger(uiForms[1], uiForms[0]):
	def __init__(self):
		super(prefChanger, self).__init__()
		self.setupUi(self)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	win = prefChanger()
	win.show()
	app.exec_()
