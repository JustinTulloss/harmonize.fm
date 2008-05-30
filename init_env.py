#!/usr/bin/env python

"""
This script initializes your environment to work the way it should.
"""
import os, sys
import subprocess
import shutil
from deployment.deploy import to_setup, to_fetch
from os.path import join

USAGE = """
Without arguments, just sets environment variables. Run with -i to install
necessary packages
"""
def setup_env_variables():
    """
    Sets the appropriate environment variables.
    """
    ENV_SH = '/var/local/rubicon_env.sh'
    if os.path.exists(ENV_SH) and \
            not os.environ.has_key('PRODUCTION'):
        brc = open('~/.bashrc', 'a')
        brc.write('source %s' % ENV_SH)
        brc.close()
        os.system('source %s' % ENV_SH)

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
            try:
                shutil.rmtree(package[0])
            except Exception:
                pass

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
