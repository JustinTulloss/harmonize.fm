import os, re, hashlib, httplib, sys, time, urllib
import os.path as path
from thread import start_new_thread
import config, rate_limit, fb, db
from db import is_file_uploaded, is_sha_uploaded
from hfile import HFile
from httplib import HTTPConnection
from decorator import decorator

class RetryException(Exception):
	pass

class WaitException(Exception):
	pass

class ReauthenticateException(Exception):
	pass

response_switch = {
	'retry': RetryException,
	'wait': WaitException,
	'reauthenticate': ReauthenticateException
}

def check_response(response):
	response_body = response.read()

	if response.status != 200:
		raise Exception('Server returned status code %s!' % response.status)
	elif response_switch.has_key(response_body):
		raise response_switch[response_body]
	return response_body

def upload_files(song_list, callback):
	def reauthenticate():
		callback.error("facebook login expired, please log in again")
		fb.synchronous_login()
		callback.error("Login complete, uploading will resume shortly")

	def retry_fn(fn):
		def default_action():
			if config.current['debug']:
				import pdb; pdb.set_trace()
			callback.error('Error connecting to server, \nWill try again')

		def wrapper(*args, **kws):
			while True:
				try:
					return fn(*args, **kws)
				except WaitException, e:
					default_action()
					time.sleep(120)
				except RetryException, e:
					default_action()
				except ReauthenticateException, e:
					reauthenticate()
				except Exception, e:
					default_action()
					time.sleep(20)
		return wrapper
	
	@retry_fn
	def start_rate_limit():
		rate_limit.establish_baseline(config.current['server_addr'],
										config.current['server_port'])

	@retry_fn
	def is_puid_uploaded(hfile):
		conn = get_conn()
		body = urllib.urlencode(hfile.tags)
		headers = {'Content-type': 'application/x-www-form-urlencoded'}
		url = get_url('/upload/tags')
		conn.request('POST', url, body, headers)
		response =  check_response(conn.getresponse())
		if response == 'done':
			return True
		else: return False

	@retry_fn
	def upload_file(hfile):
		url = get_url('/upload/file/' + hfile.sha)
		conn = get_conn()
		if hfile.puid:
			url += '&puid=' + hfile.puid
		if config.current['rate_limit']:
			response = rate_limit.post(conn, url, hfile.contents)
		else:
			conn.request('POST', url, hfile.contents, 
							{'Content-Type':'audio/x-mpeg-3'})
			response = conn.getresponse()
		check_response(response)

	upload_list = [] #a list of hfiles
	for song in song_list:
		hfile = HFile(song)
		try:
			if not hfile.contents: continue
		except IOError:
			#Todo: add error indicator to uploader
			continue

		if is_file_uploaded(hfile.name) or is_sha_uploaded(hfile.sha):
			continue
		elif hfile.puid:
			if not is_puid_uploaded(hfile):
				upload_list.append(hfile)
		else:
			upload_list.append(hfile)

	songs_left = len(upload_list)
	callback.init('%s songs remaining' % songs_left, songs_left)
	for hfile in upload_list:
		upload_file(hfile)
		songs_left -= 1
		callback.update('%s songs remaining' % songs_left, songs_left)

		if songs_left % 15 == 0:
			pass
		#	retry_fn(reset_rate_limit, callback)
	
	callback.update('Upload complete!', 0)

def get_conn():
	return HTTPConnection(
			config.current['server_addr'], config.current['server_port'])

def get_url(base_url):
	if '?' not in base_url:
		return base_url + '?session_key=' + fb.get_session_key()
	else:
		return base_url + '&session_key=' + fb.get_session_key()
