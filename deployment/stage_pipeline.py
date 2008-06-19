#!/usr/bin/env python

"""
This deploys the stage file_pipeline
"""
import os, sys
import subprocess
from mercurial.localrepo import localrepository
from mercurial.ui import ui
from deploy import deploy

REPOPATH = os.path.join(os.environ['REPOSITORY'], 'fileprocess')
STAGEPATH = os.path.join(os.environ['STAGE'])
SERVER = 'stage_file_pipeline'

# Change to repository
os.chdir(REPOPATH)

# Update repository
subprocess.check_call(['hg', 'up'])

# Install the fileprocess
subprocess.check_call([STAGEPATH+'/bin/python', 'setup.py', 'install'])

# Restart the fileprocess
proxy = xmlrpclib.ServerProxy('http://localhost:9001')
if proxy.supervisor.getProcessInfo(SERVER)['statename'] == 'RUNNING':
    proxy.supervisor.stopProcess(SERVER)

proxy.supervisor.startProcess(SERVER)
