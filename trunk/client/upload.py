import os, re, hashlib

def get_music_files(dir):
	music_files = []
	
	for root, dirs, files in os.walk(dir):
		for file in files:
			if is_music_file(file):
				music_files.append(path.join(root, file))
	
	return music_files

def is_music_file(file):
	return re.match(r'.*\.mp3$', file) != None

def upload_file(file):
	file_contents = open(file).read()
	file_sha = hashlib.sha1(file_contents).hexdigest()

	connection = httplib.HTTPConnection('127.0.0.1', 2985)
	url = '/uploads/' + file_sha
	connection.request('GET', url)

	if connection.getresponse.read() == '0':
		connection.request('POST', url, file_contents)

	connection.close()

upload_gen = None

def upload_generator(song_list):
	songs_left = len(song_list)

	for song in song_list:
		yield songs_left
		upload_file(song)
		songs_left -= 1
	
	while True:
		yield 0

#Ideally, should be returning just songs remaining, and uploading should happen
#in another thread, so that uploading happends even if browser is closed
def upload_all(c):
	global upload_gen
	if upload_gen == None:
		song_list = get_music_files('/media/sda1/MyMusic/Air/Talkie Walkie/')
		upload_gen = upload_generator(song_list)
	
	songs_left = upload_gen.next()
	
	#time.sleep(3)

	if songs_left == 0:
		return 'Upload Complete.'
	else:
		return '%s songs remaining...' % songs_left

