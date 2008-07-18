import os, re, hashlib, httplib, sys, time, urllib, simplejson
import os.path as path
import config, rate_limit, fb
from db import db
from config import get_conn
from Queue import Queue, Empty
from excepthandler import exception_managed, get_tb
from hfile import HFile, HFileException

actionq = Queue()
actions = set(['login_complete', 'options_changed'])
def get_action(timeout=None):
	try:
		action = actionq.get(True, timeout)
		if action not in actions:
			raise Exception('Unknown action added: %s' % action)
		return action
	except Empty:
		return None

def login_callback(session_key=None):
	actionq.put('login_complete')

def options_changed():
	actionq.put('options_changed')

def empty_actions():
	while not actionq.empty():
		actionq.get()

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
		raise Exception(
			'Server returned status code %s %s!' % 
			(response.status, response.reason))
	elif response_switch.has_key(response_body):
		raise response_switch[response_body]
	return response_body

def tag_upload(tags):
	if tags == []: return

	json = simplejson.dumps(tags)
	url = get_url('/upload/tags')
	params = {
		'version': tags[0]['version'],
		'tags': json
	}
	body = urllib.urlencode(params)
	headers = {'Content-type': 'application/x-www-form-urlencoded'}
	conn = get_conn()
	conn.request('POST', url, body, headers)
	return simplejson.loads(check_response(conn.getresponse()))

def is_puid_uploaded(hfile):
	conn = get_conn()
	body = urllib.urlencode(hfile.puid_tags)
	headers = {'Content-type': 'application/x-www-form-urlencoded'}
	url = get_url('/upload/tags')
	conn.request('POST', url, body, headers)
	response =  check_response(conn.getresponse())
	if response == 'done':
		hfile.uploaded = True
		return True
	else: return False
		

@exception_managed
def start_uploader(guimgr):
	listen_enabled = False

	while True:
		guimgr.start_search()

		song_list = db.get_tracks()
		if song_list == None:
			guimgr.no_music_found()
			while get_action() != 'options_changed': pass
			guimgr.activate()
			continue
		elif song_list == []:
			guimgr.no_new_music()
			get_action(300)
			continue

		if not fb.get_session_key():
			guimgr.start_auth(db.upload_src)
			action = get_action()
			if action == 'options_changed':
				guimgr.activate()
				continue
			elif action != 'login_complete':
				raise Exception('Unknown action received')
			guimgr.end_auth()
		
		upload_files(song_list, guimgr)
		get_action(30)


def upload_files(song_list, guimgr):
	def retry_fn(fn):
		def default_action():
			if config.current['debug']:
				contents = get_tb()
				import pdb; pdb.set_trace()
			guimgr.conn_error()

		def reauthenticate():
			guimgr.start_reauth()
			fb.synchronous_login()
			guimgr.end_reauth()

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
		rate_limit.establish_baseline(
				config.current['server_addr'], config.current['server_port'])

	r_is_puid_uploaded = retry_fn(is_puid_uploaded)

	@retry_fn
	def upload_file(hfile):
		contents = hfile.contents

		guimgr.start_upload(hfile.ppname, len(contents))

		url = get_url('/upload/file/' + hfile.sha)
		conn = get_conn()
		if hfile.puid:
			url += '&puid=' + hfile.puid
		if config.current['rate_limit']:
			response = rate_limit.post(conn, url, contents, 
										guimgr.upload_progress)
		else:
			conn.request('POST', url, contents, 
							{'Content-Type':'audio/x-mpeg-3'})
			response = conn.getresponse()
		check_response(response)
		hfile.uploaded = True

	r_tag_upload = retry_fn(tag_upload)

	guimgr.start_analysis(float(len(song_list)*2))

	puid_list = []
	while song_list != []:
		song_chunk = song_list[:10]
		song_list = song_list[10:]

		new_hfiles = []
		mass_upload = []
		for song in song_chunk:
			hfile = HFile(song)
			try:
				hfile.contents

				if not hfile.uploaded:
					mass_upload.append(hfile.tags)
					new_hfiles.append(hfile)
				else:
					#If file is uploaded it won't be analyzed later, gotta keep
					#count accurate
					guimgr.file_analyzed()

				guimgr.file_analyzed()
			except HFileException, e:
				guimgr.file_skipped()
				db.add_skipped(hfile.name)
				continue

		if mass_upload == []:
			continue

		responses = r_tag_upload(mass_upload)

		auto_uploaded = 0
		db.start_trans()

		for response in responses:
			hfile = new_hfiles.pop(0)
			if response == 'done':
				hfile.uploaded = True
				auto_uploaded += 1
				continue
			puid_list.append(hfile)

		db.end_trans()
		guimgr.file_auto_uploaded(auto_uploaded)
		guimgr.file_analyzed(auto_uploaded)
			
	upload_list = [] #a list of hfiles
	for hfile in puid_list:
		try:
			if hfile.puid:
				if not r_is_puid_uploaded(hfile):
					upload_list.append(hfile)
					guimgr.file_queued()
				else:
					guimgr.file_auto_uploaded()
			else:
				upload_list.append(hfile)
				guimgr.file_queued()

			guimgr.file_analyzed()
		except HFileException, e:
			guimgr.file_skipped()
			db.add_skipped(hfile.name)
			continue

	songs_left = len(upload_list)

	start_rate_limit()

	for hfile in upload_list:
		try:
			upload_file(hfile)
			songs_left -= 1

			guimgr.file_uploaded()
		except HFileException, e:
			guimgr.file_skipped()
			db.add_skipped(hfile.name)
			continue

		'''
		if songs_left % 15 == 0:
			retry_fn(reset_rate_limit, callback)
		'''
	
	guimgr.upload_complete()

def get_url(base_url):
	if '?' not in base_url:
		return base_url + '?session_key=' + fb.get_session_key()
	else:
		return base_url + '&session_key=' + fb.get_session_key()
