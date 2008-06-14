import sys
from distutils.core import setup
import os

r_scripts = ['fb.py', 'dir_browser.py', 'upload.py', 'itunes.py', 'tags.py', 
			 'config.py', 'genpuid.py', 'db.py', 'hplatform.py']

if sys.platform == 'darwin':
	if not os.path.exists('genpuid_bin_osx'):
		print 'genpuid directory missing, download it at musicip.com'
	import py2app
	setup(
		name='Harmonize',
		setup_requires=['py2app'],		
		app=['Harmonize_osx.py'],
		scripts=r_scripts,
		data_files=['MainMenu.nib', 
					'genpuid_bin_osx/genpuid', 'genpuid_bin_osx/AACTagReader',
					'genpuid_bin_osx/mipcore']
	)
elif sys.platform == 'win32':
	import py2exe
	setup(
		windows=[{'script':'Harmonize_win.py',
				  'dest_base':'Harmonize'}],
		scripts=r_scripts,
		data_files=['Python.Runtime.dll', 'folder.bmp', 'hd.bmp', 'cd.bmp']
	)
