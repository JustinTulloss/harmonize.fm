import pythoncom
pythoncom.CoInitialize()

import fb, itunes, upload, thread
import clr
import System
import System.Windows.Forms as winforms
from System.Drawing import Size, Point
from System import EventHandler

class Rubicon(winforms.Form):
	def __init__(self):
		self.pagelist = [startPage, loginPage, uploadSelectPage, \
			folderSelectPage, uploadPage]

		self.Locked = True
		formSize = Size(329, 332)
		self.Size = formSize
		self.MinimunSize = formSize
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
	textbox.Text = 'Upload Folder'
	panel.Controls.Add(textbox)

	changeButton = winforms.Button()
	changeButton.Location = Point(80, -1)
	changeButton.Size = Size(52, 20)
	changeButton.Text = 'Change'
	panel.Controls.Add(changeButton)

	folderLabel = winforms.Label()
	folderLabel.Location = Point(3, 23)
	folderLabel.AutoSize = True
	folderLabel.Text = uploadFolder
	panel.Controls.Add(folderLabel)

	def onChangeClick(sender, args):
		global uploadFolder

		folderBrowser = winforms.FolderBrowserDialog()
		folderBrowser.SelectedPath = upload.get_default_path()
		folderBrowser.ShowNewFolderButton = False
		res = folderBrowser.ShowDialog()
	
		if res == winforms.DialogResult.OK:
			uploadFolder = folderBrowser.SelectedPath
			folderLabel.Text = uploadFolder
	
	changeButton.Click += EventHandler(onChangeClick)

def uploadPage(form, panel):
	form.prevButton.Enabled = False
	
	textbox = winforms.Label()
	textbox.Text = 'Upload starting...'
	textbox.AutoSize = True
	textbox.Location = Point(0, 2)
	panel.Controls.Add(textbox)

	def make_progressbar():
		progressbar = winforms.ProgressBar()
		progressbar.Location = Point(3, 29)
		progressbar.Size = Size(288, 23)
		progressbar.Style = winforms.ProgressBarStyle.Marquee
		panel.Controls.Add(progressbar)

		def update_progressbar(songs_left):
			if progressbar.Style == winforms.ProgressBarStyle.Marquee:
				progressbar.Maximum = songs_left
				progressbar.Style = winforms.ProgressBarStyle.Blocks
			else:
				progressbar.Value = progressbar.Maximum - songs_left
		return update_progressbar
	
	progress_updater = make_progressbar()

	def uploader():
		global uploadMethod, uploadFolder, session_key
		if uploadMethod == 'itunes':
			tracks = filter(upload.is_music_file,
							itunes.ITunes().get_all_track_filenames())
		elif uploadMethod == 'folder':
			tracks = upload.get_music_files(uploadFolder)

		def callback(songs_left):
			def updateSongs():
				if songs_left != 0:
					textbox.Text = '%s songs remaining' % songs_left
				else:
					textbox.Text = 'Upload complete!'
				progress_updater(songs_left)

			delegate = winforms.MethodInvoker(updateSongs)
			form.Invoke(delegate)

		upload.upload_files(tracks, session_key, callback)

	thread.start_new_thread(uploader, ())


if __name__ == '__main__':
	Rubicon().run()
