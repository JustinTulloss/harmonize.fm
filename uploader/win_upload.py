import clr
import System.Windows.Forms as winforms
from System import EventHandler
from System.Drawing import Size, Point, ContentAlignment

class UploadWin(winforms.Form):
	def __init__(self, icon):
		formSize = Size(308, 213)
		self.Size = formSize
		self.MinimumSize = formSize
		self.MaximumSize = formSize
		self.StartPosition = winforms.FormStartPosition.CenterScreen
		self.Text = 'Harmonizer'
		self.Icon = icon
		self.MaximizeBox = False

		def closing(s, e):
			if e.CloseReason == winforms.CloseReason.UserClosing:
				e.Cancel = True
				self.Hide()
			else:
				self.appIcon.Dispose()
		self.FormClosing += EventHandler(closing)

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
		totalUploadedLabel.Text = 'Songs Uploaded to harmonize.fm'
		self.Controls.Add(totalUploadedLabel)

		remainingLabel = winforms.Label()
		remainingLabel.AutoSize = True
		remainingLabel.Location = Point(13, 33)
		remainingLabel.Text = 'Songs Remaining to Upload'
		self.Controls.Add(remainingLabel)

		skippedLabel = winforms.Label()
		skippedLabel.AutoSize = True
		skippedLabel.Location = Point(13, 53)
		skippedLabel.Text = 'Songs Skipped'
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
		self.Controls.Add(self.loginButton)

		self.optionsButton = winforms.Button()
		self.optionsButton.Size = Size(54, 23)
		self.optionsButton.Location = Point(173, 144)
		self.optionsButton.Text = 'Options'
		self.Controls.Add(self.optionsButton)

		self.listenButton = winforms.Button()
		self.listenButton.Location = Point(16, 144)
		self.listenButton.Size = Size(54, 23)
		self.listenButton.Text = 'Listen'
		self.listenButton.Enabled = False
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

		self.appIcon = winforms.NotifyIcon()
		self.appIcon.Icon = icon
		self.appIcon.Text = 'Harmonizer'

		menu = winforms.ContextMenu()
		statusMenuItem = winforms.MenuItem('Status')

		activate_handler = EventHandler(lambda s, e: self.activate())

		self.appIcon.DoubleClick += activate_handler

		statusMenuItem.Click += activate_handler
		menu.MenuItems.Add(statusMenuItem)
		self.optionsMenuItem = winforms.MenuItem('Options')
		menu.MenuItems.Add(self.optionsMenuItem)
		self.exitMenuItem = winforms.MenuItem('Exit')
		menu.MenuItems.Add(self.exitMenuItem)
			
		self.appIcon.ContextMenu = menu
		self.appIcon.Visible = True

	def activate(self):
		self.Show()
		if self.WindowState == winforms.FormWindowState.Minimized:
			self.WindowState = winforms.FormWindowState.Normal
		self.Activate()

	def fatal_error(self, msg):
		self.Controls.Clear()

		panel = winforms.Panel()
		panel.Size = self.Size

		text = winforms.Label()
		text.Location = Point(13, 13)
		text.Size = Size(275, 125)
		text.Text = msg
		panel.Controls.Add(text)

		self.exitButton = winforms.Button()
		self.exitButton.Location = Point(233, 144)
		self.exitButton.Size = Size(54, 23)
		self.exitButton.Text = 'Exit'
		panel.Controls.Add(self.exitButton)

		self.Controls.Add(panel)
