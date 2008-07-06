import itunes, upload
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

	def awakeFromNib(self):
		#Set up the file chooser dialog
		self.folderChooser = NSOpenPanel.openPanel()
		self.folderChooser.setCanChooseFiles_(False)
		self.folderChooser.setCanChooseDirectories_(True)
		self.folderChooser.setAllowsMultipleSelection_(True)
		self.options_changed = None
		self.changed = False

	def init_options(self, upload_mode, upload_dirs, 
					itunes_enabled, changed_callback):
		self.changed_callback = changed_callback

		if upload_mode == 'itunes':
			self.iTunesButton.setState_(1)
			self.folderButton.setState_(0)
		else:
			self.iTunesButton.setState_(0)
			self.folderButton.setState_(1)

		self.iTunesButton.setEnabled_(itunes_enabled)
		self.uploadFolders.dirs = upload_dirs
		self.folderGrid.reloadData()

	def windowWillClose_(self, notification):
		NSApp().stopModalWithCode_(0)
		if self.changed:
			self.changed = False
			if self.iTunesButton.state() == 1:
				src = 'itunes'
			else:
				src = 'folder'
			self.changed_callback(src, self.uploadFolders.dirs)

	def optionsClosed_(self, sender):
		self.window.close()

	def setUploadFolder_(self, sender):
		self.changed = True
	
	def setUploadITunes_(self, sender):
		self.changed = True

	def addFolders_(self, sender):
		res = self.folderChooser.runModalForTypes_(None)
		
		if res == NSOKButton and len(self.folderChooser.filenames()) > 0:
			self.uploadFolders.add(self.folderChooser.filenames())
			self.folderGrid.reloadData()
			self.changed = True

	def removeFolders_(self, sender):
		self.uploadFolders.remove(self.folderGrid.selectedRowIndexes())
		self.folderGrid.reloadData()
		self.changed = True

class UploadFolders(NSObject):
	def init(self):
		self = super(UploadFolders, self).init()

		self.dirs = []
		return self

	def numberOfRowsInTableView_(self, tableView):
		return len(self.dirs)

	def tableView_objectValueForTableColumn_row_(self, tableView, col, row):
		return self.dirs[row]

	def set_dirs(dirs):
		self.dirs = dirs

	def add(self, new_dirs):
		for new_dir in new_dirs:
			if new_dir not in self.dirs:
				self.dirs.append(new_dir)
	
	def remove(self, selected_rows):
		new_dirs = []
		for i in range(len(self.dirs)):
			if not selected_rows.containsIndex_(i):
				new_dirs.append(self.dirs[i])

		self.dirs = new_dirs
