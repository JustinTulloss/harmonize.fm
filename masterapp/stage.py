#!/usr/bin/env python

"""
This script is for deploying the staging server. It automatically updates the
codebase and restarts paster in daemon mode. Optionally, pass it -d to go into
staging debug mode (no daemon and with the debugger turned on)
"""

import subprocess
import os, sys
import time

PIDPATH = '/var/log/rubicon/paster.pid'
STAGEPATH = '/var/www/sites/stage/masterapp'

#ignore errors, means server isn't already running
os.system('kill -9 `cat %s` 2> /dev/null' % (PIDPATH)) 

#Change to staging directory
os.chdir(STAGEPATH)

#Update repository
subprocess.check_call(['hg', 'pull', '-u'])

#Update compressed javascript
sys.path.append('./helpers')
import compressor
compressor.main()

#Restart server
arglist = [
    'paster', 'serve', 
    '--user=www-data',
    '--group=www-data',
    '--pid-file', PIDPATH
]

if '-d' in sys.argv or '--debug' in sys.argv:
    arglist.append('dproduction.ini')
else:
    arglist.append('production.ini')
    arglist.append('--daemon')

subprocess.check_call(arglist)

time.sleep(10)
os.system('/etc/init.d/lighttpd restart')

