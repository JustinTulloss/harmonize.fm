import objc, fb, itunes, thread, upload, os, db
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper

NibClassBuilder.extractClasses('MainMenu')

class RubiconController(NSObject):
	uploadOptions = objc.ivar('uploadOptions')
	uploadFolderButton = objc.ivar('uploadFolderButton')
	uploadITunesButton = objc.ivar('uploadITunesButton')
	uploadFolderField = objc.ivar('uploadFolderField')

	loginView = objc.ivar('loginView')
	uploadView = objc.ivar('uploadView')

	mainWindow = objc.ivar('mainWindow')

	uploadPath = objc.ivar('uploadPath')
	uploadStatus = objc.ivar('uploadStatus')
	
	progressbar = objc.ivar('progressbar')

	def awakeFromNib(self):
		NSThread.detachNewThreadSelector_toTarget_withObject_(
				self.dummy_fn, self, None)

		#Set up the default upload location
		if itunes.get_library_file() == None:
			self.uploadITunesButton.setEnabled_(False)

		if db.get_upload_src() == 'folder':
			self.uploadITunesButton.setState_(0)
			self.uploadFolderButton.setState_(1)

		self.uploadFolderField.setStringValue_(db.get_upload_dir())

		#Set up the file chooser dialog
		self.folderChooser = NSOpenPanel.openPanel()
		self.folderChooser.setCanChooseFiles_(False)
		self.folderChooser.setCanChooseDirectories_(True)

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
	def changeFolder_(self, sender):
		res = self.folderChooser.runModalForTypes_(None)
		
		if res == NSOKButton and len(self.folderChooser.filenames()) > 0:
			db.set_upload_dir(self.folderChooser.filenames()[0])
			self.uploadFolderField.setStringValue_(db.get_upload_dir())

	def login_(self, sender):
		def callback(session_key):
			pool = NSAutoreleasePool.alloc().init()

			self.performSelectorOnMainThread_withObject_waitUntilDone_(
				self.loginCallbackSync, None, False)

			del pool

		fb.login(callback)

	def options_(self, sender):
		self.uploadOptions.makeKeyAndOrderFront_(self)

	def setUploadFolder_(self, sender):
		db.set_upload_src('folder')
	
	def setUploadITunes_(self, sender):
		db.set_upload_src('folder')

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
