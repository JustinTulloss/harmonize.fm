import traceback as tb
from StringIO import StringIO
import sys, platform
import config, build

def exception_managed(fn):
	def wrapper(*args, **kws):
		try:
			fn(*args, **kws)
		except Exception, e:
			f_contents = StringIO()
			tb.print_tb(sys.exc_traceback, file=f_contents)
			contents = f_contents.getvalue()
			f_contents.close()

			contents += '\nplatform.uname():\n' + str(platform.uname())
			contents += '\nRepo version: ' + build.repo_version

			if config.current['debug']:
				import pdb; pdb.set_trace()
			try:
				conn = config.get_conn()
				conn.request('POST', '/upload/error', contents, 
								{'Content-Type':'text/plain'})
				conn.getresponse().read()
			except Exception:
				return

	return wrapper
