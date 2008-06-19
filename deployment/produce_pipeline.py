#!/usr/bin/env python

# This script installs the code currently being staged on the production server

import os
import subprocess
import xmlrpclib

STAGING = os.environ['STAGING']
PRODUCTION = os.environ['PRODUCTION']
REPOSITORY = os.path.join(os.environ['REPOSITORY'], 'fileprocess')
SERVER = 'live_file_pipeline'

def main():
    # Get stage revision
    fd = open(os.path.join(STAGING, 'pipeline-changeset'))
    changeset = fd.read()
    fd.close()
    os.chdir(REPOSITORY)

    # Update the repo to what the stage is currently running
    subprocess.check_call(['hg', 'up', '-r', changeset])

    # Install the fileprocess
    subprocess.check_call([PRODUCTION+'/bin/python', 'setup.py', 'install'])

    # Restart the fileprocess
    proxy = xmlrpclib.ServerProxy('http://localhost:9001')
    if proxy.supervisor.getProcessInfo(SERVER)['statename'] == 'RUNNING':
        proxy.supervisor.stopProcess(SERVER)

    proxy.supervisor.startProcess(SERVER)

if __name__=='__main__':
    main()
