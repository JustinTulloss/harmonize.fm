import sys
from distutils.core import setup
import os

r_scripts = ['fb.py', 'dir_browser.py', 'upload.py', 'itunes.py', 'tags.py', 
			 'config.py', 'genpuid.py', 'db.py', 'hplatform.py']

if sys.platform == 'darwin':
	if not os.path.exists('genpuid'):
		print 'genpuid directory missing, download it at musicip.com'
		sys.exit(1)
	import py2app
	setup(
		name='Harmonize',
		setup_requires=['py2app'],		
		app=['Harmonize_osx.py'],
		scripts=r_scripts + ['osx_options.py'],
		data_files=['MainMenu.nib', 
					'genpuid/genpuid', 'genpuid/AACTagReader',
					'genpuid/mipcore']
	)
elif sys.platform == 'win32':
	import py2exe
	setup(
		windows=[{'script':'Harmonize_win.py',
				  'dest_base':'Harmonize'}],
		scripts=r_scripts,
		data_files=['Python.Runtime.dll', 'folder.bmp', 'hd.bmp', 'cd.bmp',
					'genpuid\\genpuid.exe', 'genpuid\\AACTagReader.exe',
					'genpuid\\mipcore.exe', 'genpuid\\libexpat.dll']
	)
