import db, itunes, upload
import objc
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper

class OptionsController(NSObject):
	window = objc.ivar('window')
	folderButton = objc.ivar('folderButton')
	iTunesButton = objc.ivar('iTunesButton')
	folderGrid = objc.ivar('folderGrid')
	uploadFolders = objc.ivar('uploadFolders')
	optionsVisible = objc.ivar('optionsVisible')

	def closeWindow_(self, sender):
		self.window.orderOut_(self)

	def awakeFromNib(self):
		#Set up the default upload location
		if itunes.get_library_file() == None:
			self.iTunesButton.setEnabled_(False)

		if db.get_upload_src() == 'folder':
			self.iTunesButton.setState_(0)
			self.folderButton.setState_(1)

		#Set up the file chooser dialog
		self.folderChooser = NSOpenPanel.openPanel()
		self.folderChooser.setCanChooseFiles_(False)
		self.folderChooser.setCanChooseDirectories_(True)
		self.folderChooser.setAllowsMultipleSelection_(True)

		self.options_changed = False

	def windowDidResignMain_(self, notification):
		if self.options_changed:
			upload.options_changed()
			self.options_changed = False

	def setUploadFolder_(self, sender):
		db.set_upload_src('folder')
		self.options_changed = True
	
	def setUploadITunes_(self, sender):
		db.set_upload_src('itunes')
		self.options_changed = True

	def addFolders_(self, sender):
		res = self.folderChooser.runModalForTypes_(None)
		
		if res == NSOKButton and len(self.folderChooser.filenames()) > 0:
			self.uploadFolders.add(self.folderChooser.filenames())
			self.folderGrid.reloadData()
			self.options_changed = True

	def removeFolders_(self, sender):
		self.uploadFolders.remove(self.folderGrid.selectedRowIndexes())
		self.folderGrid.reloadData()
		self.options_changed = True

class UploadFolders(NSObject):
	def init(self):
		self = super(UploadFolders, self).init()

		self.dirs = db.get_upload_dirs()
		return self

	def numberOfRowsInTableView_(self, tableView):
		return len(self.dirs)

	def tableView_objectValueForTableColumn_row_(self, tableView, col, row):
		return self.dirs[row]

	def add(self, new_dirs):
		for new_dir in new_dirs:
			if new_dir not in self.dirs:
				self.dirs.append(new_dir)
		db.set_upload_dirs(self.dirs)
	
	def remove(self, selected_rows):
		new_dirs = []
		for i in range(len(self.dirs)):
			if not selected_rows.containsIndex_(i):
				new_dirs.append(self.dirs[i])

		self.dirs = new_dirs
		db.set_upload_dirs(self.dirs)
