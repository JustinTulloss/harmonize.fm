import os.path as path
import time, webbrowser, cgi
import facebook, upload
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

	def handle_request(self):
		#split path into components, take the path, strip leading /
		split_url = urlsplit(self.path)
		request_path = split_url.path[1:]
		
		#parse the query string
		c_globals.query = parse_qs(split_url.query)

		response = self.render_file(request_path)
		if response == None:
			response = self.render_mapping(request_path)
		
		if response == None:
			self.send_response(404)
			not_found_response = open(self.not_found_path()).read()
			response = Template(not_found_response).render(c=c_global)
		else:
			self.send_response(200)

		self.end_headers()
		self.wfile.write(response)
		
	def do_GET(self):
		c_global.request_body = None
		self.handle_request()
	
	def do_POST(self):
		c_global.request_body = self.rfile.read()
		self.handle_request()

action_mappings = {'upload_all':upload.upload_all}

class Global():
	pass
c_global = Global() #This is all the important state for the templates
c_global.facebook = facebook

if __name__ == '__main__':
	server = HTTPServer(('localhost', 8080), ClientHTTPServer)
	webbrowser.open('http://localhost:8080/login.html')
	server.serve_forever()
