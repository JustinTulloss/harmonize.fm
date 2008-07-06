"""This file ensures that there is only one instance of the program running,
   and shows the currently running instance if there is"""

from socket import socket
from thread import start_new_thread
import atexit
from excepthandler import exception_managed

class PortInUse(Exception):
	pass

def set_callback(new_callback):
	global callback
	callback = new_callback

callback = None

def atexit():
	global port
	sock = socket()
	sock.connect(('127.0.0.1', port))
	if sock.recv(9) == 'harmonize':
		sock.send('q')
	sock.close()

port = 26505
def running():
	global port

	sock = socket()
	if sock.connect_ex(('127.0.0.1', port)) == 0:
		if sock.recv(9) == 'harmonize':
			sock.send('c')
			sock.close()
			return True
		else:
			raise PortInUse()
	else:
		@exception_managed
		def start_server(port):
			global callback
			server_sock = socket()
			server_sock.bind(('127.0.0.1', port))
			server_sock.listen(2)
			while True:
				request, addr = server_sock.accept()
				request.send('harmonize')
				res = request.recv(1)
				request.close()
				if res == 'c' and callback:
					callback()
				elif res == 'q':
					break
			server_sock.close()


		start_new_thread(start_server, (port,))
		return False
