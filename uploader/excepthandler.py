from decorator import decorator

@decorator
def exception_managed(fn, *args, **kws):
	try:
		fn(*args, **kws)
	except Exception, e:
		import pdb; pdb.set_trace()
