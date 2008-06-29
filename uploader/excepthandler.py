from decorator import decorator
import traceback as tb
from StringIO import StringIO
import sys
import config

@decorator
def exception_managed(fn, *args, **kws):
	try:
		fn(*args, **kws)
	except Exception, e:
		f_contents = StringIO()
		tb.print_tb(sys.exc_traceback, file=f_contents)
		contents = f_contents.getvalue()
		f_contents.close()

		try:
			conn = config.get_conn()
			conn.request('POST', '/upload/error', contents, 
							{'Content-Type':'text/plain'})
			conn.getresponse().read()
		except Exception:
			return

		if config.current['debug']:
			import pdb; pdb.set_trace()
