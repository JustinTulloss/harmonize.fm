import sys, os, re
from distutils.core import setup
from mako.template import Template
from popen2 import popen2

r_scripts = ['fb.py', 'dir_browser.py', 'upload.py', 'itunes.py', 'tags.py', 
			 'config.py', 'genpuid.py', 'db.py', 'hplatform.py', 'hfile.py',
			 'singleton.py', 'excepthandler.py', 'build.py', 'guimanager.py']

def get_repo_version():
	stdout, stdin = popen2('hg identify')
	stdin.close()
	match = re.match('^[a-fA-F0-9]+', stdout.read())
	if not match:
		raise Exception('Unable to determine build version')
	return match.group(0)

excepthandler_py = open('excepthandler.py', 'w+')
excepthandler_py.write(
	Template(filename='excepthandler.mako.py').\
	render(repo_version=get_repo_version()))
excepthandler_py.close()

if sys.platform == 'darwin':
	if not os.path.exists('genpuid'):
		print 'genpuid directory missing, download it at musicip.com'
		sys.exit(1)

	main_py = open('main.py', 'w+')
	main_py.write(
		Template(filename='main.mako.py').render(window_file='Harmonize_osx'))
	main_py.close()

	app = ['main.py']
	scripts = r_scripts + \
				['Harmonize_osx.py', 'osx_options.py', 'osx_upload.py']
	if len(sys.argv) == 4 and sys.argv[3] == 'test':
		app = ['test_win_upload.py']
		scripts = ['Harmonize_osx.py', 'osx_options.py', 'osx_upload.py']

	if len(sys.argv) == 1 or sys.argv[1] != 'py2app':
		sys.exit(0)

	import py2app
	setup(
		name='Harmonizer',
		setup_requires=['py2app'],		
		app=app,
		scripts=scripts,
		data_files=['MainMenu.nib', 'desktop_icon.icns',
					'genpuid/genpuid', 'genpuid/AACTagReader',
					'genpuid/mipcore'],
		options=dict(py2app=dict(plist=dict(
			LSUIElement=True,
			CFBundleIconFile='desktop_icon.icns')))
	)
elif sys.platform == 'win32':
	main_py = open('main.py', 'w+')
	main_py.write(
		Template(filename='main.mako.py').render(window_file='Harmonize_win'))
	main_py.close()

	if len(sys.argv) == 1 or sys.argv[1] != 'py2exe':
		sys.exit(0)

	import py2exe
	setup(
		windows=[{'script':'main.py',
				  'dest_base':'Harmonize'}],
		scripts=r_scripts + \
				['Harmonize_win.py', 'win_options.py', 'win_upload.py'],
		data_files=['Python.Runtime.dll', 'harmonize_icon.ico',
					'folder.bmp', 'hd.bmp', 'cd.bmp',
					'genpuid\\genpuid.exe', 'genpuid\\AACTagReader.exe',
					'genpuid\\mipcore.exe', 'genpuid\\libexpat.dll']
	)
