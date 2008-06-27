import os, re, hashlib, httplib, sys, time, urllib
import os.path as path
from thread import start_new_thread
import config, rate_limit, fb, db
from db import is_file_uploaded, is_sha_uploaded, set_file_uploaded
from hfile import HFile
from httplib import HTTPConnection
from Queue import Queue

actionq = Queue()
actions = set(['login_complete', 'options_changed'])
def get_action():
	action = actionq.get()
	if action not in actions:
		raise Exception('Unknown action added: %s' % action)
	return action

def login_callback(session_key=None):
	actionq.put('login_complete')

def options_changed():
	actionq.put('options_changed')

def empty_actions():
	while not actionq.empty():
		actionq.get()

class Callback(object):
	def __init__(self, base_callback):
		self.base = base_callback

	def __getattr__(self, name):
		if hasattr(self.base.a, name):
			def wrapper(*args):
				fn = getattr(self.base.a, name)
				self.base.do_action(fn, args)
			return wrapper
		else: raise ValueError, name

	def error(self, msg):
		base = self.base
		base.add_action(base.a.set_msg, (msg,))
		base.add_action(base.a.set_progress, (True,))
		base.complete_actions()

	def start_reauth(self, msg):
		self.set_msg(msg)
		self.set_progress(True)
		self.loginEnabled(True)

	def end_reauth(self, msg):
		self.set_msg(msg)
		self.loginEnabled(False)

	def start_auth(self):
		if db.get_upload_src() == 'itunes':
			msg = 'Click Login to start uploading your iTunes library'
		else:
			msg = 'Click Login to start uploading your music'
		self.set_msg(msg)
		self.loginEnabled(True)

	def end_auth(self):
		self.loginEnabled(False)

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

def start_uploader(base_callback):
	callback = Callback(base_callback)

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
		callback.set_msg('Uploading file:\n%s' % hfile.ppname)
		callback.set_progress(False, 0.0)

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

	callback.init()
	callback.set_totalUploaded(db.total_uploaded_tracks())

	while True:
		callback.loginEnabled(False)
		callback.optionsEnabled(True)
		callback.set_msg('Searching for music...')

		song_list = db.get_tracks()
		if song_list == None:
			callback.set_msg('No music found!\nClick Options to add some')
			while get_action() != 'options_changed': pass
			callback.activate()
			continue
		elif song_list == []:
			callback.set_msg('No new music to upload...')
			#time.sleep(300)
			time.sleep(10)
			continue

		if not fb.get_session_key():
			callback.start_auth()
			action = get_action()
			if action == 'options_changed':
				callback.activate()
				continue
			elif action != 'login_complete':
				raise Exception('Unknown action received')
			callback.end_auth()
		
		#Start uploading process
		total_tracks = float(len(song_list))
		tracks_analyzed = 0
		callback.set_msg('Analyzing library...')
		callback.set_progress(False, 0.0)
		callback.optionsEnabled(False)

		upload_list = [] #a list of hfiles
		for song in song_list:
			hfile = HFile(song)
			try:
				if not hfile.contents: 
					callback.inc_skipped()
					db.add_skipped(hfile.name)
					continue
			except IOError:
				callback.inc_skipped()
				db.add_skipped(hfile.name)
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
		time.sleep(30)

def get_conn():
	return HTTPConnection(
			config.current['server_addr'], config.current['server_port'])

def get_url(base_url):
	if '?' not in base_url:
		return base_url + '?session_key=' + fb.get_session_key()
	else:
		return base_url + '&session_key=' + fb.get_session_key()
