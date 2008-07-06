from ${window_file} import Application
from guimanager import GuiManager
from itunes import get_library_file
from db import db
from excepthandler import exception_managed, set_gui_error

import thread, webbrowser, sys
import singleton, fb


@exception_managed
def main():
	if singleton.running():
		sys.exit(1)

	window = Application(db.upload_src, db.upload_dirs, 
							get_library_file() != None)

	def app_started():
		def login_clicked():
			import upload
			fb.login(upload.login_callback)

		def options_changed(upload_src, upload_dirs):
			import upload
			db.upload_src = upload_src
			db.upload_dirs = upload_dirs
			upload.options_changed()

		def exit_clicked():
			singleton.atexit()
			window.quit()

		window.login_clicked = login_clicked
		window.options_changed = options_changed
		window.exit_clicked = exit_clicked
		window.listen_clicked = fb.listen_now

		singleton.set_callback(window.activate)

		def start_uploader():
			import upload
			guimgr = GuiManager(window, db.total_uploaded_tracks())
			set_gui_error(guimgr.fatal_error)
			upload.start_uploader(guimgr)

		thread.start_new_thread(start_uploader, ())

	window.app_started = app_started

	window.start()

if __name__ == '__main__':
	main()
