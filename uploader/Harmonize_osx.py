import objc, fb
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
from osx_options import UploadFolders, OptionsController
from osx_upload import UploadController
import singleton

NibClassBuilder.extractClasses('MainMenu')

class RubiconController(NSObject):
	optionsWindow = objc.ivar('optionsWindow')
	uploadWindow = objc.ivar('uploadWindow')
	statusMenu = objc.ivar('statusMenu')

	def awakeFromNib(self):
		singleton.set_callback(self.activate_uploads_async)

		NSThread.detachNewThreadSelector_toTarget_withObject_(
				self.dummy_fn, self, None)

		statusBar = NSStatusBar.systemStatusBar()
		item = statusBar.statusItemWithLength_(NSVariableStatusItemLength)
		item.retain()

		item.setTitle_("H")
		item.setHighlightMode_(True)
		item.setMenu_(self.statusMenu)

		NSApp().setDelegate_(self)

	def dummy_fn(self):
		"""Called in order to put Cocoa in multithreaded mode"""
		pass

	def loginCallbackSync(self):
		self.optionsWindow.orderOut_(self)
		self.mainWindow.orderOut_(self)
		self.uploadController.start()

		NSApp().activateIgnoringOtherApps_(True)

	def activate_uploads(self):
		self.uploadWindow.makeKeyAndOrderFront_(self)
		NSApp().activateIgnoringOtherApps_(True)

	def activate_uploads_async(self):
		pool = NSAutoreleasePool.alloc().init()

		self.performSelectorOnMainThread_withObject_waitUntilDone_(
			self.activate_uploads, None, False)

		del pool

	def applicationWillTerminate_(self, notification):
		singleton.atexit()

	#Controller actions:
	def options_(self, sender):
		self.optionsWindow.makeKeyAndOrderFront_(self)
		NSApp().activateIgnoringOtherApps_(True)

	def upload_(self, sender):
		self.activate_uploads()

	def quit_(self, sender):
		NSApp().terminate_(self)

if __name__ == '__main__':
	if not singleton.running():
		AppHelper.runEventLoop()
