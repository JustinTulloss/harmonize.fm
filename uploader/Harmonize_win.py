import pythoncom
pythoncom.CoInitialize()

import clr
import System.Windows.Forms as winforms
from System import EventHandler
from System.Drawing import Size, Point, ContentAlignment, Bitmap, Icon

from win_upload import UploadWin
from win_options import OptionWin

winforms.Application.EnableVisualStyles()

def Application(upload_mode, upload_dirs, itunes_enabled,
				listen_clicked=None, login_clicked=None, 
				exit_clicked=None, options_changed=None):

	icon = Icon.FromHandle(Bitmap('icon.bmp').GetHicon())
	mainWin = UploadWin(icon)
	optionWin = OptionWin(icon, upload_mode, upload_dirs, itunes_enabled)
	mainWin.AddOwnedForm(optionWin)

	def main_thread_invoke(fn):
		def wrapper(*args, **kws):
			mainWin.Invoke(winforms.MethodInvoker(lambda: fn(*args, **kws)))
		return wrapper

	class Delegate(object):
		def __init__(self):
			self.listen_clicked = listen_clicked
			self.login_clicked = login_clicked
			self.exit_clicked = exit_clicked
			self.options_changed = options_changed

			self.options_dialog_open = False

			def create_handler(name):
				def caller(sender, args):
					if getattr(self, name) != None:
						getattr(self, name)()
				return EventHandler(caller)

			mainWin.listenButton.Click += create_handler('listen_clicked')
			mainWin.loginButton.Click += create_handler('login_clicked')
			mainWin.exitMenuItem.Click += create_handler('exit_clicked')

			def options_clicked(s, e):
				if self.options_dialog_open:
					optionWin.activate()
					return

				self.options_dialog_open = True
				optionWin.ShowDialog()
				if optionWin.changed:
					optionWin.changed = False
					if optionWin.radioITunes.Checked:
						src = 'itunes'
					else:
						src = 'folder'
						
					options_changed(src, optionWin.upload_dirs)
				self.options_dialog_open = False

			options_handler = EventHandler(options_clicked)

			mainWin.optionsButton.Click += options_handler
			mainWin.optionsMenuItem.Click += options_handler

		@main_thread_invoke
		def set_uploaded(self, value):
			mainWin.totalUploaded.Text = str(value)

		@main_thread_invoke
		def set_remaining(self, value):
			mainWin.remaining.Text = str(value)

		@main_thread_invoke
		def set_skipped(self, value):
			mainWin.skipped.Text = str(value)

		@main_thread_invoke
		def set_progress(self, spinning, value=None):
			if spinning:
				mainWin.progress.Style = winforms.ProgressBarStyle.Marquee
			else:
				mainWin.progress.Style = winforms.ProgressBarStyle.Continuous

			if val != None:
				mainWin.progress.Value = int(val*100)

		@main_thread_invoke
		def set_msg(self, msg):
			mainWin.info.Text = msg

		@main_thread_invoke
		def enable_listen(self, enabled):
			mainWin.listenButton.Enabled = enabled

		@main_thread_invoke
		def enable_options(self, enabled):
			mainWin.optionsButton.Enabled = enabled

		@main_thread_invoke
		def enable_login(self, enabled):
			mainWin.loginButton.Enabled = enabled

		@main_thread_invoke
		def activate(self):
			mainWin.activate()

		@main_thread_invoke
		def quit(self):
			mainWin.quit = True
			winforms.Application.Exit()

		def start(self):
			winforms.Application.Run(mainWin)

	return Delegate()
