#!/usr/bin/env python

"""
This script is for deploying the staging server. It automatically updates the
codebase and restarts paster in daemon mode. Optionally, pass it -d to go into
staging debug mode (no daemon and with the debugger turned on)
"""
import os, sys
import subprocess
from mercurial.localrepo import localrepository
from mercurial.ui import ui
from deploy import deploy

REPOPATH = os.path.join(os.environ['REPOSITORY'], 'masterapp')

#Change to repository
os.chdir(REPOPATH)

#Update repository
subprocess.check_call(['hg', 'up'])

#Update compressed javascript
os.chdir('./helpers')
sys.path.append('.')
import compressor
compressor.main()

#Install changes in stage server
deploy('STAGING', '-d' in sys.argv or '--debug' in sys.argv)

#Record the current version.
repo = localrepository(ui(), os.environ['REPOSITORY'])
fd = open(os.path.join(os.environ['STAGING'], 'changeset'), 'w')
fd.write(str(repo.changectx()))
fd.close()
