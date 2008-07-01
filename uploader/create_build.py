from popen2 import popen2
import re

def create():
    build_file = open('build.py', 'w+')
    stdout, stdin = popen2('hg identify')
    stdin.close()

    match = re.match('^[a-fA-F0-9]+', stdout.read())
    if not match:
        raise Exception('Unable to determine build version')

    build_file.write('repo_version = "%s"' % match.group(0))
    build_file.close()
