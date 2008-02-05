import os, re, hashlib, httplib, simplejson
import os.path as path
from thread import start_new_thread

#UPLOAD_PATH = '/Users/justin/Music/Feist'

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
		#song_list = get_music_files(UPLOAD_PATH)
		song_list = get_music_files(c.query['path'][0])
		songs_left = len(song_list)
		start_new_thread(upload_files, (song_list, c.session_key))
		return str(songs_left)
	else: return str(songs_left)

def contains_dir(dir_path):
	return [dir for dir in os.listdir(dir_path) if path.isdir(path.join(dir_path, dir))] != []

def get_dir_listing(c):
	request_dir = c.post_query['node'][0]
	new_dirs = [dir for dir in os.listdir(request_dir) if path.isdir(path.join(request_dir, dir))]

	node_list = []
	for dir in new_dirs:
		dir_path = path.join(request_dir, dir)
		new_node = {}
		new_node['text'] = dir
		new_node['id'] = dir_path
		if not contains_dir(dir_path):
			new_node['leaf'] = True
		node_list.append(new_node)

	return simplejson.dumps(node_list)
