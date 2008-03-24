import sys
from distutils.core import setup

r_scripts = ['fb.py', 'dir_browser.py', 'upload.py', 'itunes.py']

if sys.platform == 'darwin':
	import py2app
	setup(
		name='Rubicon',
		setup_requires=['py2app'],		
		app=['Rubicon_osx.py'],
		scripts=r_scripts,
		data_files=['MainMenu.nib']
	)
elif sys.platform == 'win32':
	import py2exe
	setup(
		name='Rubicon',
		setup_requires=['py2exe'],
		windows=['Rubicon_win.py'],
		scripts=r_scripts,
		data_files=['Python.Runtime.dll']
	)
