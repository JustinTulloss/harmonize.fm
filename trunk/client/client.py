import os.path as path
import time, webbrowser, cgi
import upload
from urlparse import urlsplit
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from mako.template import Template

class ClientHTTPServer(BaseHTTPRequestHandler):
	base_dir = 'public'

	def not_found_path(self):
		return path.join(self.base_dir, '404.html')

	def render_file(self, request_path):
		#base_dir = 'public'
		file_path = path.join(self.base_dir, request_path)

		if path.isdir(file_path):
			file_path = path.join(file_path, 'index.html')

		if path.exists(file_path):
			requested_file = open(file_path)
			return Template(requested_file.read()).render(c=c_global)
		else:
			return None
		
	def render_mapping(self, request_path):
		global action_mappings
		
		if action_mappings.has_key(request_path):
			return action_mappings[request_path](c_global)
		else:
			return None

	def redirect(self, url):
		print 'Redirecting to: ', url
		self.send_response(307)
		self.send_header('Location', url)
		self.end_headers()

	def handle_request(self):
		#split path into components, take the path, strip leading /
		split_url = urlsplit(self.path)
		request_path = split_url.path[1:]
		
		#parse the query string
		c_global.query = cgi.parse_qs(split_url.query)

		response = self.render_file(request_path)
		if response == None:
			response = self.render_mapping(request_path)
		
		if response == None:
			self.send_response(404)
			not_found_response = open(self.not_found_path()).read()
			response = Template(not_found_response).render(c=c_global)
		else:
			if type(response) == Redirect: #Special case for redirect
				self.redirect(response.url)
				return
			else: self.send_response(200)

		if type(response) != str:
			print 'Error: response is not string!'
	
		self.end_headers()
		self.wfile.write(response)
		
	def do_GET(self):
		c_global.request_body = None
		self.handle_request()
	
	def do_POST(self):
		if self.headers.has_key('Content-Length'):
			length = int(self.headers['Content-Length'])
			print 'Content-Length: ' + self.headers['Content-Length']
			c_global.request_body = self.rfile.read(length)
		self.handle_request()

def complete_login(c):
	c.session_key = c.query['session_key'][0]
	return Redirect('index.html')

action_mappings = {'upload_all':upload.upload_all, 
	'complete_login':complete_login}

class Global(object):
	pass
c_global = Global() #This is all the important state for the templates

class Redirect(object):
	def __init__(self, url):
		self.url = url

if __name__ == '__main__':
	server = HTTPServer(('localhost', 8080), ClientHTTPServer)
	webbrowser.open('http://localhost:8080/login.html')
	server.serve_forever()
