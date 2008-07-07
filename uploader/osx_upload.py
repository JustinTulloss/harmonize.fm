import objc, thread
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
from Queue import Queue

class UploadController(NSObject):
	window = objc.ivar('window')
	optionsWindow = objc.ivar('optionsWindow')
	introView = objc.ivar('introView')
	errorView = objc.ivar('errorView')
	errorMsg = objc.ivar('errorMsg')

	def awakeFromNib(self):
		self.window.makeKeyAndOrderFront_(self)
		NSApp().activateIgnoringOtherApps_(True)

		self.uploadView = self.window.contentView()
		self.uploadView.retain()
		self.window.setContentView_(self.introView)

	def fatalError_(self, msg):
		self.window.setContentView_(self.errorView)
		self.errorMsg = msg

	def activate(self):
		NSApp().activateIgnoringOtherApps_(True)
		self.window.makeKeyAndOrderFront_(self)

	#actions
	def options_(self, sender):
		NSApp().activateIgnoringOtherApps_(True)
		self.optionsWindow.makeKeyAndOrderFront_(self)

	def next_(self, sender):
		self.window.setContentView_(self.uploadView)

	def activate_(self, sender):
		self.activate()
