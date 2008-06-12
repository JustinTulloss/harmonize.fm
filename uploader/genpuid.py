import subprocess
import re
from hplatform import get_genpuid_path

def gen(filename):
	prog = subprocess.Popen(
				[get_genpuid_path(), 'ffa7339e1b6bb1d26593776b4257fce1', 
			 			'-noanalysis', filename],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE)
	match = re.search(r'puid: ([0-9a-z-]+)', prog.stdout.read())
	
	prog.stderr.read()

	if not match or prog.wait() != 0:
		return None
	
	return match.group(1)
