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
    

if __name__=='__main__':
    main()
