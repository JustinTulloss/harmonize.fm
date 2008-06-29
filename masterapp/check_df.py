#!/usr/bin/python
from popen2 import popen2

import sys
sys.path.extend(['/var/www/sites/stage/libs.py', 
				 '/Users/brian/rubicon/libs.py'])
import alert

stdout, stdin = popen2('df .')
stdout.readline() #stip column headers
data = [field for field in stdout.readline().split(' ') if field.endswith('%')]
used = int(data[0][:-1])
if used > 70:
	alert.alert('Disk space used at '+str(used)+'%' , '')

stdout, stdin = popen2("free -tm | awk '/Mem:/ {print $4}'")
free = int(stdout.readline().rstrip())
if free < 45:
	alert.alert('Memory free at %s MB' % free, '')
