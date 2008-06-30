import pythoncom
pythoncom.CoInitialize()

import os
import fb, itunes, upload, thread, dir_browser, hplatform, db, singleton
from Queue import Queue
import clr
import System
import System.IO
import System.Windows.Forms as winforms
from System.Drawing import Size, Point, Image, ContentAlignment, Bitmap, Icon
from System import EventHandler

icon = Icon.FromHandle(Bitmap('icon.bmp').GetHicon())

class MainWin(winforms.Form):
	def __init__(self):
		global icon

		formSize = Size(308, 213)
		self.Size = formSize
		self.MinimumSize = formSize
		self.MaximumSize = formSize
		self.StartPosition = winforms.FormStartPosition.CenterScreen
		self.Text = 'Harmonizer'
		self.Icon = icon
		self.MaximizeBox = False

		self.FormClosing += EventHandler(self.formClosing)

		self.components = System.ComponentModel.Container()

		intro = winforms.Panel()
		intro.Size = formSize

		introText = winforms.Label()
		introText.Location = Point(13, 13)
		introText.Size = Size(275, 125)
		introText.Text = \
'''Welcome to the Harmonizer.

This program will synchronize your music library with our servers so you can listen to your music anywhere and share music with your friends.'''
		intro.Controls.Add(introText)

		def nextClicked(sender, args):
			self.Controls.Remove(intro)
			thread.start_new_thread(upload.start_uploader, (self,))
		
		nextButton = winforms.Button()
		nextButton.Location = Point(233, 144)
		nextButton.Size = Size(54, 23)
		nextButton.Text = 'Next'
		nextButton.Click += EventHandler(nextClicked)
		intro.Controls.Add(nextButton)

		self.Controls.Add(intro)

		totalUploadedLabel = winforms.Label()
		totalUploadedLabel.AutoSize = True
		totalUploadedLabel.Location = Point(13, 13)
		totalUploadedLabel.Text = 'Total Uploaded:'
		self.Controls.Add(totalUploadedLabel)

		remainingLabel = winforms.Label()
		remainingLabel.AutoSize = True
		remainingLabel.Location = Point(13, 33)
		remainingLabel.Text = 'Remaining:'
		self.Controls.Add(remainingLabel)

		skippedLabel = winforms.Label()
		skippedLabel.AutoSize = True
		skippedLabel.Location = Point(13, 53)
		skippedLabel.Text = 'Skipped:'
		self.Controls.Add(skippedLabel)

		self.totalUploaded = winforms.Label()
		self.totalUploaded.Location = Point(187, 13)
		self.totalUploaded.Size = Size(100, 13)
		self.totalUploaded.TextAlign = ContentAlignment.TopRight
		self.Controls.Add(self.totalUploaded)

		self.remaining = winforms.Label()
		self.remaining.Location = Point(187, 33)
		self.remaining.Size = Size(100, 13)
		self.remaining.TextAlign = ContentAlignment.TopRight
		self.Controls.Add(self.remaining)

		self.skipped = winforms.Label()
		self.skipped.Location = Point(187, 53)
		self.skipped.Size = Size(100, 13)
		self.skipped.TextAlign = ContentAlignment.TopRight
		self.Controls.Add(self.skipped)

		self.loginButton = winforms.Button()
		self.loginButton.Location = Point(233, 144)
		self.loginButton.Size = Size(54, 23)
		self.loginButton.Text = 'Login'
		self.loginButton.Click += EventHandler(self.loginClicked)
		self.Controls.Add(self.loginButton)

		def optionsClicked(sender, args):
			self.AddOwnedForm(self.optionWin)
			self.optionWin.ShowDialog()

		self.optionsButton = winforms.Button()
		self.optionsButton.Size = Size(54, 23)
		self.optionsButton.Location = Point(173, 144)
		self.optionsButton.Text = 'Options'
		self.optionsButton.Click += EventHandler(optionsClicked)
		self.Controls.Add(self.optionsButton)

		self.optionWin = OptionWin(self)

		def listenClicked(s, e):
			fb.listen_now()

		self.listenButton = winforms.Button()
		self.listenButton.Location = Point(16, 144)
		self.listenButton.Size = Size(54, 23)
		self.listenButton.Text = 'Listen'
		self.listenButton.Enabled = False
		self.listenButton.Click += EventHandler(listenClicked)
		self.Controls.Add(self.listenButton)

		self.progress = winforms.ProgressBar()
		self.progress.Location = Point(16, 78)
		self.progress.Minimum = 0
		self.progress.Maximum = 100
		self.progress.Size = Size(271, 23)
		self.Controls.Add(self.progress)

		self.info = winforms.Label()
		self.info.Location = Point(16, 110)
		self.info.Size = Size(271, 28)
		self.Controls.Add(self.info)

		my = self
		class Actions(object):
			def init(self):
				my.remaining.Text = str(0)
				my.skipped.Text = str(0)
				my.progress.Value = 0.0

			def inc_totalUploaded(self):
				my.totalUploaded.Text = str(int(my.totalUploaded.Text) + 1)

			def set_totalUploaded(self, val):
				my.totalUploaded.Text = str(val)

			def inc_skipped(self):
				my.skipped.Text = str(int(my.skipped.Text) + 1)

			def dec_remaining(self):
				my.remaining.Text = str(int(my.remaining.Text) - 1)

			def inc_remaining(self):
				my.remaining.Text = str(int(my.remaining.Text) + 1)

			def set_progress(self, spinning, val=None):
				if spinning:
					my.progress.Style = winforms.ProgressBarStyle.Marquee
				else:
					my.progress.Style = winforms.ProgressBarStyle.Continuous

				if val != None:
					my.progress.Value = int(val*100)

			def set_msg(self, msg):
				my.info.Text = msg

			def loginEnabled(self, val):
				my.loginButton.Enabled = val

			def optionsEnabled(self, val):
				my.optionsButton.Enabled = val
				my.optionsMenuItem.Enabled = val

			def listenEnabled(self, val):
				my.listenButton.Enabled = val

			def activate(self):
				my.activate()

		self.a = Actions()
		self.actions = Queue()
		#icon = Icon.FromHandle(Bitmap('icon.bmp').GetHicon())
		self.appIcon = winforms.NotifyIcon()
		self.appIcon.Icon = icon
		self.appIcon.Text = 'Harmonizer'

		menu = winforms.ContextMenu()
		statusMenuItem = winforms.MenuItem('Status')
		def statusClicked(s, e):
			self.Show()
			if self.WindowState == winforms.FormWindowState.Minimized:
				self.WindowState = winforms.FormWindowState.Normal
			self.Activate()
		self.activate = lambda: statusClicked(None, None)

		self.appIcon.DoubleClick += EventHandler(statusClicked)

		statusMenuItem.Click += EventHandler(statusClicked)
		menu.MenuItems.Add(statusMenuItem)
		my.optionsMenuItem = winforms.MenuItem('Options')
		my.optionsMenuItem.Click += optionsClicked
		menu.MenuItems.Add(my.optionsMenuItem)
		exitMenuItem = winforms.MenuItem('Exit')
		menu.MenuItems.Add(exitMenuItem)
		self.exitClicked = False
		def exit(s, e):
			self.exitClicked = True
			winforms.Application.Exit()
		exitMenuItem.Click += EventHandler(exit)
			
		self.appIcon.ContextMenu = menu
		self.appIcon.Visible = True

		singleton.set_callback(self.activate)
	
	def add_action(self, fn, params):
		self.actions.put((fn, params))

	def complete_actions(self):
		def complete_actions_aux():
			while not self.actions.empty():
				fn, params = self.actions.get()
				fn(*params)

		#Don't want to keep updating UI after the app has closed
		if not self.exitClicked:
			self.Invoke(winforms.MethodInvoker(complete_actions_aux))

	def do_action(self, fn, params):
		self.add_action(fn, params)
		self.complete_actions()	
			
	def loginClicked(self, sender, args):
		fb.login(upload.login_callback)	

	def formClosing(self, sender, e):
		if not self.exitClicked:
			e.Cancel = True
			self.Hide()
		else:
			self.appIcon.Dispose()

class OptionWin(winforms.Form):
	def __init__(self, statusForm):
		global icon
		formSize = Size(352, 273)
		self.Size = formSize
		self.MinimumSize = formSize
		self.StartPosition = winforms.FormStartPosition.CenterScreen
		self.Text = 'Options'
		self.Icon = icon

		label = winforms.Label()
		label.AutoSize = True
		label.Location = Point(12, 13)
		label.Text = 'Select where you would like to upload music from'
		self.Controls.Add(label)

		self.changed = False

		def onITunesChecked(sender, args):
			if self.radioITunes.Checked:
				db.set_upload_src('itunes')
				self.changed = True

		self.radioITunes = winforms.RadioButton()
		self.radioITunes.AutoSize = True
		self.radioITunes.Location = Point(12, 33)
		self.radioITunes.Text = 'iTunes'
		self.radioITunes.CheckedChanged += EventHandler(onITunesChecked)
		self.Controls.Add(self.radioITunes)

		def onFolderChecked(sender, args):
			if self.radioFolder.Checked:
				db.set_upload_src('folder')
				self.changed = True

		self.radioFolder = winforms.RadioButton()
		self.radioFolder.AutoSize = True
		self.radioFolder.Location = Point(12, 56)
		self.radioFolder.Text = 'Folder:'
		self.radioFolder.CheckedChanged += EventHandler(onFolderChecked)
		self.Controls.Add(self.radioFolder)

		folderList = winforms.ListBox()
		folderList.Location = Point(31, 79)
		folderList.SelectionMode = winforms.SelectionMode.MultiExtended
		folderList.Size = Size(301, 121)
		folderList.Anchor = \
			winforms.AnchorStyles.Top | winforms.AnchorStyles.Bottom | \
			winforms.AnchorStyles.Left | winforms.AnchorStyles.Right
		self.Controls.Add(folderList)

		for dir in db.get_upload_dirs():
			folderList.Items.Add(dir)

		def addClicked(sender, args):
			upload_dirs = db.get_upload_dirs()
			if upload_dirs:
				start_dir = upload_dirs[-1]
			else:
				start_dir = hplatform.get_default_path()
			browser = FolderBrowserWin(start_dir)
			if browser.ShowDialog() == winforms.DialogResult.OK:
				upload_dirs.append(browser.uploadFolder)
				db.set_upload_dirs(upload_dirs)
				folderList.Items.Add(browser.uploadFolder)
				self.changed = True
			browser.Dispose()

		addButton = winforms.Button()
		addButton.Location = Point(31, 208)
		addButton.Size = Size(62, 23)
		addButton.Text = 'Add...'
		addButton.Click += EventHandler(addClicked)
		addButton.Anchor = \
			winforms.AnchorStyles.Left | winforms.AnchorStyles.Bottom
		self.Controls.Add(addButton)

		def removeClicked(sender, args):
			upload_dirs = db.get_upload_dirs()
			new_upload_dirs = []
			i=0
			for dir in upload_dirs:
				if i not in folderList.SelectedIndices:
					new_upload_dirs.append(dir)
				i += 1
			db.set_upload_dirs(new_upload_dirs)
			folderList.Items.Clear()
			for dir in new_upload_dirs:
				folderList.Items.Add(dir)
			self.changed = True

		removeButton = winforms.Button()
		removeButton.Location = Point(99, 208)
		removeButton.Text = 'Remove'
		removeButton.Click += EventHandler(removeClicked)
		removeButton.Anchor = \
			winforms.AnchorStyles.Left | winforms.AnchorStyles.Bottom
		self.Controls.Add(removeButton)

		def okClicked(sender, args):
			self.Hide()
			self.DialogResult = winforms.DialogResult.OK

		okButton = winforms.Button()
		okButton.Size = Size(62, 23)
		okButton.Location = Point(270, 208)
		okButton.Text = 'OK'
		okButton.Click += EventHandler(okClicked)
		okButton.Anchor = \
			winforms.AnchorStyles.Right | winforms.AnchorStyles.Bottom 
		self.Controls.Add(okButton)

		if not itunes.get_library_file():
			self.radioITunes.Enabled = False
			db.set_upload_src('folder')

		if db.get_upload_src() == 'itunes':
			self.radioITunes.Checked = True
			self.radioFolder.Checked = False
		else:
			self.radioITunes.Checked = False
			self.radioFolder.Checked = True

		def formClosed(sender, args):
			if self.changed:
				upload.options_changed()
				self.changed = False
		self.FormClosed += EventHandler(formClosed)


class FolderBrowserWin(winforms.Form):
	def __init__(self, uploadFolder):
		global icon
		formSize = Size(367, 367)
		self.Size = formSize
		self.MinimumSize = formSize
		self.StartPosition = winforms.FormStartPosition.CenterScreen
		self.Text = 'Folder Select'
		self.Icon = icon

		self.uploadFolder = uploadFolder

		def okClicked(sender, args):
			self.Hide()
			self.DialogResult = winforms.DialogResult.OK

		okButton = winforms.Button()
		okButton.Size = Size(75, 23)
		okButton.Location = Point(190, 298)
		okButton.Text = 'OK'
		okButton.Click += EventHandler(okClicked)
		okButton.Anchor = \
			winforms.AnchorStyles.Right | winforms.AnchorStyles.Bottom 
		self.Controls.Add(okButton)

		def cancelClicked(sender, args):
			self.Hide()
			self.DialogResult = winforms.DialogResult.Cancel

		cancelButton = winforms.Button()
		cancelButton.Size = Size(75, 23)
		cancelButton.Location = Point(271, 298)
		cancelButton.Text = 'Cancel'
		cancelButton.Click += EventHandler(cancelClicked)
		cancelButton.Anchor = \
			winforms.AnchorStyles.Right | winforms.AnchorStyles.Bottom 
		self.Controls.Add(cancelButton)

		imageList = winforms.ImageList()
		imageList.Images.Add(Image.FromFile('folder.bmp'))
		imageList.Images.Add(Image.FromFile('hd.bmp'))
		imageList.Images.Add(Image.FromFile('cd.bmp'))

		treeview = winforms.TreeView()
		treeview.Size = Size(334, 280)
		treeview.Location = Point(13, 12)
		treeview.Anchor = \
			winforms.AnchorStyles.Top | winforms.AnchorStyles.Bottom | \
			winforms.AnchorStyles.Left | winforms.AnchorStyles.Right
		treeview.ImageList = imageList
		treeview.ImageIndex = 0
		self.Controls.Add(treeview)

		def add_children(node):
			if node.Nodes.Count != 1 or node.Nodes[0].Text != 'harmonize_dummy':
				return
			try:
				node.Nodes.Clear()
				children = dir_browser.get_dir_listing(node.FullPath + '\\')
				for child in children:
					new_node = node.Nodes.Add(child, child)
					if os.path.isdir(new_node.FullPath):
						new_node.Nodes.Add('harmonize_dummy')
				if len(self.path_list) == 1:
					treeview.SelectedNode = \
						node.Nodes[node.Nodes.IndexOfKey(self.path_list.pop(0))]
				elif self.path_list != []:
					node.Nodes[node.Nodes.IndexOfKey(self.path_list.pop(0))].\
						Expand()
			except WindowsError:
				pass #This is an access denied error

		def onBeforeExpand(sender, args):
			node = args.Node

			add_children(node)

		def onAfterSelect(sender, args):
			add_children(args.Node)
			self.uploadFolder = args.Node.FullPath

		treeview.BeforeExpand += EventHandler(onBeforeExpand)
		treeview.AfterSelect += EventHandler(onAfterSelect)

		for driveInfo in System.IO.DriveInfo.GetDrives():
			if driveInfo.DriveType == System.IO.DriveType.NoRootDirectory or \
					driveInfo.Name == 'A:\\':
				continue
			name = driveInfo.Name[:-1]
			node = treeview.Nodes.Add(name, name)
			if not (driveInfo.DriveType in 
					[System.IO.DriveType.CDRom, System.IO.DriveType.Unknown]):
				add_children(node)

			if driveInfo.DriveType == System.IO.DriveType.Fixed:
				node.ImageIndex = 1
				node.SelectedImageIndex = 1
			elif driveInfo.DriveType == System.IO.DriveType.CDRom:
				node.ImageIndex = 2
				node.SelectedImageIndex = 2
			node.Nodes.Add('harmonize_dummy')

		treeview.BeginUpdate()
		
		self.path_list = self.uploadFolder.split('\\')
		treeview.Nodes[treeview.Nodes.IndexOfKey(self.path_list.pop(0))].\
			Expand()
		
		treeview.EndUpdate()
		treeview.Focus()

winforms.Application.EnableVisualStyles()

if __name__ == '__main__':
	if not singleton.running():
		winforms.Application.Run(MainWin())
