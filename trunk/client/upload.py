import os, re, hashlib, httplib
import os.path as path
from thread import start_new_thread

UPLOAD_PATH = '/Users/justin/Music/Feist'

def get_music_files(dir):
	music_files = []
	
	for root, dirs, files in os.walk(dir):
		for file in files:
			if is_music_file(file):
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

	connection.close()

#A global representing the songs remaining to be uploaded
songs_left = None

def upload_files(song_list, session_key):
	global songs_left
	for song in song_list:
		upload_file(song, session_key)
		songs_left -= 1
	
	songs_left = 0

#Ideally, should be returning just songs remaining, and uploading should happen
#in another thread, so that uploading happends even if browser is closed
def upload_all(c):
	if not hasattr(c, 'session_key'):
		return 'Error: not logged into Facebook!'

	global songs_left
	if songs_left == None:
		song_list = get_music_files(UPLOAD_PATH)
		songs_left = len(song_list)
		start_new_thread(upload_files, (song_list, c.session_key))
		return str(songs_left)
	else: return str(songs_left)
