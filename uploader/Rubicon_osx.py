import objc, fb, itunes, thread, upload, os
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper
from dir_browser import contains_dir, get_dir_listing

NibClassBuilder.extractClasses("MainMenu")

class WizardWindow(NSWindow):
	viewMappings = {}
	pageView = None
	nextButton = None
	prevButton = None
	hasRun = False

	def awakeFromNib(self):
		for view in self.contentView().subviews():
			if type(view) == NSButton:
				if view.title() == 'Next':
					self.nextButton = view
				elif view.title() == 'Previous':
					self.prevButton = view
			elif type(view) == NSView:
				self.pageView = view

		NSThread.detachNewThreadSelector_toTarget_withObject_(
				self.dummy_fn, self, None)
		self.setFirstView()

	def dummy_fn(self):
		"""Called in order to put Cocoa in multithreaded mode"""
		pass

	def nextView_(self, sender):
		self.setNewView(self.pageView.getNext())

	def prevView_(self, sender):
		self.setNewView(self.pageView.getPrev())

	def setNewView(self, newViewType):
		"""Replace the content of the content view"""
		newView = self.viewMappings[newViewType]
		frame = self.pageView.frame()
		self.contentView().replaceSubview_with_(self.pageView, newView)
		newView.setFrame_(frame)
		if type(self.pageView) != NSView:
			self.pageView.viewActive = False
		self.pageView = newView
		if newView.getNext() == None:
			self.nextButton.setEnabled_(False)
		else:
			self.nextButton.setEnabled_(True)

		if newView.getPrev() == None:
			self.prevButton.setEnabled_(False)
		else:
			self.prevButton.setEnabled_(True)

		newView.viewActive = True
		newView.viewSet()
	
	def registerView(self, viewClass, view):
		if not self.viewMappings.has_key(viewClass):
			self.viewMappings[viewClass] = view
		else:
			print 'Error: two instances of same view class'
	
	def setFirstView(self):
		if not self.hasRun:
			self.hasRun = True
		else:
			self.setNewView(StartView)

	def enableNext_(self):
		self.nextButton.setEnabled_(True)

	def enablePrev_(self):
		self.prevButton.setEnabled_(False)

def getWizard():
	for window in NSApp().windows():
		if type(window) == WizardWindow:
			return window

class WizardView(NSView):
	viewActive = False

	def awakeFromNib(self):
		getWizard().registerView(type(self), self)

	def getNext(self):
		return None
	
	def getPrev(self):
		return None

	def viewSet(self):
		"""Called when a view is loaded into the wizard"""
		pass

class StartView(WizardView):
	"""The first page when the program opens"""
	def awakeFromNib(self):
		getWizard().registerView(type(self), self)
		getWizard().setFirstView()

	def getNext(self):
		return LoginView

session_key = None

class LoginView(WizardView):
	def callback(self, new_session_key):
		global session_key
		pool = NSAutoreleasePool.alloc().init()
		session_key = new_session_key
		textfield = self.subviews()[0]
		textfield.performSelectorOnMainThread_withObject_waitUntilDone_(
			textfield.setStringValue_, "Login complete", False)
		getWizard().performSelectorOnMainThread_withObject_waitUntilDone_(
			getWizard().enableNext_, None, False)
		NSApp().performSelectorOnMainThread_withObject_waitUntilDone_(
			NSApp().activateIgnoringOtherApps_, True, False)
		del pool

	def viewSet(self):
		global session_key
		if session_key == None:
			fb.login(self.callback)

	def getPrev(self):
		return StartView

	def getNext(self):
		if session_key == None:
			return None
		else:
			return UploadSelectView

uploadInfo = None

class UploadView(WizardView):
	uploadThread = None
	def awakeFromNib(self):
		getWizard().registerView(type(self), self)
		for view in self.subviews():
			if type(view) == NSProgressIndicator:
				self.progress = view
			elif type(view) == NSTextField:
				self.status = view

	def updateStatus(self, new_status):
		self.status.performSelectorOnMainThread_withObject_waitUntilDone_(
			self.status.setStringValue_, new_status, False)
	
	def viewSet(self):
		if self.uploadThread == None:
			thread.start_new_thread(self.uploadSongs, ())
			self.progress.startAnimation_(self)
		
	def uploadSongs(self):
		global uploadInfo, session_key
		pool = NSAutoreleasePool.alloc().init()
		tracks = uploadInfo.getTracks()
		upload.upload_files(tracks, session_key, self.onSongsLeft)
		del pool

	def onSongsLeft(self, songs_left):
		if type(songs_left) == str:
			self.updateStatus(songs_left)
		elif songs_left != 0:
			self.updateStatus("%s songs remaining..." % songs_left)
		else:
			self.performSelectorOnMainThread_withObject_waitUntilDone_(
				self.uploadComplete, None, False)

	def uploadComplete(self):
		self.status.setStringValue_("Upload complete!")
		self.progress.stopAnimation_(self)
		self.progress.setHidden_(True)
		
class FolderBrowserDelegate(NSObject):
	paths = {}
	selectedPath = None

	def ensure_path(self, path):
		if path == '':
			path = '/'
		if not self.paths.has_key(path):
			self.paths[path] = get_dir_listing(path)

		return self.paths[path]

	def setFolderField(self, value):
		global folderField
		folderField.setStringValue_(value)
		folderField.setToolTip_(value)
		self.selectedPath = value

	def browser_numberOfRowsInColumn_(self, browser, column):
		path = browser.path()
		self.setFolderField(path)
		return len(self.ensure_path(path))

	def browser_willDisplayCell_atRow_column_(self, browser,cell,row,column):
		parentdir_path = os.path.join('/', browser.pathToColumn_(column))
		dirname = self.ensure_path(parentdir_path)[row]
		dirpath = os.path.join(parentdir_path, dirname)
		cell.setStringValue_(dirname)

		if contains_dir(dirpath):
			cell.setLeaf_(False)
		else:
			cell.setLeaf_(True)

folderField = None

class FolderSelectView(WizardView):
	def awakeFromNib(self):
		global folderField
		getWizard().registerView(type(self), self)
		folderField = self.viewWithTag_(1)
		self.browser = self.viewWithTag_(2)
		self.delegate = FolderBrowserDelegate.alloc().init()
		
		self.browser.setTitled_(False)
		self.browser.setDelegate_(self.delegate)

	def viewSet(self):
		"""This autoexpands the directory browser"""
		i = 0
		for component in upload.get_default_path().split('/')[1:]:
			row = self.delegate.ensure_path(self.browser.path()).index(component)
			self.browser.selectRow_inColumn_(row, i)
			i += 1

	def getPrev(self):
		return UploadSelectView

	def getNext(self):
		global uploadInfo
		if self.viewActive:
			uploadInfo =  FolderUpload(self.delegate.selectedPath)

		return UploadView


class UploadSelectView(WizardView):
	nextView = UploadView
	
	def getNext(self):
		global uploadInfo
		if self.nextView == UploadView and uploadInfo == None:
			uploadInfo = ITunesUpload()
		return self.nextView

	def getPrev(self):
		return LoginView
	
	def setUploadAll_(self):
		self.nextView = FolderSelectView
	
	def setUploadiTunes_(self):
		self.nextView = UploadView

class ITunesUpload(object):
	"""Indicates that the upload action is set to upload iTunes music"""
	def getTracks(self):
		return filter(upload.is_music_file, 
					itunes.ITunes().get_all_track_filenames())

class FolderUpload(object):
	"""Indicates that a directory will be uploaded"""
	def __init__(self, path):
		self.path = path

	def getTracks(self):
		return upload.get_music_files(self.path)

if __name__ == "__main__":
    AppHelper.runEventLoop()
