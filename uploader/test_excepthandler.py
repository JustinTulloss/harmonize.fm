from excepthandler import exception_managed, set_gui_error

def gui_error():
	print 'Gui error received:'

@exception_managed
def except_fn():
	raise Exception('testing')

if __name__ == '__main__':
	set_gui_error(gui_error)
	except_fn()
