import traceback as tb
from StringIO import StringIO
import sys, platform
import config

repo_version = "${repo_version}"

gui_error = None

def set_gui_error(new_gui_error):
	global gui_error
	gui_error = new_gui_error

def get_tb():
	f_contents = StringIO()
	tb.print_tb(sys.exc_traceback, file=f_contents)
	contents = f_contents.getvalue()
	f_contents.close()
	return contents

def exception_managed(fn):
	def wrapper(*args, **kws):
		global gui_error, repo_version

		try:
			return fn(*args, **kws)
		except Exception, e:
			contents = get_tb()

			contents += str(e) + '\n'
			contents += '\nplatform.uname():\n' + str(platform.uname())
			contents += '\nRepo version: ' + repo_version

			if config.current['debug']:
				import pdb; pdb.set_trace()

			if gui_error != None:
				gui_error()

			try:
				conn = config.get_conn()
				conn.request('POST', '/upload/error', contents, 
								{'Content-Type':'text/plain'})
				conn.getresponse().read()
			except Exception:
				open('error.log', 'w+').write(
						'Error sending traceback:\n' + contents)
				return

	return wrapper
