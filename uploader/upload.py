import os, re, hashlib, httplib, sys
import os.path as path
from thread import start_new_thread
import time

#UPLOAD_PATH = '/Users/justin/Music/Feist'

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

def upload_file(file, session_key):
	try:
		fd = open(file)
		file_contents = fd.read()
		fd.close()
	except IOError, e:
		#sys.stderr.write('Unable to read file %s, skipping.\n' % file)
		return

	file_sha = hashlib.sha1(file_contents).hexdigest()

	connection = httplib.HTTPConnection('127.0.0.1', 2985)
	url = '/uploads/' + file_sha + '?session_key=' + session_key
	connection.request('GET', url)

	if connection.getresponse().read() == '0':
		connection.request('POST', url, file_contents, 
			{'Content-Type':'audio/x-mpeg-3'})
		connection.getresponse().read()

def upload_files(song_list, session_key, callback):
	songs_left = len(song_list)	
	callback(songs_left)

	for song in song_list:
		upload_file(song, session_key)
		songs_left -= 1
		callback(songs_left)
	
	callback(0)
