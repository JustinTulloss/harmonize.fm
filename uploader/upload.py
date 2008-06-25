import os, re, hashlib, httplib, sys, time, urllib
import os.path as path
from thread import start_new_thread
import config, rate_limit, fb, db
from db import is_file_uploaded, is_sha_uploaded, set_file_uploaded
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

def upload_files(callback):
	def reauthenticate():
		callback.start_reauth('You need to re-login to continue\nClick "Save my login" on login page to stay logged in')
		fb.synchronous_login()
		callback.end_reauth("Login complete, uploading will resume shortly")

	def retry_fn(fn):
		def default_action():
			if config.current['debug']:
				import pdb; pdb.set_trace()
			callback.error('Error connecting to server, \nWill retry in a moment')

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
			set_file_uploaded(hfile.name, hfile.puid, hfile.sha)
			return True
		else: return False

	@retry_fn
	def upload_file(hfile):
		callback.set_msg('Uploading file:\n%s - %s' % 
							(hfile.tags['title'], hfile.tags['artist']))

		url = get_url('/upload/file/' + hfile.sha)
		conn = get_conn()
		if hfile.puid:
			url += '&puid=' + hfile.puid
		if config.current['rate_limit']:
			response = rate_limit.post(conn, url, hfile.contents, callback)
		else:
			conn.request('POST', url, hfile.contents, 
							{'Content-Type':'audio/x-mpeg-3'})
			response = conn.getresponse()
		check_response(response)
		set_file_uploaded(hfile.name, hfile.puid, hfile.sha)

	callback.init_status('Finding music...')
	song_list = db.get_tracks()
	total_tracks = float(len(song_list))
	tracks_analyzed = 0
	callback.set_msg('Analyzing library...')
	callback.set_progress(False, 0.0)

	upload_list = [] #a list of hfiles
	for song in song_list:
		hfile = HFile(song)
		try:
			if not hfile.contents: 
				callback.inc_skipped()
				continue
		except IOError:
			callback.inc_skipped()
			continue

		if is_file_uploaded(hfile.name) or is_sha_uploaded(hfile.sha):
			continue
		elif hfile.puid:
			if not is_puid_uploaded(hfile):
				upload_list.append(hfile)
				callback.inc_remaining()
			else:
				callback.inc_totalUploaded()
		else:
			upload_list.append(hfile)
			callback.inc_remaining()

		tracks_analyzed += 1
		callback.set_progress(False, tracks_analyzed/total_tracks)

	songs_left = len(upload_list)

	start_rate_limit()

	for hfile in upload_list:
		upload_file(hfile)
		songs_left -= 1

		callback.dec_remaining()
		callback.inc_totalUploaded()

		'''
		if songs_left % 15 == 0:
			retry_fn(reset_rate_limit, callback)
		'''
	
	callback.set_msg('Upload complete!')

def get_conn():
	return HTTPConnection(
			config.current['server_addr'], config.current['server_port'])

def get_url(base_url):
	if '?' not in base_url:
		return base_url + '?session_key=' + fb.get_session_key()
	else:
		return base_url + '&session_key=' + fb.get_session_key()
