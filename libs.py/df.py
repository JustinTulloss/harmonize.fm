#!/var/www/sites/live/bin/python
import subprocess
import re

def check(path):
	proc = subprocess.Popen(['df', path], stdout=subprocess.PIPE, 
										  stderr=subprocess.PIPE)
	proc.stdout.readline()
	line = proc.stdout.readline()
	used = int(re.match(r'.*\s(\d+)%', line).groups()[0])

	proc.stdout.read()
	proc.stderr.read()
	return used

if __name__ == '__main__':
	import alert

	if check('/var/opt/media') > 70:
		alert.alert('Disk usage at '+str(used)+'%!', '')
