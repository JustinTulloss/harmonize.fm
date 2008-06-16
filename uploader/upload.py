import os, re, hashlib, httplib, sys, time, urllib
import os.path as path
from thread import start_new_thread
import config, tags, rate_limit, fb, genpuid
#some imports at end of file

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
	return file.endswith('.mp3') or file.endswith('.m4a')

def reauthenticate(callback_obj):
	callback_obj.error("facebook login expired, please log in again")
	fb.synchronous_login()
	callback_obj.error("Login complete, uploading will resume shortly")

def upload_file(filename, callback):
	try:
		file_contents = open(filename, 'rb').read()
		if file_contents == '': return
		file_sha = hashlib.sha1(file_contents).hexdigest()
		if db.is_sha_uploaded(file_sha):
			return
		puid = genpuid.gen(filename)
	except IOError, e:
		if config.current['debug']:
			sys.stderr.write('Unable to read file %s, skipping.\n' % filename)
		return

	uploaded = False
	while not uploaded:
		try:
			connection = httplib.HTTPConnection(
					config.current['server_addr'],
					config.current['server_port'])
			if puid:
				song_tags = tags.get_tags(filename, puid)
				body = urllib.urlencode(song_tags)
				headers = {"Content-type": "application/x-www-form-urlencoded"}
				puid_url = '/upload/tags'+'?session_key='+fb.get_session_key()
				connection.request('POST', puid_url, body, headers)

				response = connection.getresponse().read()
			else:
				response = 'upload'

			if response == 'upload':
				upload_url = '/upload/file/'+file_sha + \
								'?session_key='+fb.get_session_key()+\
                                '&puid='+puid
				if config.current['rate_limit']:
					response = \
						rate_limit.post(connection, upload_url, file_contents).read()
				else:
					connection.request('POST', upload_url, file_contents, 
										{'Content-type':'audio/x-mpeg-3'})
					response = connection.getresponse().read()
				
				if response == 'reauthenticate':
					reauthenticate(callback)
					#Going to retry request
				elif response == 'retry':
					pass #This will just retry
				elif response =='wait':
					time.sleep(60)
				elif response == 'done':
					db.set_file_uploaded(filename, sha=file_sha)
					uploaded = True
				else:
					raise Exception('Unknown response from server received')
			elif response == 'reauthenticate':
				reauthenticate(callback)
			elif response == 'wait':
				time.sleep(60)
			elif response == 'done':
				db.set_file_uploaded(filename, puid, file_sha)
				uploaded = True 
			else:
				raise Exception('Unknown response from server received')
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
			pass
		#	retry_fn(reset_rate_limit, callback)
	
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

import db
