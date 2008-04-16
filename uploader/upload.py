import os, re, hashlib, httplib, sys
import os.path as path
from thread import start_new_thread
import time
import config, tags
import fb

def get_default_path():
	#Have to wrap paths in lambda's so they don't get executed on windows
	paths = {'posix':(lambda: os.getenv('HOME')),
		'nt':(lambda: os.getenv('USERPROFILE')),
		'mac':(lambda: path.join(os.getenv('HOME'), 'Music'))}
	
	return paths[os.name]()

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
	callback_obj.error("facebook login expired\n\n"
							+"Please log in again")
	fb.synchronous_login()
	callback_obj.error("Login complete, uploading will resume shortly")

def upload_file(filename, callback):
	try:
		file_contents = open(filename, 'rb').read()
		contents_wo_tags = tags.file_contents_without_tags(filename)
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
			callback.error('Error connecting to server, will try again')
			time.sleep(60) #This is a little safer than inside the exception

def upload_files(song_list, callback):
	songs_left = len(song_list)	
	callback.init('%s songs remaining' % songs_left, songs_left)

	for song in song_list:
		upload_file(song, callback)
		songs_left -= 1
		callback.update('%s songs remaining' % songs_left, songs_left)
	
	callback.update('Upload complete!', 0)
