"""
Utilites to deploy rubicon
"""
import subprocess
import os, sys
import shutil
import time
import xmlrpclib
from os.path import join

# a list of packages to run "setup.py develop" on
to_setup = [
    'masterapp',
    'libs.py',
    'fileprocess'
]

# a list of packages to download (and the command to do so) and install
to_fetch = [
    ('sqlalchemy',
    'svn checkout http://svn.sqlalchemy.org/sqlalchemy/trunk sqlalchemy')
]

def create_production_env(root):
    """
    Installs all the software necessary to serve a production site.
    """

    python = os.path.join(root, 'bin', 'python')
    os.chdir(root)
    for package in to_fetch:
        try:
            os.system(package[1])
            os.chdir(join(root, package[0]))
            subprocess.check_call([
                python, 'setup.py', 'install'
            ])
        finally:
            os.chdir(root)
            shutil.rmtree(package[0])

    for package in to_setup:
        os.chdir(join(root, package))
        subprocess.check_call([
            python,
            'setup.py',
            'install'
        ])

def deploy(env, debug=False):
    root = os.environ[env]
    create_production_env(root)

    #Restart server
    if env == 'STAGING':
        server = 'stage_server'
        pidpath = '/var/log/rubicon/paster.pid'
    elif env == 'PRODUCTION':
        server = 'live_server'
        pidpath = '/var/log/harmonize/paster.pid'

    proxy = xmlrpclib.ServerProxy('http://localhost:9001')
    if proxy.supervisor.getProcessInfo(server)['statename'] == 'RUNNING':
        proxy.supervisor.stopProcess(server)

    if debug:
        arglist = [
            'paster', 'serve', 
            '--user=www-data',
            '--group=www-data',
            '--pid-file', pidpath
        ]
        arglist.append('dproduction.ini')
        subprocess.check_call(arglist)
    else:
        proxy.supervisor.startProcess(server)

    # Restart lighty to ensure that the fastcgi connection is fresh
    os.system('/etc/init.d/lighttpd restart')

