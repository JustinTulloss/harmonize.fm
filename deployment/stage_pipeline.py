#!/usr/bin/env python

"""
This deploys the stage file_pipeline
"""
import os, sys
import subprocess
import xmlrpclib
from mercurial.localrepo import localrepository
from mercurial.ui import ui

REPOPATH = os.path.join(os.environ['REPOSITORY'], 'filemq')
STAGEPATH = os.path.join(os.environ['STAGING'])
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

# Record the current version.
repo = localrepository(ui(), os.environ['REPOSITORY'])
fd = open(os.path.join(os.environ['STAGING'], 'pipeline-changeset'), 'w')
fd.write(str(repo.changectx()))
fd.close()
