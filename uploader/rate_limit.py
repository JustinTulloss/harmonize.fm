import config, fb
import httplib, time, thread, threading, math
from httplib import HTTPConnection

debug = False

def send_rate_limited(connection, url, contents):
	global pinger, debug
	#connection.set_debuglevel(1)
	if pinger == None: raise Exception()

	connection.putrequest("POST", url)
	connection.putheader("Content-Type", "audio/x-mpeg-3")
	connection.putheader("Content-Length", str(len(contents)))
	connection.endheaders()

	interval = 1.0

	while contents != '':
		amount = pinger.get_rate()*1024

		t1 = time.time()
		connection.send(contents[:amount])
		contents = contents[amount:]
		t2 = time.time()
		
		elapsed = t2-t1
		if elapsed < interval:
			if debug: print 'Time taken: %s' % (elapsed)
			time.sleep(interval-elapsed)
		else:
			if debug: print 'Interval exceeded, ran for %s seconds' % elapsed
	
	pinger.running = False
	return connection.getresponse()

def ping(connection):
	t1 = time.time()
	connection.request('GET', '/upload_ping')
	connection.getresponse().read()
	t2 = time.time()
	return t2-t1

def get_baseline(connection):
	ping(connection)

	baseline = 0.0
	iterations = 6
	for i in range(iterations):
		baseline += ping(connection)
	
	return baseline/iterations

def establish_baseline(addr, port):
	global pinger
	
	connection = HTTPConnection(addr, port)
	baseline = get_baseline(connection)
	
	pinger = Pinger(baseline, addr, port)

def reestablish_baseline(addr, port):
	global pinger

	connection = HTTPConnection(addr, port)
	baseline = get_baseline(connection)

	pinger.reset(baseline)

class Pinger(object):
	def __init__(self, baseline, addr, port):
		self.baseline = baseline
		self.lock = threading.Lock()
		self.rate = 20
		self.running = True
		self.idleticks = 0
		self.state = 'expand'
		self.counter = 0
		self.connection = httplib.HTTPConnection(addr, port)
		ping(self.connection) #First ping always take longer

		self.thread = thread.start_new_thread(self.loop, ())

	def update_rate(self, status):
		global debug

		vals = {'fast': -2, 'ok': -1, 'slow': 1}
		self.counter += vals[status]

		if self.state == 'expand' and self.counter < -4:
			self.rate += 10
			self.counter = 0
			if debug: print 'Increasing upload rate to %s' % self.rate
		elif self.counter > 4 and self.state == 'expand':
			self.rate = int((self.rate/10)*.8)*10
			self.state = 'maintain'
			self.counter = 0
			if debug:
				print 'Going into maintain mode, final rate is %s' % self.rate
		elif self.counter > 4:
			self.rate = max(10, self.rate-5)
			self.counter = 0
			if debug: print 'Whoa now, slowing down upload to %s' % self.rate

	def loop(self):
		global debug

		while self.running:
			self.lock.acquire()
			if self.idleticks == 0:
				self.lock.release()
				time.sleep(1)
				continue
			
			self.idleticks -= 1
			self.lock.release()

			try:
				pingtime = ping(self.connection)
			except Exception:
				continue

			self.lock.acquire()
			error = (pingtime - self.baseline) / pingtime
			if error < -.2:
				self.update_rate('fast')
				if debug:
					print 'pingtime is fast: %s / %s' % (pingtime*1000, self.baseline*1000)
			elif error < .4:
				self.update_rate('ok')
				if debug:
					print 'pingtime is ok: %s / %s' % (pingtime*1000, self.baseline*1000)
			else:
				self.update_rate('slow')
				if debug:
					print 'pingtime is slow: %s / %s' % (pingtime*1000, self.baseline*1000)
			self.lock.release()
			time.sleep(.6)

	def get_rate(self):
		self.lock.acquire()
		rate = self.rate
		self.idleticks = 3
		self.lock.release()
		return rate

	def reset(self, baseline):
		self.lock.acquire()
		self.idleticks = 0
		self.state = 'expand'
		self.counter = 0
		self.lock.release()

def test_send(filename='02 Vacileo.mp3'):
	file_contents = open(filename).read()
	session_key = fb.synchronous_login()
	url = '/uploads/abc' #?session_key=' + session_key
	addr = config.staging['server_addr']
	port = config.staging['server_port']
	connection = httplib.HTTPConnection(addr, port)
	
	establish_baseline(addr, port)

	connection.request('GET', url)
	print 'GET response:', connection.getresponse().read()
	response = send_rate_limited(connection, url, file_contents)
	print 'response:', response.read()

if __name__ == '__main__':
	test_send()