#!/usr/bin/env python

"""
This script is for deploying the staging server. It automatically updates the
codebase and restarts paster in daemon mode. Optionally, pass it -d to go into
staging debug mode (no daemon and with the debugger turned on)
"""
import deploy

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
