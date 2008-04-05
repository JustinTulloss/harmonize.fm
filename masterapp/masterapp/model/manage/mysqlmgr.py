#!/usr/bin/env python
from migrate.versioning.shell import main
url = 'mysql://webappadmin:step2witch@localhost:3306/rubicon'
main(url=url,repository='.')
