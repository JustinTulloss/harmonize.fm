import webbrowser, cgi, thread, urlparse, socket
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import config

server_url = 'http://'+config.current['server_addr']+':'+ \
		str(config.current['server_port'])+'/desktop_login'
thread_started = False

def login(callback):
	"""A non-blocking function that handles facebook login through a web
	browser. callback should be a function that takes the session key as an
	argument"""
	global thread_started, server_url
	if thread_started == False:
		thread.start_new_thread(wait_login, (callback,))
		thread_started = True

	webbrowser.open(server_url)

def synchronous_login():
	global session_key, server_url

	session_key = None #This needs to be reset for reauthenticating uploader

	server = HTTPServer(('localhost', 26504), LoginServer)
	webbrowser.open(server_url)
	while session_key == None:
		server.handle_request()

	return session_key

session_key = None

def get_session_key():
	global session_key
	return session_key

def wait_login(callback=None):
	global session_key
	server = HTTPServer(('localhost', 26504), LoginServer)
	while session_key == None:
		server.handle_request()

	callback(session_key)

class LoginServer(BaseHTTPRequestHandler):
	def error(self):
		self.send_response(404)
		self.end_headers()
	def log_message(format, *args):
		pass

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
		
	success_response = """<html>
	<style type="text/css">
		body {
			font-family: "Lucida Sans Unicode","Lucida Grande","Lucida Sans","Lucida",sans-serif;
		}
		#main {
			text-align: center;
			width: 100%;
			color: #334466;
			padding-top: 10px;
		}
		h1 {
			font-size: 34pt;
			margin-top: 30px;
		}
	</style>
<body>
<div id="main">
	<center>
	<img src="http://stage.harmonize.fm/images/bigharmonized.png" />
		<h1>Login successful!</h1>
		<h2>You can close this window.</h2>
	</center>
</div>
</body></html>"""
