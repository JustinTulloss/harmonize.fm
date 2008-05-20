import sys
from distutils.core import setup

r_scripts = ['fb.py', 'dir_browser.py', 'upload.py', 'itunes.py', 'tags.py', 
			 'config.py']

if sys.platform == 'darwin':
	import py2app
	setup(
		name='Harmonize',
		setup_requires=['py2app'],		
		app=['Harmonize_osx.py'],
		scripts=r_scripts,
		data_files=['MainMenu.nib']
	)
elif sys.platform == 'win32':
	import py2exe
	setup(
		windows=[{'script':'Harmonize_win.py',
				  'dest_base':'Harmonize'}],
		scripts=r_scripts,
		data_files=['Python.Runtime.dll', 'folder.bmp', 'hd.bmp', 'cd.bmp']
	)
