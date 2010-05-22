import subprocess
import re

def create():
    build_file = open('build.py', 'w+')
    p = subprocess.Popen(['hg', 'identify'], stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()

    match = re.match('^[a-fA-F0-9]+', stdout)
    if not match:
        raise Exception('Unable to determine build version')

    build_file.write('repo_version = "%s"' % match.group(0))
    print "Version is: " + match.group(0)
    build_file.close()

if __name__ == '__main__':
    create()
