import os, re, hashlib, httplib
import os.path as path
from thread import start_new_thread

#UPLOAD_PATH = '/Users/justin/Music/Feist'

def update_actions(actions):
	actions['uploads_remaining'] = uploads_remaining
	actions['begin_upload'] = begin_upload
	actions['upload_itunes'] = upload_itunes

def get_default_path():
	paths = {'posix':os.getenv('HOME'),
		'nt':r'C:\\',
		'mac':path.join(os.getenv('HOME'), 'Music')}
	
	return paths[os.name]

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
	return re.match(r'.*\.mp3$', file) != None

def upload_file(file, session_key):
	file_contents = open(file).read()
	file_sha = hashlib.sha1(file_contents).hexdigest()

	connection = httplib.HTTPConnection('127.0.0.1', 2985)
	url = '/uploads/' + file_sha + '?session_key=' + session_key
	connection.request('GET', url)

	if connection.getresponse().read() == '0':
		connection.request('POST', url, file_contents, 
			{'Content-Type':'audio/x-mpeg-3'})

def upload_files(song_list, session_key):
	global songs_left
	for song in song_list:
		upload_file(song, session_key)
		songs_left -= 1
	
	songs_left = 0

def create_song_list(file_path, session_key):
	global songs_left
	#song_list = get_music_files(UPLOAD_PATH)
	song_list = get_music_files(file_path)
	songs_left = len(song_list)
	start_new_thread(upload_files, (song_list, session_key))

def begin_upload(c):
	if not hasattr(c, 'session_key'):
		return 'Error: you must be logged into facebook to upload songs!'

	connection.close()

#A global representing the songs remaining to be uploaded
songs_left = None

def upload_files(song_list, session_key):
	global songs_left
	for song in song_list:
		upload_file(song, session_key)
		songs_left -= 1
	
	songs_left = 0

def create_song_list(file_path, session_key):
	global songs_left
	#song_list = get_music_files(UPLOAD_PATH)
	song_list = get_music_files(file_path)
	songs_left = len(song_list)
	upload_files(song_list, session_key)
	#start_new_thread(upload_files, (song_list, session_key))

def upload_itunes_library(itunes, session_key):
	global songs_left
	file_path = itunes.get_library_file()
	if file_path:
		library = itunes.ITunes(file_path)
		song_list = library.get_all_track_filenames()
		songs_left = len(song_list)
		upload_files(song_list, session_key)

def begin_upload(c):
	if not hasattr(c, 'session_key'):
		return 'Error: you must be logged into facebook to upload songs!'

	global songs_left
	if songs_left == None:
		songs_left = 'Finding music...'
		start_new_thread(create_song_list, (c.query['path'][0], c.session_key))

	return 'Finding music...'
	
def uploads_remaining(c):
	if songs_left != None:
		return str(songs_left)
	else: return 'Error: uploading has not begun'

def upload_itunes(c):
	start_new_thread(upload_itunes_library, (c.itunes, c.session_key))
	return "Finding music..."
