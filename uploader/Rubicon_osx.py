import objc, fb, itunes, thread, upload, os
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper

NibClassBuilder.extractClasses('MainMenu')

class RubiconController(NSObject):
	uploadOptions = objc.ivar('uploadOptions')
	uploadFolderButton = objc.ivar('uploadFolderButton')
	uploadITunesButton = objc.ivar('uploadITunesButton')

	loginView = objc.ivar('loginView')
	uploadView = objc.ivar('uploadView')

	mainWindow = objc.ivar('mainWindow')

	uploadPath = objc.ivar('uploadPath')
	uploadStatus = objc.ivar('uploadStatus')
	
	progressbar = objc.ivar('progressbar')

	def awakeFromNib(self):
		NSThread.detachNewThreadSelector_toTarget_withObject_(
				self.dummy_fn, self, None)

		self.uploadPath = upload.get_default_path()

		#Set up the default upload location
		if itunes.get_library_file() != None:
			self.uploadSrc = self.uploadITunes
		else:
			self.uploadSrc = self.uploadFolder
			self.uploadITunesButton.setEnabled_(False)
			self.uploadITunesButton.setState_(0)
			self.uploadFolderButton.setState_(1)

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

			tracks = self.uploadSrc()
			upload.upload_files(tracks, Receiver())
			del pool

		thread.start_new_thread(uploadSongs, ())

		self.mainWindow.setContentView_(self.uploadView)
		self.progressbar.startAnimation_(self)
		NSApp().activateIgnoringOtherApps_(True)

	#Upload selections
	def uploadITunes(self):
		return filter(upload.is_music_file,
						itunes.ITunes().get_all_track_filenames())

	def uploadFolder(self):
		return upload.get_music_files(self.uploadPath)

	#Controller actions:
	def changeFolder_(self, sender):
		res = self.folderChooser.runModalForTypes_(None)
		
		if res == NSOKButton and len(self.folderChooser.filenames()) > 0:
			self.uploadPath = self.folderChooser.filenames()[0]

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
		self.uploadSrc = self.uploadFolder
	
	def setUploadITunes_(self, sender):
		self.uploadSrc = self.uploadITunes

	#Upload status callbacks
	def upload_error(self, msg):
		self.uploadStatus = msg
		self.progressbar.setIndeterminate_(True)
		self.progressbar.startAnimation_(self)
	
	def upload_update(self, args):
		msg, songs_left = args
		self.uploadStatus = msg
		self.progressbar.setIndeterminate_(False)
		self.progressbar.setDoubleValue_(self.progressbar.maxValue()-songs_left)

	def upload_init(self, args):
		msg, total_songs = args
		self.uploadStatus = msg
		self.progressbar.setMaxValue_(total_songs)
		self.progressbar.setIndeterminate_(False)

if __name__ == '__main__':
	AppHelper.runEventLoop()
