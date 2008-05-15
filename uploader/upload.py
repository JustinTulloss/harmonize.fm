import os, re, hashlib, httplib, sys, platform, time
import os.path as path
from thread import start_new_thread
import config, tags, rate_limit, fb

def get_default_path():
	def default_osx():
		home_dir = os.getenv('HOME')
		music_dir = path.join(home_dir, 'Music')
		if path.exists(music_dir):
			return music_dir
		else: return home_dir

	def default_win():
		home_path = os.getenv('USERPROFILE')
		xp_music_path = path.join(home_path, 'My Documents', 'My Music')
		vista_music_path = path.join(home_path, 'Documents', 'Music')
		if path.exists(xp_music_path):
			return xp_music_path
		elif path.exists(vista_music_path):
			return vista_music_path
		else:
			return home_path
			
	#Have to wrap paths in lambda's so they don't get executed on windows
	paths = {'Linux':(lambda: os.getenv('HOME')),
		'Windows':default_win,
		'Darwin':default_osx}
	
	return paths[platform.system()]()

def get_music_files(dir):
	music_files = []
	
	for root, dirs, files in os.walk(dir):
		for file in files:
			if is_music_file(file):
				#trying to catch the special case in Ubuntu where $HOME/Network
				#maps to every network share. You can still upload that dir if
				#you select it explicitly, but it won't descend automatically.
				if not(root == os.getenv('HOME') and file == 'Network' 
					   and os.name == 'posix'):
					music_files.append(os.path.join(root, file))
	
	return music_files

def is_music_file(file):
	return file.endswith('.mp3')

def reauthenticate(callback_obj):
	callback_obj.error("facebook login expired, please log in again")
	fb.synchronous_login()
	callback_obj.error("Login complete, uploading will resume shortly")

def upload_file(filename, callback):
	try:
		file_contents = open(filename, 'rb').read()
		if file_contents == '': return
		contents_wo_tags = tags.file_contents_without_tags(filename)
		if contents_wo_tags == '': return
	except IOError, e:
		#sys.stderr.write('Unable to read file %s, skipping.\n' % filename)
		return

	file_sha = hashlib.sha1(contents_wo_tags).hexdigest()

	uploaded = False
	while not uploaded:
		try:
			connection = httplib.HTTPConnection(config.current['server_addr'],
				config.current['server_port'])
			url = '/uploads/' + file_sha + '?session_key='+fb.get_session_key()
			connection.request('GET', url)

			response = connection.getresponse().read()

			if response == 'upload_file':
				connection.request('POST', url, file_contents, 
					{'Content-Type':'audio/x-mpeg-3'})
				response = connection.getresponse().read()
				
				if response == 'reauthenticate':
					reauthenticate(callback)
					#Going to retry request
				elif response == 'retry':
					pass #This will just retry
				else:
					uploaded = True
			elif response == 'reauthenticate':
				reauthenticate(callback)
			else:
				#Should be file_uploaded, but if it's not just keep on truckin
				uploaded = True 
		except Exception, e:
			if config.current['debug']:
				import pdb; pdb.set_trace()
			callback.error('Error connecting to server, \nWill try again')
			time.sleep(20) #This is a little safer than inside the exception

def upload_files(song_list, callback):
	songs_left = len(song_list)	
	callback.init('%s songs remaining' % songs_left, songs_left)

	#Initialize rate limiting algorithm
	def start_rate_limit():
		rate_limit.establish_baseline(config.current['server_addr'],
									  config.current['server_port'])
	retry_fn(start_rate_limit, callback)

	def reset_rate_limit():
		rate_limit.reestablish_baseline(config.current['server_addr'],
										config.current['server_port'])

	for song in song_list:
		upload_file(song, callback)
		songs_left -= 1
		callback.update('%s songs remaining' % songs_left, songs_left)

		if songs_left % 15 == 0:
			retry_fn(reset_rate_limit, callback)
	
	callback.update('Upload complete!', 0)

def retry_fn(fn, callback):
	success = False
	while not success:
		try:
			res = fn()
			success = True
		except Exception, e:
			if config.current['debug']:
				import pdb; pdb.set_trace()
			callback.error('Error connecting to server, \nWill try again')
			time.sleep(20)
	return res
