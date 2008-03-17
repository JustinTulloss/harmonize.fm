import cgi
import os.path as path
from urlparse import urlsplit
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class ClientHTTPServer(BaseHTTPRequestHandler):
	requests = 0 #we want to say we have the file in question on odd requests

	def redirect(self, url):
		print 'Redirecting to: ', url
		self.send_response(307)
		self.send_header('Location', url)
		self.end_headers()

	def handle_request(self):
		#split path into components 
		split_url = urlsplit(self.path)
		request_path = split_url.path
		
		#parse the query string
		self.query = cgi.parse_qs(split_url.query)

		if request_path[:9] == '/uploads/' and self.request_body == None:
			print 'Asking if file ', request_path[9:], 'has been uploaded'
			response = str(self.requests % 2)
			self.requests += 1
		elif request_path[:9] == '/uploads/' and self.request_body != None:
			print 'Attempting to upload the file ', request_path[9:], \
					'with file length: ', self.length
			response = None
		elif request_path == '/desktop_login':
			return self.redirect('http://localhost:8080/complete_login?session_key=asdf')
		else:
			print 'Error: unkown request received'
			response = None
			

		self.send_response(200)
		self.end_headers()
		if response != None:
			self.wfile.write(response)
		
	def do_GET(self):
		self.request_body = None
		self.handle_request()
	
	def do_POST(self):
		if self.headers.has_key('Content-Length'):
			self.length = int(self.headers['Content-Length'])
			self.request_body = self.rfile.read(self.length)
			if self.headers.has_key('Content-Type') and \
					self.headers['Content-Type']=='application/x-www-form-urlencoded':
				self.post_query = cgi.parse_qs(self.request_body)
			else:
				self.post_query = None

		self.handle_request()

if __name__ == '__main__':
	server = HTTPServer(('localhost', 2985), ClientHTTPServer)
	server.serve_forever()
