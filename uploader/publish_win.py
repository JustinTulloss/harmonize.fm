import os, sys
import config

def notify_user(msg):
	sys.stderr.write(msg+'\n')
	raw_input('Press enter to exit ')
	sys.exit(1)

def run_cmd(cmd):
	if os.system(cmd) != 0:
		notify_user('Command "%s" failed!'%cmd)

def run_cmds(*cmds):
	for cmd in cmds:	
		run_cmd(cmd)


if config.current != config.production:
	notify_user('Change current configuration to production before running')

run_cmds(
	'python setup.py py2exe',
	r'"C:\Program Files\Inno Setup 5\iscc" windows_installer.iss',
	'pscp Output\setup.exe harmonize.fm:/var/opt/uploaders')
	
