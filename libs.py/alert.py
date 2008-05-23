#!/usr/bin/python
import mailer
import sys
from ConfigParser import SafeConfigParser

config_paths = ['/var/www/sites/stage/masterapp/development.ini',
				'/Users/brian/rubicon/masterapp/development.ini']

def alert(subject, message):
	configp = SafeConfigParser()
	configp.read(config_paths)

	smtp_addr = configp.defaults()['smtp_server']
	smtp_port = configp.defaults()['smtp_port']
	alert_email = configp.defaults()['alert_email']
	alert_password = configp.defaults()['alert_password']

	mailer.mail(smtp_addr, smtp_port, alert_email, alert_password, 
				'founders@harmonize.fm', subject, message)

if __name__ == '__main__':
	args = sys.argv[1:]
	if len(args) != 2:
		print 'Usage: alert.py <subject> <message>'

	subject = args[0]
	message = args[1]
	alert(subject, message)
