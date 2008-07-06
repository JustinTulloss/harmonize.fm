import traceback as tb
from StringIO import StringIO
import sys, platform
import config

repo_version = "${repo_version}"

gui_error = None

def set_gui_error(new_gui_error):
	global gui_error
	gui_error = new_gui_error

def exception_managed(fn):
	def wrapper(*args, **kws):
		global gui_error, repo_version

		try:
			return fn(*args, **kws)
		except Exception, e:
			try:
				f_contents = StringIO()
				tb.print_tb(sys.exc_traceback, file=f_contents)
				contents = f_contents.getvalue()
				f_contents.close()

				contents += str(e) + '\n'
				contents += '\nplatform.uname():\n' + str(platform.uname())
				contents += '\nRepo version: ' + repo_version

				if config.current['debug']:
					import pdb; pdb.set_trace()

				if gui_error != None:
					gui_error()

				conn = config.get_conn()
				conn.request('POST', '/upload/error', contents, 
								{'Content-Type':'text/plain'})
				conn.getresponse().read()
			except Exception:
				return

	return wrapper
