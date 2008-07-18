class GuiManager(object):
	def __init__(self, gui, total_uploaded):
		self.gui = gui
		self.gui.set_uploaded(total_uploaded)
		self.gui.set_remaining(0)
		self.gui.set_skipped(0)
		if total_uploaded == 0:
			self.gui.enable_listen(False)
		else:
			self.gui.enable_listen(True)

		self.uploaded = total_uploaded
		self.skipped = 0
		self.remaining = 0

	def start_search(self):
		self.gui.set_msg('Searching for music...')
		self.gui.enable_login(False)
		self.gui.enable_options(True)

	def start_auth(self, upload_src):
		self.gui.enable_login(True)
		msg = 'Music has been found that has not been uploaded\n'
		if upload_src == 'itunes':
			msg += 'Click Login to start uploading your iTunes library'
		else:
			msg += 'Click Login to start uploading your music'
		self.gui.set_msg(msg)

	def end_auth(self):
		self.gui.enable_login(False)
		self.gui.set_msg('Login complete, uploading will begin shortly')
		self.gui.activate()

	def start_reauth(self):
		self.gui.enable_login(True)
		self.gui.set_msg('You need to re-login to continue\nClick "Save my login" on login page to stay logged in')

	def end_reauth(self):
		self.gui.enable_login(False)
		self.gui.set_msg('Login complete, uploading will resume shortly')
		self.gui.activate()

	def conn_error(self):
		self.gui.set_msg('Error connecting to server,\nWill retry in a moment')
		self.gui.set_progress(True)

	def no_music_found(self):
		self.gui.set_msg('No music found!\nClick Options to add some')

	def no_new_music(self):
		self.gui.set_msg('No new music to upload...')
		self.gui.set_progress(False, 0.0)

	def start_analysis(self, total_tracks):
		self.gui.set_msg('Analyzing library...')
		self.gui.set_progress(False, 0.0)
		self.gui.enable_options(False)
		self.total_tracks = float(total_tracks)
		self.tracks_analyzed = 0

	def file_analyzed(self):
		self.gui.set_msg('Analyzing library...')
		self.tracks_analyzed += 1
		self.gui.set_progress(False, (self.tracks_analyzed/self.total_tracks))

	def file_skipped(self):
		self.skipped += 1
		self.gui.set_skipped(self.skipped)

	def file_auto_uploaded(self):
		self.uploaded += 1
		self.gui.set_uploaded(self.uploaded)

	def file_queued(self):
		self.remaining += 1
		self.gui.set_remaining(self.remaining)


	def start_upload(self, filename, file_len):
		self.gui.set_msg(u'Uploading file:\n%s' % filename)
		self.gui.set_progress(False, 0.0)
		self.file_len = float(file_len)
		self.amount_uploaded = 0

	def file_uploaded(self):
		self.uploaded += 1
		self.remaining -= 1
		self.gui.set_uploaded(self.uploaded)
		self.gui.set_remaining(self.remaining)

	def upload_progress(self, amount_uploaded):
		self.amount_uploaded += amount_uploaded
		self.gui.set_progress(False, self.amount_uploaded/self.file_len)

	def activate(self):
		self.gui.activate()

	def upload_complete(self):
		self.gui.set_msg('Upload complete!')
		self.gui.enable_options(True)

	def fatal_error(self):
		self.gui.enable_options(False)
		self.gui.fatal_error('A fatal has occured in the Harmonizer.\n\nPlease exit the program and start it again.')
