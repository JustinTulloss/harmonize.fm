import pythoncom
pythoncom.CoInitialize()

import fb, itunes, upload, thread, dir_browser
import clr
import System
import System.IO
import System.Windows.Forms as winforms
from System.Drawing import Size, Point, Image
from System import EventHandler

class MainWin(winforms.Form):
	def __init__(self):
		formSize = Size(173, 102)
		self.Size = formSize
		self.MinimumSize = formSize
		self.MaximumSize = formSize
		self.StartPosition = winforms.FormStartPosition.CenterScreen
		self.Text = 'Harmonize'

		self.mainLabel = winforms.Label()
		self.mainLabel.AutoSize = True
		self.mainLabel.Location = Point(12, 9)
		self.mainLabel.Text = 'Click Login to start uploading'
		self.Controls.Add(self.mainLabel)

		loginButton = winforms.Button()
		loginButton.Size = Size(65, 23)
		loginButton.Location = Point(15, 26)
		loginButton.Text = 'Login'
		loginButton.Click += EventHandler(self.loginClicked)
		self.Controls.Add(loginButton)

		def optionClicked(sender, args):
			self.AddOwnedForm(self.optionWin)
			self.optionWin.ShowDialog()

		self.optionsButton = winforms.Button()
		self.optionsButton.Size = Size(65, 23)
		self.optionsButton.Location = Point(86, 26)
		self.optionsButton.Text = 'Options...'
		self.optionsButton.Click += EventHandler(optionClicked)
		self.Controls.Add(self.optionsButton)

		self.optionWin = OptionWin()

	def loginClicked(self, sender, args):
		def callback(session_key):
			self.Invoke(winforms.MethodInvoker(self.startUploading))

		fb.login(callback)	
	
	def startUploading(self):
		self.Controls.Clear()

		self.mainLabel = winforms.Label()
		self.mainLabel.Location = Point(12, 9)
		self.mainLabel.AutoSize = True
		self.mainLabel.Text = 'Upload starting...'
		self.Controls.Add(self.mainLabel)

		self.progressbar = winforms.ProgressBar()
		self.Controls.Add(self.progressbar)
		self.progressbar.Size = Size(133, 14)
		self.progressbar.Location = Point(12, 42)
		self.progressbar.Style = winforms.ProgressBarStyle.Marquee

		thread.start_new_thread(self.uploader, ())

	def uploader(self):
		tracks = self.optionWin.get_tracks()

		def main_thread_delegated(fn):
			def wrapper(*args):
				delegate = winforms.MethodInvoker(lambda: fn(*args))
				self.Invoke(delegate)

			return wrapper

		textbox = self.mainLabel
		progressbar = self.progressbar

		class Callback(object):
			@main_thread_delegated
			def init(self, msg, total_songs):
				textbox.Text = msg
				progressbar.Maximum = total_songs
				progressbar.Style = winforms.ProgressBarStyle.Blocks

			@main_thread_delegated
			def update(self, msg, songs_left):
				textbox.Text = msg
				progressbar.Style = winforms.ProgressBarStyle.Blocks
				progressbar.Value = progressbar.Maximum - songs_left

			@main_thread_delegated
			def error(self, msg):
				textbox.Text = msg
				progressbar.Style = winforms.ProgressBarStyle.Marquee

		callback = Callback()

		upload.upload_files(tracks, callback)

class OptionWin(winforms.Form):
	def __init__(self):
		formSize = Size(367, 184)
		self.Size = formSize
		self.MinimumSize = formSize
		self.StartPosition = winforms.FormStartPosition.CenterScreen
		self.Text = 'Options'

		label = winforms.Label()
		label.AutoSize = True
		label.Location = Point(12, 9)
		label.Text = 'Select where you would like to upload from'
		self.Controls.Add(label)

		self.radioITunes = winforms.RadioButton()
		self.radioITunes.AutoSize = True
		self.radioITunes.Location = Point(16, 27)
		self.radioITunes.Text = 'iTunes'
		self.Controls.Add(self.radioITunes)

		self.radioFolder = winforms.RadioButton()
		self.radioFolder.AutoSize = True
		self.radioFolder.Location = Point(16, 51)
		self.radioFolder.Text = 'Folder:'
		self.Controls.Add(self.radioFolder)

		self.uploadFolderBox = winforms.TextBox()
		self.uploadFolderBox.Size = Size(247, 20)
		self.uploadFolderBox.Location = Point(36, 74)
		self.uploadFolderBox.Text = upload.get_default_path()
		self.uploadFolderBox.ReadOnly = True
		self.Controls.Add(self.uploadFolderBox)

		def browseClicked(sender, args):
			browser = FolderBrowserWin(self.selected_folder())
			if browser.ShowDialog() == winforms.DialogResult.OK:
				self.set_selected_folder(browser.uploadFolder)
			browser.Dispose()

		browseButton = winforms.Button()
		browseButton.Size = Size(61, 23)
		browseButton.Location = Point(287, 72)
		browseButton.Text = 'Browse...'
		browseButton.Click += EventHandler(browseClicked)
		self.Controls.Add(browseButton)

		def okClicked(sender, args):
			self.Hide()
			self.DialogResult = winforms.DialogResult.OK

		okButton = winforms.Button()
		okButton.Size = Size(61, 23)
		okButton.Location = Point(287, 115)
		okButton.Text = 'OK'
		okButton.Click += EventHandler(okClicked)
		self.Controls.Add(okButton)

		if itunes.get_library_file() != None:
			self.radioITunes.Checked = True
		else:
			self.radioITunes.Checked = False
			self.radioITunes.Enabled = False
			self.radioFolder.Checked = True

	def get_tracks(self):
		if self.radioITunes.Checked:
			return filter(upload.is_music_file,
							itunes.ITunes().get_all_track_filenames())
		else:
			return upload.get_music_files(self.selected_folder())

	def selected_folder(self):
		return self.uploadFolderBox.Text
	
	def set_selected_folder(self, value):
		self.uploadFolderBox.Text = value
		

class FolderBrowserWin(winforms.Form):
	def __init__(self, uploadFolder):
		formSize = Size(367, 367)
		self.Size = formSize
		self.MinimumSize = formSize
		self.StartPosition = winforms.FormStartPosition.CenterScreen
		self.Text = 'Folder Select'

		self.uploadFolder = uploadFolder

		def okClicked(sender, args):
			self.Hide()
			self.DialogResult = winforms.DialogResult.OK

		okButton = winforms.Button()
		okButton.Size = Size(75, 23)
		okButton.Location = Point(190, 298)
		okButton.Text = 'OK'
		okButton.Click += EventHandler(okClicked)
		self.Controls.Add(okButton)

		def cancelClicked(sender, args):
			self.Hide()
			self.DialogResult = winforms.DialogResult.Cancel

		cancelButton = winforms.Button()
		cancelButton.Size = Size(75, 23)
		cancelButton.Location = Point(271, 298)
		cancelButton.Text = 'Cancel'
		cancelButton.Click += EventHandler(cancelClicked)
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
			if node.Nodes.Count != 0:
				return
			try:
				children = dir_browser.get_dir_listing(node.FullPath + '\\')
				for child in children:
					node.Nodes.Add(child, child)
			except WindowsError:
				pass #This is an access denied error

		def onBeforeExpand(sender, args):
			node = args.Node

			for childNode in node.Nodes:
				add_children(childNode)

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

		def getNode(path):
			path_list = path.split('\\')
			node = treeview
			for next_node in path_list:
				node = node.Nodes[node.Nodes.IndexOfKey(next_node)]
				add_children(node)
			
			return node

		treeview.SelectedNode = getNode(self.uploadFolder)
		treeview.Focus()

winforms.Application.EnableVisualStyles()

if __name__ == '__main__':
	winforms.Application.Run(MainWin())
