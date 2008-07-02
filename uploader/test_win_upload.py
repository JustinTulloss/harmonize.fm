from Harmonize_win import Application

import thread

def create_printer(val):
	def fn():
		print val + ' clicked!'
	return fn

def options_changed(src, dirs):
	print 'Upload src: %s, Upload dirs: %s' % (src, dirs)

upload_window = Application('itunes', [r'C:\MyMusic'], False,
							create_printer('listen_clicked'),
							create_printer('login_clicked'),
							create_printer('exit_clicked'),
							options_changed)

def exit_clicked():
	print 'exit_clicked'
	upload_window.quit()

upload_window.exit_clicked = exit_clicked

upload_window.start()
