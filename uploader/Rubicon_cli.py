#!/usr/bin/env python
#vim:expandtab:smarttab
import upload, os, sys, fb, db

session_key = None

def main():
    if len(sys.argv)>1:
        path = sys.argv[1]
    else:
        print "Please give a directory to upload"
        return

    db.set_upload_src('folder')
    db.set_upload_dirs([path])
    print 'starting uploader'
    fb.login(upload.login_callback) 
    upload.start_uploader(TextView())


class TextView(object):
    def __init__(self):
        class Actions(object):
            def init(self):
                print 'Initializing'
                self.remaining = 0
                self.skipped = 0

            def inc_totalUploaded(self):
                self.totalUploaded += 1

            def set_totalUploaded(self, val):
                my.totalUploaded = val

            def inc_skipped(self):
                my.skipped += 1

            def dec_remaining(self):
                my.remaining -= 1
                print '%s songs remaining' % my.remaining

            def inc_remaining(self):
                my.remaining += 1

            def set_progress(self, spinning, val=None):
                pass

            def set_msg(self, msg):
                print msg

            def loginEnabled(self, val):
                pass

            def optionsEnabled(self, val):
                pass

            def listenEnabled(self, val):
                fb.login(upload.login_callback)

            def activate(self):
                pass
        self.a = Actions()

        self.actions = []
        def add_action(self, fn, params):
            self.actions.push((fn, params))

        def complete_actions(self):
            while self.actions != []:
                fn, params = self.actions.pop(0)
                fn(*params)

        def do_action(self, fn, params):
            self.add_action(fn, params)
            self.complete_actions() 

if __name__ == '__main__':
    main()
