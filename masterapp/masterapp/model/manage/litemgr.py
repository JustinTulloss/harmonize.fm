#!/usr/bin/env python
from migrate.versioning.shell import main

main(url='sqlite:///../../../music.db',repository='.')
