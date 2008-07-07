import objc
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
from osx_options import UploadFolders, OptionsController
from osx_upload import UploadController

NibClassBuilder.extractClasses('MainMenu')

def d_invoke(val):
	global delegate
	if getattr(delegate, val) != None:
		getattr(delegate, val)()

director = None
delegate = None

def Application(upload_mode, upload_dirs, itunes_enabled,
				listen_clicked=None, login_clicked=None,
				exit_clicked=None, options_changed=None,
				app_started=None):
	global delegate

	#NibClassBuilder.extractClasses(path='MainMenu.nib')

	def ns_gc(fn):
		def wrapper(*args, **kws):
			pool = NSAutoreleasePool.alloc().init()
			res = fn(*args, **kws)
			del pool
			return res
		return wrapper

	class Delegate(object):
		def __init__(self):
			self.listen_clicked = listen_clicked
			self.login_clicked = login_clicked
			self.exit_clicked = exit_clicked
			self.options_changed = options_changed
			self.app_started = app_started

			self.upload_mode = upload_mode
			self.upload_dirs = upload_dirs
			self.itunes_enabled = itunes_enabled

		def start(self):
			AppHelper.runEventLoop()

		@ns_gc
		def set_uploaded(self, value):
			director.uploaded.\
				performSelectorOnMainThread_withObject_waitUntilDone_(
				'setStringValue:', str(value), False)

		@ns_gc
		def set_skipped(self, value):
			director.skipped.\
				performSelectorOnMainThread_withObject_waitUntilDone_(
				'setStringValue:', str(value), False)

		@ns_gc
		def set_remaining(self, value):
			director.remaining.\
				performSelectorOnMainThread_withObject_waitUntilDone_(
				'setStringValue:', str(value), False)

		@ns_gc
		def set_progress(self, spinning, value=None):
			director.performSelectorOnMainThread_withObject_waitUntilDone_(
				'setProgress:', (spinning, value), False)

		@ns_gc
		def set_msg(self, msg):
			director.msg.performSelectorOnMainThread_withObject_waitUntilDone_(
				'setStringValue:', msg, False)

		@ns_gc
		def enable_listen(self, enabled):
			director.performSelectorOnMainThread_withObject_waitUntilDone_(
				'listenEnabled:', enabled, False)

		@ns_gc
		def enable_options(self, enabled):
			director.performSelectorOnMainThread_withObject_waitUntilDone_(
				'optionsEnabled:', enabled, False)

		@ns_gc
		def enable_login(self, enabled):
			director.performSelectorOnMainThread_withObject_waitUntilDone_(
				'loginEnabled:', enabled, False)

		@ns_gc
		def activate(self):
			director.uploadController.\
				performSelectorOnMainThread_withObject_waitUntilDone_(
				'activate', None, False)

		@ns_gc
		def quit(self):
			NSApp().performSelectorOnMainThread_withObject_waitUntilDone_(
				'terminate:', self, False)

		@ns_gc
		def fatal_error(self, msg):
			director.uploadController.\
				performSelectorOnMainThread_withObject_waitUntilDone_(
					'fatalError:', msg, False)
	
	delegate = Delegate()
	return delegate

class RubiconController(NibClassBuilder.AutoBaseClass):
	def awakeFromNib(self):
		NSThread.detachNewThreadSelector_toTarget_withObject_(
				self.dummy_fn, self, None)

		statusBar = NSStatusBar.systemStatusBar()
		item = statusBar.statusItemWithLength_(NSVariableStatusItemLength)
		item.retain()

		item.setTitle_("H")
		item.setHighlightMode_(True)
		item.setMenu_(self.statusMenu)
		#NSApp().setMainMenu_(self.statusMenu)

		global director
		director = self

		d_invoke('app_started')
		self.optionsController.init_options(
			delegate.upload_mode, delegate.upload_dirs, 
			delegate.itunes_enabled, self.options_changed)

		self.modal = False

	def dummy_fn(self):
		"""Called in order to put Cocoa in multithreaded mode"""
		pass

	def setProgress_(self, args):
		spinning, value = args
		if spinning:
			self.progressb.setIndeterminate_(True)
			self.progressb.startAnimation_(self)
		else:
			self.progressb.setIndeterminate_(False)
			self.progressb.setDoubleValue_(value)

	def listenEnabled_(self, enabled):
		self.listenButton.setEnabled_(enabled)

	def optionsEnabled_(self, enabled):
		self.optionsButton.setEnabled_(enabled)
		self.optionsMenuItem.setEnabled_(enabled)

	def loginEnabled_(self, enabled):
		self.loginButton.setEnabled_(enabled)

	def options_changed(self, src, dirs):
		if delegate.options_changed:
			delegate.options_changed(src, dirs)

	def worksWhenModal(self):
		return True

	#actions
	def listen_(self, sender):
		d_invoke('listen_clicked')

	def exit_(self, sender):
		d_invoke('exit_clicked')

	def login_(self, sender):
		d_invoke('login_clicked')

	def options_(self, sender):
		if self.modal:
			self.optionsWindow.makeKeyAndOrderFront_(self)
			NSApp().activateIgnoringOtherApps_(True)
		else:
			self.statusMenuItem.setEnabled_(False)
			self.modal = True
			NSApp().runModalForWindow_(self.optionsWindow)
			self.modal = False
			self.statusMenuItem.setEnabled_(True)
