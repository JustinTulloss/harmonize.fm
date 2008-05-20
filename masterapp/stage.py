#!/usr/bin/env python

"""
This script is for deploying the staging server. It automatically updates the
codebase and restarts paster in daemon mode. Optionally, pass it -d to go into
staging debug mode (no daemon and with the debugger turned on)
"""

import subprocess
import os, sys

PIDPATH = '/var/log/rubicon/paster.pid'
STAGEPATH = '/var/www/sites/stage/masterapp'

#Kill old server
try:
    fpid = open(PIDPATH)
    pid = fpid.read()

    subprocess.check_call(['kill', pid])
except Exception, e:
    print e

#Change to staging directory
try:
    os.chdir(STAGEPATH)
except Exception, e:
    print e

#Update repository
subprocess.check_call([
    'hg',
    'pull',
    '-u'
])

#Update compressed javascript
os.chdir('helpers')
sys.path.append('.')
import compressor
compressor.main()

#Restart server
arglist = [
    'paster', 
    'serve', 
    '--user=www-data',
    '--group=www-data',
    '--pid-file',
    PIDPATH
]

if '-d' in sys.argv or '--debug' in sys.argv:
    arglist.append('dproduction.ini')
else:
    arglist.append('production.ini')
    arglist.append('--daemon')

subprocess.check_call(arglist)

