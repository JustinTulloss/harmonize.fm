import os
import os.path as path
import re
import hashlib
import httplib
import time
from urlparse import urlparse

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import webbrowser
from mako.template import Template

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
	connection.request('POST', url, file_contents)

	connection.close()

class ClientHTTPServer(BaseHTTPRequestHandler):
	def do_GET(self):
		self.path = urlparse(self.path)[2]
		base_dir = 'public'
		if self.path == '/':
			file_path = base_dir
		else:
			#need to remove the front / in self.path
			file_path = path.join(base_dir, self.path[1:])

		if path.isdir(file_path):
			file_path = path.join(file_path, 'index.html')

		print 'file_path: ' + file_path
			
		if path.exists(file_path):
			self.send_response(200)
			self.end_headers()
			
			requested_file = open(file_path)
			response = Template(requested_file.read()).render()
			self.wfile.write(response)
		else:
			self.send_response(404)
			self.end_headers()
	
	def do_POST(self):
		self.path = urlparse(self.path)[2]
		self.path = self.path[1:] #strip leading /
		if action_mappings.has_key(self.path):
			response = action_mappings[self.path]()
			self.send_response(200)
			self.end_headers()
			self.wfile.write(response)
		else:
			self.send_response(404)
			self.end_headers()

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
def upload_all():
	global upload_gen
	if upload_gen == None:
		song_list = get_music_files('/media/sda1/MyMusic/Air/Talkie Walkie/')
		upload_gen = upload_generator(song_list)
	
	songs_left = upload_gen.next()
	
	//time.sleep(3)

	if songs_left == 0:
		return 'Upload Complete.'
	else:
		return '%s songs remaining...' % songs_left

action_mappings = {'upload_all':upload_all}

if __name__ == '__main__':
	server = HTTPServer(('localhost', 8080), ClientHTTPServer)
	webbrowser.open('http://localhost:8080')
	server.serve_forever()
