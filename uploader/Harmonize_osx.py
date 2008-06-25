import objc, fb
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
from osx_options import UploadFolders, OptionsController
from osx_upload import UploadController

NibClassBuilder.extractClasses('MainMenu')

class RubiconController(NSObject):
	optionsWindow = objc.ivar('optionsWindow')

	mainWindow = objc.ivar('mainWindow')
	uploadController = objc.ivar('uploadController')

	uploadPath = objc.ivar('uploadPath')
	uploadStatus = objc.ivar('uploadStatus')
	
	progressbar = objc.ivar('progressbar')

	def awakeFromNib(self):
		NSThread.detachNewThreadSelector_toTarget_withObject_(
				self.dummy_fn, self, None)

	def dummy_fn(self):
		"""Called in order to put Cocoa in multithreaded mode"""
		pass

	def loginCallbackSync(self):
		self.optionsWindow.orderOut_(self)
		self.mainWindow.orderOut_(self)
		self.uploadController.start()

		NSApp().activateIgnoringOtherApps_(True)

	#Controller actions:
	def login_(self, sender):
		def callback(session_key):
			pool = NSAutoreleasePool.alloc().init()

			self.performSelectorOnMainThread_withObject_waitUntilDone_(
				self.loginCallbackSync, None, False)

			del pool

		fb.login(callback)

	def options_(self, sender):
		self.optionsWindow.makeKeyAndOrderFront_(self)

if __name__ == '__main__':
	AppHelper.runEventLoop()
