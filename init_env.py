#!/usr/bin/env python

"""
This script initializes your environment to work the way it should.
"""
import os, sys
import subprocess
import shutil
from os.path import join

USAGE = """
Without arguments, just sets environment variables. Run with -i to install
necessary packages
"""
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

def setup_env_variables():
    """
    Sets the appropriate environment variables.
    """
    if os.path.exists('/var/local/rubicon_env.sh') and \
            not os.environ.has_key('PRODUCTION'):
        brc = open('~/.bashrc', 'a')
        brc.write('source /var/local/rubicon_env.sh')
        brc.close()

def create_dev_env():
    """
    Installs all the software necessary to develop.
    """

    repo = os.path.abspath(os.curdir)
    for package in to_fetch:
        try:
            os.system(package[1])
            os.chdir(join(repo, package[0]))
            subprocess.check_call([
                'python', 'setup.py', 'install'
            ])
        finally:
            os.chdir(repo)
            shutil.rmtree(package[0])

    for package in to_setup:
        os.chdir(join(repo, package))
        subprocess.check_call([
            'python',
            'setup.py',
            'develop'
        ])

def main():
    if '-h' in sys.argv or '--help' in sys.argv:
        print USAGE
        sys.exit(0)
    
    setup_env_variables()

    if '-i' in sys.argv or '--install' in sys.argv:
        create_dev_env()

if __name__ == '__main__':
    main()
