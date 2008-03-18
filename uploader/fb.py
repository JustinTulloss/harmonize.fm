import webbrowser, cgi, thread, urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

thread_started = False

def login(callback):
	"""A non-blocking function that handles facebook login through a web
	browser. callback should be a function that takes the session key as an
	argument"""
	global thread_started
	if thread_started == False:
		thread.start_new_thread(wait_login, (callback,))
		thread_started = True
	webbrowser.open('http://localhost:2985/desktop_login')

session_key = None

def wait_login(callback):
	global session_key
	server = HTTPServer(('localhost', 8080), LoginServer)
	while session_key == None:
		server.handle_request()

	callback(session_key)

class LoginServer(BaseHTTPRequestHandler):
	def error(self):
		self.send_response(404)
		self.end_headers()

	def do_GET(self):
		global session_key
		url = urlparse.urlsplit(self.path)
		if url.path != '/complete_login':
			return self.error()

		query = cgi.parse_qs(url.query)
		session_key = query['session_key'][0]
		
		self.send_response(200)
		self.end_headers()
		self.wfile.write(self.success_response)
		
	success_response = """<html><body><p>Login successful!</p>
							<p>You can close this window.</p>
							</body></html>"""
