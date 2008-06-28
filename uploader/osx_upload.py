import upload, fb
import objc, thread
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
from Queue import Queue

class UploadController(NSObject):
	information = objc.ivar('information')
	progress = objc.ivar('progress')
	remaining = objc.ivar('remaining')
	skipped = objc.ivar('skipped')
	totalUploaded =  objc.ivar('totalUploaded')
	window = objc.ivar('window')
	optionsWindow = objc.ivar('optionsWindow')
	loginButton = objc.ivar('loginButton')
	optionsButton = objc.ivar('optionsButton')
	optionsMenu = objc.ivar('optionsMenu')
	introView = objc.ivar('introView')
	listenButton = objc.ivar('listenButton')

	def awakeFromNib(self):
		self.window.makeKeyAndOrderFront_(self)
		NSApp().activateIgnoringOtherApps_(True)
		self.actions = Queue()

		my = self
		class Actions(object):
			def init(self):
				my.remaining = str(0)
				my.skipped = str(0)
				my.progress.setDoubleValue_(0.0)

			def inc_totalUploaded(self):
				my.totalUploaded = str(int(my.totalUploaded) + 1)

			def set_totalUploaded(self, val):
				my.totalUploaded = str(val)

			def inc_skipped(self):
				my.skipped = str(int(my.skipped) + 1)

			def dec_remaining(self):
				my.remaining = str(int(my.remaining) - 1)

			def inc_remaining(self):
				my.remaining = str(int(my.remaining) + 1)

			def set_progress(self, spinning, val=None):
				my.progress.setIndeterminate_(spinning)
				if not spinning:
					my.progress.setDoubleValue_(val)

			def set_msg(self, msg):
				my.information = msg

			def loginEnabled(self, val):
				my.loginButton.setEnabled_(val)

			def optionsEnabled(self, val):
				my.optionsButton.setEnabled_(val)
				my.optionsMenu.setEnabled_(val)

			def activate(self):
				my.window.activateIgnoringOtherApps_(True)

			def listenEnabled(self, val):
				my.listenButton.setEnabled_(val)

		self.a = Actions()
		self.uploadView = self.window.contentView()
		self.uploadView.retain()
		self.window.setContentView_(self.introView)

	#actions
	def login_(self, sender):
		fb.login(upload.login_callback)

	def options_(self, sender):
		NSApp().activateIgnoringOtherApps_(True)
		self.optionsWindow.makeKeyAndOrderFront_(self)

	def next_(self, sender):
		self.window.setContentView_(self.uploadView)

		def uploadSongs():
			pool = NSAutoreleasePool.alloc().init()

			upload.start_uploader(self)
			del pool

		thread.start_new_thread(uploadSongs, ())

	def listen_(self, sender):
		fb.listen_now()

	#Upload status callbacks
	def complete_actions(self):
		self.performSelectorOnMainThread_withObject_waitUntilDone_(
			self._complete_actions, None, False)
		
	def _complete_actions(self):
		while not self.actions.empty():
			fn, params = self.actions.get()
			fn(*params)

	def add_action(self, fn, params):
		self.actions.put((fn, params))

	def do_action(self, fn, params):
		self.add_action(fn, params)
		self.complete_actions()

