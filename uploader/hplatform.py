import os, platform
import os.path as path

def get_default_path():
	def default_osx():
		home_dir = os.getenv('HOME')
		music_dir = path.join(home_dir, 'Music')
		if path.exists(music_dir):
			return music_dir
		else: return home_dir

	def default_win():
		home_path = os.getenv('USERPROFILE')
		if platform.uname()[3].startswith('6'):
			music_path = path.join(home_path, 'Music')
		else:
			music_path = path.join(home_path, 'My Documents', 'My Music')

		if path.exists(music_path):
			return music_path
		else:
			return home_path
			
	#Have to wrap paths in lambda's so they don't get executed on windows
	paths = {'Linux':(lambda: os.getenv('HOME')),
		'Windows':default_win,
		'Microsoft':default_win,
		'Darwin':default_osx}
	
	return paths[platform.system()]()

def get_db_path():
	if platform.system() == 'Darwin':
		return os.path.join(os.getenv('HOME'), '.harmonize')
	else:
		return os.path.join(os.getenv('USERPROFILE'), '_harmonize')

def get_genpuid_path():
	if platform.system() == 'Darwin':
		return './genpuid'
	else:
		return '.\\genpuid'
