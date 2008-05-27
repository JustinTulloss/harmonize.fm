#!/usr/bin/env python

# This script moves code to production and installs it
# It expects the PRODUCTION and REPO environment variables to be set.

import sys
import os
import shutil
import subprocess
import xmlrpclib

PRODUCTION = os.environ['PRODUCTION']
STAGING = os.environ['STAGING']
REPOSITORY = os.environ['REPOSITORY']

def main():
    try:
        setup(os.path.join(STAGING, 'masterapp'))
        setup(os.path.join(STAGING, 'libs.py'))
        setup(os.path.join(STAGING, 'fileprocess'))
        configure()
        restart()
    except:
        type, value, traceback = sys.exc_info()
        print "An exception occurred %s, %s: %s" % (type.__name__, value, traceback)
    finally:
        cleanup()

def setup(path):
    os.chdir(path)
    subprocess.check_call([
        os.path.join(PRODUCTION,'bin','python'), 'setup.py', 'install'
    ])

def configure():
    configdir = os.path.join(PRODUCTION, 'config')
    if not os.path.exists(configdir):
        os.makedirs(configdir)
    os.chdir(os.path.join(STAGING, 'masterapp'))
    shutil.copy('development.ini', configdir)
    shutil.copy('production.ini', configdir)
    shutil.copy('live.ini', configdir)

def restart():
    proxy = xmlrpclib.ServerProxy('http://localhost:9001')
    if proxy.supervisor.getProcessInfo('live_server')['statename'] == 'RUNNING':
        proxy.supervisor.stopProcess('live_server')
    proxy.supervisor.startProcess('live_server')

def cleanup():
    pass

if __name__=='__main__':
    main()
