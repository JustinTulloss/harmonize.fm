import clr
import System, System.IO
import System.Windows.Forms as winforms
from System.Drawing import Size, Point, Image
from System import EventHandler

import os
import hplatform, dir_browser

class OptionWin(winforms.Form):
	def __init__(self, icon, upload_mode, upload_dirs, itunes_enabled):
		self.upload_dirs = upload_dirs

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

		self.radioITunes = winforms.RadioButton()
		self.radioITunes.AutoSize = True
		self.radioITunes.Location = Point(12, 33)
		self.radioITunes.Text = 'iTunes'
		self.radioITunes.Enabled = itunes_enabled
		self.Controls.Add(self.radioITunes)

		self.radioFolder = winforms.RadioButton()
		self.radioFolder.AutoSize = True
		self.radioFolder.Location = Point(12, 56)
		self.radioFolder.Text = 'Folder:'
		self.Controls.Add(self.radioFolder)

		if upload_mode == 'itunes':
			self.radioITunes.Checked = True
		else:
			self.radioFolder.Checked = True

		def checked(s, e):
			self.changed = True
		checked_handler = EventHandler(checked)
		self.radioITunes.CheckedChanged += checked_handler
		self.radioFolder.CheckedChanged += checked_handler

		folderList = winforms.ListBox()
		folderList.Location = Point(31, 79)
		folderList.SelectionMode = winforms.SelectionMode.MultiExtended
		folderList.Size = Size(301, 121)
		folderList.Anchor = \
			winforms.AnchorStyles.Top | winforms.AnchorStyles.Bottom | \
			winforms.AnchorStyles.Left | winforms.AnchorStyles.Right
		self.Controls.Add(folderList)

		for dir in self.upload_dirs:
			folderList.Items.Add(dir)

		def addClicked(sender, args):
			if self.upload_dirs:
				start_dir = self.upload_dirs[-1]
			else:
				start_dir = hplatform.get_default_path()
			browser = FolderBrowserWin(icon, start_dir)
			if browser.ShowDialog() == winforms.DialogResult.OK:
				self.upload_dirs.append(browser.uploadFolder)
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
			new_upload_dirs = []
			i=0
			for dir in self.upload_dirs:
				if i not in folderList.SelectedIndices:
					new_upload_dirs.append(dir)
				i += 1
			folderList.Items.Clear()
			for dir in new_upload_dirs:
				folderList.Items.Add(dir)
			self.upload_dirs = new_upload_dirs
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

	def activate(self):
		self.Show()
		if self.WindowState == winforms.FormWindowState.Minimized:
			self.WindowState = winforms.FormWindowState.Normal
		self.Activate()


class FolderBrowserWin(winforms.Form):
	def __init__(self, icon, uploadFolder):
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
