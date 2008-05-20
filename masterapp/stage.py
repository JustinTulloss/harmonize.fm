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
n:~$ ln -s /var/www/sites/stage/masterapp/stage.py .
brian@rubicon:~$ ls
1  2  stage.py
brian@rubicon:~$ sudo python stage.py
[sudo] password for brian:
pulling from /var/www/sites/repo/main
searching for changes
adding changesets
adding manifests
adding file changes
added 4 changesets with 6 changes to 5 files
5 files updated, 0 files merged, 0 files removed, 0 files unresolved
[Errno 17] File exists: '../masterapp/public/javascripts/compressed'
[Errno 17] File exists: '../masterapp/public/stylesheets/compressed'
Changing user to www-data:www-data (33:33)
    'hg',
    'pull',
    '-u'
])

#Update compressed javascript
os.chdir('helpers')
sys.path.append('.')
import compressor
compressor.main()

os.chdir('..')

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

os.system('/etc/init.d/lighttpd restart')

