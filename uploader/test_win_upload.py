try:
	from Harmonize_win import Application
except ImportError:
	from Harmonize_osx import Application
from guimanager import GuiManager

import thread

def create_printer(val):
	def fn():
		print val + ' clicked!'
	return fn

def options_changed(src, dirs):
	print 'Upload src: %s, Upload dirs: %s' % (src, dirs)

window = Application('itunes', [r'C:\MyMusic'], False,
							create_printer('listen_clicked'),
							create_printer('login_clicked'),
							create_printer('exit_clicked'),
							options_changed,
							create_printer('app_started'))

def exit_clicked():
	print 'exit_clicked'
	window.quit()

def app_started():
	def test_window():
		print 'Setting initial values'
		window.set_uploaded(1)
		window.set_remaining(2)
		window.set_skipped(3)
		window.set_progress(False, .5)
		window.set_msg('Testing\nTwo rows')
		window.enable_listen(True)
		window.enable_options(True)
		window.enable_login(False)
		raw_input()
		window.fatal_error('An error occurred')
		window.enable_options(False)
		
	def test_guimgr():
		guimgr = GuiManager(window, 5)
		guimgr.start_auth('folder')
		raw_input()
		guimgr.end_auth()
		raw_input()
		guimgr.start_search()
		raw_input()
		guimgr.no_music_found()
		raw_input()
		guimgr.no_new_music()
		raw_input()
		guimgr.start_analysis(5)
		raw_input()
		guimgr.file_analyzed()
		guimgr.file_analyzed()
		guimgr.file_analyzed()
		guimgr.file_auto_uploaded()
		guimgr.file_skipped()
		guimgr.file_queued()
		guimgr.file_queued()
		guimgr.file_queued()
		guimgr.file_analyzed()
		guimgr.file_analyzed()
		raw_input()
		guimgr.upload_complete()
		raw_input()
		guimgr.conn_error()
		raw_input()
		guimgr.start_reauth()
		raw_input()
		guimgr.end_reauth()
		raw_input()
		guimgr.fatal_error()

	def app_started_th():
		#test_window()
		test_guimgr()

	thread.start_new_thread(app_started_th, ())

window.app_started = app_started

window.exit_clicked = exit_clicked

window.start()
