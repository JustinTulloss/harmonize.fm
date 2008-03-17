from distutils.core import setup
import py2app
setup(
	app=['Rubicon.py'],
	scripts=['fb.py', 'dir_browser.py', 'upload.py', 'itunes.py'],
	data_files=['MainMenu.nib']
)
