#!/usr/bin/env python
#vim:expandtab:smarttab
import upload, os, sys, fb, db, thread, time

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
    #fb.login(upload.login_callback) 
    thread.start_new_thread(upload.start_uploader, (TextView(),))
    while True:
        time.sleep(10)


class TextView(object):
    def __init__(self):
        my = self
        class Actions(object):
            def init(self):
                print 'Initializing'
                my.remaining = 0
                my.skipped = 0

            def inc_totalUploaded(self):
                my.totalUploaded += 1

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
                if val:
                    fb.login(upload.login_callback)

            def optionsEnabled(self, val):
                pass

            def listenEnabled(self, val):
                pass

            def activate(self):
                pass
        self.a = Actions()

        self.actions = []
    def add_action(self, fn, params):
        self.actions.append((fn, params))

    def complete_actions(self):
        while self.actions != []:
            fn, params = self.actions.pop(0)
            fn(*params)

    def do_action(self, fn, params):
        self.add_action(fn, params)
        self.complete_actions() 

if __name__ == '__main__':
    main()
