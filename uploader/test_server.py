import cgi
import os.path as path
import random, simplejson
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
			response = 'upload' 
		else:
			response = 'done'

		if requests % 20 == 0:
			print 'Changing session key'
			fbsession += 1

		requests += 1
		return response

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

		status = 200
		if request_path == '/upload/tags' and self.post_query.has_key('tags'):
			tags = simplejson.loads(self.post_query['tags'][0])
			response_list = [self.GET_response() for tag in tags]
			response = simplejson.dumps(response_list)
		elif request_path == '/upload/tags':
			title = self.post_query['title'][0]
			print 'Asking if file', title,\
					'has been uploaded'
			response = self.GET_response()
		elif request_path[:12] == '/upload/file' and self.request_body != None:
			print 'Attempting to upload the file ', request_path[12:], \
					'with file length: ', self.length
			if session_key != fbsession:
				print 'Session key invalid, need to reauth'
				response = 'reauthenticate'
			else:
				response = 'done'
		elif request_path == '/desktop_login':
			return self.redirect('http://localhost:26504/complete_login?session_key='+str(fbsession))
		elif request_path == '/upload_ping':
			print 'ping received'
			response = ''
		else:
			print 'Error: unknown request received (%s)' % request_path
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
			if self.headers.get('Content-Type') != 'audio/x-mpeg=3':
				self.request_body = self.rfile.read(self.length)
			else:
				while len(self.rfile.read(1024)) == 1024:
					if random.uniform(0, 3) == 0:
						print 'Closing in file'
						rfile.close()
					pass
			if self.headers.get('Content-Type') ==\
							'application/x-www-form-urlencoded':
				self.post_query = cgi.parse_qs(self.request_body)
			else:
				self.post_query = None

		self.handle_request()

if __name__ == '__main__':
	server = HTTPServer(('', config.test_server['server_port']),
						ClientHTTPServer)
	server.serve_forever()
