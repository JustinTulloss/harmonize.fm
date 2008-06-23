import objc, fb, itunes, thread, upload, os, db, osx_options
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper

NibClassBuilder.extractClasses('MainMenu')

class RubiconController(NSObject):
	optionsWindow = objc.ivar('optionsWindow')

	loginView = objc.ivar('loginView')
	uploadView = objc.ivar('uploadView')

	mainWindow = objc.ivar('mainWindow')

	uploadPath = objc.ivar('uploadPath')
	uploadStatus = objc.ivar('uploadStatus')
	
	progressbar = objc.ivar('progressbar')

	def awakeFromNib(self):
		NSThread.detachNewThreadSelector_toTarget_withObject_(
				self.dummy_fn, self, None)

		#Have the loginView display on startup
		self.mainWindow.setContentView_(self.loginView)

	def dummy_fn(self):
		"""Called in order to put Cocoa in multithreaded mode"""
		pass

	def loginCallbackSync(self):
		self.uploadOptions.close()

		target = self
		class Receiver(object):
			def init(self, msg, total_songs):
				target.performSelectorOnMainThread_withObject_waitUntilDone_(
					target.upload_init, (msg, total_songs), False)

			def update(self, msg, songs_left):
				target.performSelectorOnMainThread_withObject_waitUntilDone_(
					target.upload_update, (msg, songs_left), False)

			def error(self, msg):
				target.performSelectorOnMainThread_withObject_waitUntilDone_(
					target.upload_error, msg, False)
				
		def uploadSongs():
			pool = NSAutoreleasePool.alloc().init()

			upload.upload_files(db.get_tracks(), Receiver())
			del pool

		thread.start_new_thread(uploadSongs, ())

		self.mainWindow.setContentView_(self.uploadView)
		self.progressbar.startAnimation_(self)
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


	#Upload status callbacks
	def upload_error(self, msg):
		self.uploadStatus = msg
		self.progressbar.setIndeterminate_(True)
		self.progressbar.startAnimation_(self)
	
	def upload_update(self, args):
		msg, songs_left = args
		self.uploadStatus = msg
		self.progressbar.setIndeterminate_(False)
		if songs_left > 0:
			self.progressbar.setDisplayedWhenStopped_(True)
		else:
			self.progressbar.setDisplayedWhenStopped_(False)
			self.progressbar.stopAnimation_(self)
		self.progressbar.setDoubleValue_(self.progressbar.maxValue()-songs_left)

	def upload_init(self, args):
		msg, total_songs = args
		self.uploadStatus = msg
		self.progressbar.setMaxValue_(total_songs)
		self.progressbar.setIndeterminate_(False)

if __name__ == '__main__':
	AppHelper.runEventLoop()
