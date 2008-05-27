#!/usr/bin/env python

"""
This script is for deploying the staging server. It automatically updates the
codebase and restarts paster in daemon mode. Optionally, pass it -d to go into
staging debug mode (no daemon and with the debugger turned on)
"""

import subprocess
import os, sys
import time
import xmlrpclib

PIDPATH = '/var/log/rubicon/paster.pid'
STAGEPATH = '/var/www/sites/stage/masterapp'

proxy = xmlrpclib.ServerProxy('http://localhost:9001')
if proxy.supervisor.getProcessInfo('stage_server')['statename'] == 'RUNNING':
    proxy.supervisor.stopProcess('stage_server')
    

#Change to staging directory
os.chdir(STAGEPATH)

#Update repository
subprocess.check_call(['hg', 'pull', '-u'])

#Update compressed javascript
os.chdir('./helpers')
sys.path.append('.')
import compressor
compressor.main()
os.chdir('..')

#Restart server
if '-d' in sys.argv or '--debug' in sys.argv:
    arglist = [
        'paster', 'serve', 
        '--user=www-data',
        '--group=www-data',
        '--pid-file', PIDPATH
    ]
    arglist.append('dproduction.ini')
    subprocess.check_call(arglist)
else:
    proxy.supervisor.startProcess('stage_server')

# Restart lighty to ensure that the fastcgi connection is fresh
#os.system('/etc/init.d/lighttpd restart')

