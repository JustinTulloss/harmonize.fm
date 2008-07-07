#!/usr/bin/env python
#vim:expandtab:smarttab
import os, sys, fb
from db import use_new_db
from guimanager import GuiManager
from excepthandler import exception_managed

session_key = None

@exception_managed
def main():
    if len(sys.argv)>1:
        path = sys.argv[1]
    else:
        print "Please give a directory to upload"
        return

    if len(sys.argv) > 2:
        use_new_db(sys.argv[2])

    from db import db
    db.upload_src = 'folder'
    db.upload_dirs = [path]
    print 'starting uploader'
    fb.synchronous_login()
    guimgr = GuiManager(TextView(), 0)
    import upload
    upload.upload_files(db.get_tracks(), guimgr)


class TextView(object):
    def init(self):
        print 'Initializing'
        my.remaining = 0
        my.skipped = 0

    def set_uploaded(self, val):
        print 'Total songs uploaded:', str(val)

    def set_remaining(self, val):
        print 'Song remaining to upload:', str(val)

    def set_skipped(self, val):
        print 'Song skipped'

    def set_progress(self, spinning, val=None):
        pass

    def set_msg(self, msg):
        if msg in ['Analyzing library...']:
            return
        print msg

    def enable_login(self, val):
        if val:
            fb.login(upload.login_callback)

    def enable_options(self, val):
        pass

    def enable_listen(self, val):
        pass

    def activate(self):
        pass

    def fatal_error(self, msg):
        print 'Fatal error occured!'
        sys.exit(1)

    def start(self):
        pass

if __name__ == '__main__':
    main()
