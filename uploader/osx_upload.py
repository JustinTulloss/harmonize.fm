import upload
import objc, thread
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
from decorator import decorator

def mainThread(fn):
	def wrapper(self, *args):
		import pdb; pdb.set_trace()
		self.performSelectorOnMainThread_withObject_waitUntilDone_(
			getattr(self, fn.__name__), args, False)
	return wrapper

class UploadController(NSObject):
	information = objc.ivar('information')
	progress = objc.ivar('progress')
	remaining = objc.ivar('remaining')
	skipped = objc.ivar('skipped')
	totalUploaded =  objc.ivar('totalUploaded')
	window = objc.ivar('window')
	button = objc.ivar('button')

	def start(self):
		self.window.makeKeyAndOrderFront_(self)

		def uploadSongs():
			pool = NSAutoreleasePool.alloc().init()

			upload.upload_files(self)
			del pool

		thread.start_new_thread(uploadSongs, ())

		self.progress.startAnimation_(self)

	#actions
	def buttonPress_(self, sender):
		fb.login(None)

	#Upload status callbacks
	def init_status(self, msg):
		self.performSelectorOnMainThread_withObject_waitUntilDone_(
			self._init_status, msg, False)


	def _init_status(self, msg):
		self.totalUploaded = str(0)
		self.remaining = str(0)
		self.skipped = str(0)

		self.progress.setDoubleValue_(0.0)
		self.progress.setIndeterminate_(True)

		self.information = msg

	def inc_totalUploaded(self):
		self.performSelectorOnMainThread_withObject_waitUntilDone_(
			self._inc_totalUploaded, None, False)

	def _inc_totalUploaded(self, args):
		self.totalUploaded = str(int(self.totalUploaded) + 1)

	def inc_skipped(self):
		self.performSelectorOnMainThread_withObject_waitUntilDone_(
			self._inc_skipped, None, False)

	def _inc_skipped(self):
		self.skipped = str(int(self.skipped) + 1)

	def dec_remaining(self):
		self.performSelectorOnMainThread_withObject_waitUntilDone_(
			self._dec_remaining, None, False)

	def _dec_remaining(self):
		self.remaining = str(int(self.remaining) + 1)

	def inc_remaining(self):
		self.performSelectorOnMainThread_withObject_waitUntilDone_(
			self._inc_remaining, None, False)

	def _inc_remaining(self):
		self.remaining = str(int(self.remaining) + 1)

	def set_progress(self, spinning, val):
		self.performSelectorOnMainThread_withObject_waitUntilDone_(
			self._set_progress, (spinning, val), False)

	def _set_progress(self, args):
		spinning, val = args
		self.progress.setIndeterminate_(spinning)
		if not spinning:
			self.progress.setDoubleValue_(val)

	def set_msg(self, msg):
		self.performSelectorOnMainThread_withObject_waitUntilDone_(
			self._set_msg, msg, False)

	def _set_msg(self, msg):
		self.information = msg

	def start_reauth(self, msg):
		self.performSelectorOnMainThread_withObject_waitUntilDone_(
			self._start_reauth, msg, False)
		
	def _start_reauth(self, msg):
		self._set_msg(msg)
		self._set_progress(True)
		self.button.setHidden_(True)

	def end_reauth(self, msg):
		self.performSelectorOnMainThread_withObject_waitUntilDone_(
			self._end_reauth, msg, False)

	def _end_reauth(self, msg):
		self._set_msg(msg)
		self.button.setHidden_(False)

	def error(self, msg):
		self.set_msg(msg)
		self.set_progress(True, None)
