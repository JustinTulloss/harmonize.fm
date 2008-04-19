import pythoncom
pythoncom.CoInitialize()

import fb, itunes, upload, thread, dir_browser
import clr
import System
import System.IO
import System.Windows.Forms as winforms
from System.Drawing import Size, Point, Image
from System import EventHandler

class Rubicon(winforms.Form):
	def __init__(self):
		self.pagelist = [startPage, loginPage, uploadSelectPage, \
			folderSelectPage, uploadPage]
		#self.pagelist = [folderSelectPage]


		self.Locked = True
		formSize = Size(329, 332)
		self.Size = formSize
		self.MinimumSize = formSize
		self.StartPosition = winforms.FormStartPosition.CenterScreen
		self.Text = 'Rubicon Uploader'

		self.nextButton = winforms.Button()
		self.nextButton.Anchor = \
			winforms.AnchorStyles.Bottom | winforms.AnchorStyles.Right
		self.nextButton.Location = Point(234, 263)
		self.nextButton.Size = Size(75, 23)
		self.nextButton.Text = 'Next'
		self.nextButton.UseVisualStyleBackColor = True
		self.nextButton.Click += EventHandler(self.nextPage);
		self.Controls.Add(self.nextButton)

		self.prevButton = winforms.Button()
		self.prevButton.Anchor = \
			winforms.AnchorStyles.Bottom | winforms.AnchorStyles.Right
		self.prevButton.Location = Point(152, 263)
		self.prevButton.Size = Size(75, 23)
		self.prevButton.Text = 'Previous'
		self.prevButton.UseVisualStyleBackColor = True
		self.prevButton.Click += EventHandler(self.prevPage)
		self.Controls.Add(self.prevButton)

		self.panel = winforms.Panel()
		self.panel.Location = Point(12, 12)
		self.panel.Size = Size(297, 245)
		self.panel.Anchor = \
			winforms.AnchorStyles.Top | winforms.AnchorStyles.Bottom | \
			winforms.AnchorStyles.Left | winforms.AnchorStyles.Right
		self.Controls.Add(self.panel)

		self.setPage(0)

	def setPage(self, index):
		self.panel.Controls.Clear()
		
		#index = self.pagelist.index(page)
		if index == 0:
			self.prevButton.Enabled = False
		else:
			self.prevButton.Enabled = True

		if index+1 == len(self.pagelist):
			self.nextButton.Enabled = False
		else:
			self.nextButton.Enabled = True

		self.pageNum = index
		page = self.pagelist[index]
		page(self, self.panel)

	def nextPage(self, sender, args):
		self.setPage(self.pageNum + 1)

	def prevPage(self, sender, args):
		self.setPage(self.pageNum - 1)

	def run(self):
		winforms.Application.EnableVisualStyles()
		winforms.Application.Run(self)

def startPage(form, panel):
	textbox = winforms.Label()
	textbox.AutoSize = True
	textbox.Text = \
		'Welcome to the Rubicon Uploader\n\nPress Next to login to facebook'
	textbox.Location = Point(0, 2)
	panel.Controls.Add(textbox)

session_key = None

def loginPage(form, panel):
	global session_key
	
	textbox = winforms.Label()
	textbox.AutoSize = True
	textbox.Location = Point(0, 2)
	panel.Controls.Add(textbox)

	if session_key == None:
		textbox.Text = 'Please login to facebook to continue'
		form.nextButton.Enabled = False

		def callback(new_key):
			def updateLoginPage():
				global session_key

				textbox.Text = 'Login complete'
				form.nextButton.Enabled = True
				session_key = new_key

			delegate = winforms.MethodInvoker(updateLoginPage)
			form.Invoke(delegate)

		fb.login(callback)
	else:
		textbox.Text = 'Login complete'

uploadMethod = None
uploadFolder = upload.get_default_path()

def uploadSelectPage(form, panel):
	global uploadMethod

	textbox = winforms.Label()
	textbox.Text = 'Select how you want to upload'
	textbox.AutoSize = True
	textbox.Location = Point(0, 2)
	panel.Controls.Add(textbox)

	radioITunes = winforms.RadioButton()
	radioITunes.AutoSize = True
	radioITunes.Location = Point(4, 22)
	radioITunes.Text = 'Upload All Music in iTunes'
	panel.Controls.Add(radioITunes)
	
	radioFolder = winforms.RadioButton()
	radioFolder.AutoSize = True
	radioFolder.Location = Point(4, 45)
	radioFolder.Text = 'Upload All Music in a Folder'
	panel.Controls.Add(radioFolder)

	if itunes.get_library_file() == None:
		radioITunes.Enabled = False
		radioFolder.Checked = True
		uploadMethod = 'folder'

	if uploadMethod == 'itunes':
		radioITunes.Checked = True
	elif uploadMethod  == 'folder':
		radioFolder.Checked = True
	else:
		radioITunes.Checked = True
		uploadMethod = 'itunes'

	def checkedChanged(sender, args):
		global uploadMethod
		if radioITunes.Checked:
			uploadMethod = 'itunes'
		elif radioFolder.Checked:
			uploadMethod = 'folder'

	onCheckedChanged = EventHandler(checkedChanged)
	radioITunes.CheckedChanged += onCheckedChanged
	radioFolder.CheckedChanged += onCheckedChanged

def folderSelectPage(form, panel):
	global uploadMethod, uploadFolder

	if uploadMethod == 'itunes':
		form.nextPage(None, None)
		return

	textbox = winforms.Label()
	textbox.AutoSize = True
	textbox.Location = Point(0, 2)
	textbox.Text = 'Upload Folder:'
	panel.Controls.Add(textbox)

	folderLabel = winforms.Label()
	folderLabel.Location = Point(77, 2)
	folderLabel.Size = Size(216, 14)
	folderLabel.AutoEllipsis = True
	folderLabel.Anchor = \
		winforms.AnchorStyles.Top | winforms.AnchorStyles.Left | \
		winforms.AnchorStyles.Right
	panel.Controls.Add(folderLabel)

	tooltip = winforms.ToolTip(folderLabel)

	imageList = winforms.ImageList()
	imageList.Images.Add(Image.FromFile('folder.bmp'))
	imageList.Images.Add(Image.FromFile('hd.bmp'))
	imageList.Images.Add(Image.FromFile('cd.bmp'))

	treeview = winforms.TreeView()
	treeview.Location = Point(2, 20)
	treeview.Size = Size(293, 224)
	treeview.Anchor = \
		winforms.AnchorStyles.Top | winforms.AnchorStyles.Bottom | \
		winforms.AnchorStyles.Left | winforms.AnchorStyles.Right
	treeview.ImageList = imageList
	treeview.ImageIndex = 0
	panel.Controls.Add(treeview)

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
		global uploadFolder

		add_children(args.Node)
		uploadFolder = args.Node.FullPath
		folderLabel.Text = args.Node.FullPath
		tooltip.SetToolTip(folderLabel, args.Node.FullPath)

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

	treeview.SelectedNode = getNode(uploadFolder)
	treeview.Focus()
	"""
	def expandToPath(path):
		def expandToPath_aux(node, path_list):
			next_node_name = path_list.pop(0)
			next_node = node.Nodes[node.Nodes.IndexOfKey(next_node_name)]
			if path_list == []:
				treeview.SelectedNode = next_node
			else:
	"""
		

def uploadPage(form, panel):
	form.prevButton.Enabled = False
	
	textbox = winforms.Label()
	textbox.Text = 'Upload starting...'
	textbox.AutoSize = True
	textbox.Location = Point(0, 2)
	panel.Controls.Add(textbox)

	class Progressbar(object):
		def __init__(self):
			self.progressbar = winforms.ProgressBar()
			self.progressbar.Location = Point(3, 29)
			self.progressbar.Size = Size(288, 23)
			self.progressbar.Style = winforms.ProgressBarStyle.Marquee
			panel.Controls.Add(self.progressbar)

		def init(self, total_songs):
			self.progressbar.Maximum = total_songs
			self.progressbar.Style = winforms.ProgressBarStyle.Blocks

		def update(self, songs_left):
			self.progressbar.Style = winforms.ProgressBarStyle.Blocks
			self.progressbar.Value = self.progressbar.Maximum - songs_left

		def spin(self):
			self.progressbar.Style = winforms.ProgressBarStyle.Marquee
	
	progress_updater = Progressbar()

	def uploader():
		global uploadMethod, uploadFolder
		if uploadMethod == 'itunes':
			tracks = filter(upload.is_music_file,
							itunes.ITunes().get_all_track_filenames())
		elif uploadMethod == 'folder':
			tracks = upload.get_music_files(uploadFolder)

		def main_thread_delegated(fn):
			def wrapper(*args):
				delegate = winforms.MethodInvoker(lambda: fn(*args))
				form.Invoke(delegate)

			return wrapper


		class Callback(object):
			@main_thread_delegated
			def init(self, msg, total_songs):
				textbox.Text = msg
				progress_updater.init(total_songs)

			@main_thread_delegated
			def update(self, msg, songs_left):
				textbox.Text = msg
				progress_updater.update(songs_left)

			@main_thread_delegated
			def error(self, msg):
				textbox.Text = msg
				progress_updater.spin()

		callback = Callback()

		upload.upload_files(tracks, callback)

	thread.start_new_thread(uploader, ())


if __name__ == '__main__':
	Rubicon().run()
