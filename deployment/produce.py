#!/usr/bin/env python

# This script installs the code currently being staged on the production server

import os
from deploy import deploy
import subprocess

STAGING = os.environ['STAGING']
REPOSITORY = os.environ['REPOSITORY']

def main():
    # Get stage revision
    fd = open(os.path.join(STAGING, 'changeset'))
    changeset = fd.read()
    fd.close()
    os.chdir(REPOSITORY)

    # Update the repo to what the stage is currently running
    subprocess.check_call(['hg', 'up', '-r', changeset])

    # Deploy that code
    deploy('PRODUCTION')

    # Update the database schema
    os.chdir(os.path.join(
        os.environ['REPOSITORY'],'masterapp', 'masterapp', 'model', 'manage')
    )
    subprocess.check_call(['python', 'mysqlprodmgr.py', 'upgrade'])

    

if __name__=='__main__':
    main()
