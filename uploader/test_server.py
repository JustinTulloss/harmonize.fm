import cgi
import os.path as path
from urlparse import urlsplit
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import config

fbsession = 1
requests = 0

class ClientHTTPServer(BaseHTTPRequestHandler):
	def redirect(self, url):
		print 'Redirecting to: ', url
		self.send_response(307)
		self.send_header('Location', url)
		self.end_headers()

	def GET_response(self):
		global requests, fbsession
		if requests % 2 == 0:
			status = 200 #This means the file doesn't exist on the server
		else:
			status = 201

		if requests % 7 == 0:
			print 'Changing session key'
			fbsession += 1

		requests += 1
		return (status, '')

	def handle_request(self):
		global fbsession
		#split path into components 
		split_url = urlsplit(self.path)
		request_path = split_url.path
		
		#parse the query string
		self.query = cgi.parse_qs(split_url.query)
		if self.query.has_key('session_key'):
			session_key = int(self.query['session_key'][0])
		else:
			session_key = None

		if request_path[:9] == '/uploads/' and self.request_body == None:
			print 'Asking if file ', request_path[9:], 'has been uploaded'
			(status, response) = self.GET_response()
		elif request_path[:9] == '/uploads/' and self.request_body != None:
			print 'Attempting to upload the file ', request_path[9:], \
					'with file length: ', self.length
			if session_key != fbsession:
				print 'Session key invalid, need to reauth'
				status = 450
			else:
				status = 200
			response = None
		elif request_path == '/desktop_login':
			return self.redirect('http://localhost:8080/complete_login?session_key='+str(fbsession))
		else:
			print 'Error: unkown request received'
			response = None
			status = 404

		self.send_response(status)
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
	server = HTTPServer(('', config.test_server['server_port']),
						ClientHTTPServer)
	server.serve_forever()
