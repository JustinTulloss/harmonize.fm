import os.path as path
import os, time, webbrowser, cgi, imp
from urlparse import urlsplit
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from mako.template import Template
from response import Redirect

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
			root, ext = path.splitext(file_path)
			if ext == '.html':
				return Template(requested_file.read()).render(c=c_global)
			else:	
				return requested_file.read()
		else:
			return None
		
	def render_mapping(self, request_path):
		actions = c_global.actions
		
		if actions.has_key(request_path):
			return actions[request_path](c_global)
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
			c_global.request_body = self.rfile.read(length)
			if self.headers.has_key('Content-Type') and \
					self.headers['Content-Type']=='application/x-www-form-urlencoded':
				c_global.post_query = cgi.parse_qs(c_global.request_body)
			else:
				c_global.post_query = None

		self.handle_request()


class Env(object):
	def __init__(self, module_path='scripts'):
		#this is a mapping from urls to functions that take an Env as argument
		self.actions = {}

		module_list = \
			[path.splitext(filename)[0] for filename in os.listdir(module_path)\
			 if path.splitext(filename)[1] == '.py']
		for module_name in module_list:
			module_info = imp.find_module(module_name, [module_path])
			module = imp.load_module(module_name, module_info[0], 
									 module_info[1], module_info[2])
			setattr(self, module_name, module)
			module.update_actions(self.actions)

c_global = Env()

if __name__ == '__main__':
	server = HTTPServer(('localhost', 8080), ClientHTTPServer)
	webbrowser.open('http://localhost:8080/login.html')
	server.serve_forever()
