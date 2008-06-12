import subprocess
import re

def gen(filename):
	prog = subprocess.Popen(
				['./genpuid', 'ffa7339e1b6bb1d26593776b4257fce1', 
			 			'-noanalysis', filename],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE)
	match = re.search(r'puid: ([0-9a-z-]+)', prog.stdout.read())
	
	prog.stderr.read()

	if not match or prog.wait() != 0:
		return None
	
	return match.group(1)
