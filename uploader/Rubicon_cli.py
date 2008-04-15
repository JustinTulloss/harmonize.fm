#!/usr/bin/env python
#vim:expandtab:smarttab
import upload, os, sys, fb

session_key = None

def main():
    if len(sys.argv)>1:
        path = sys.argv[1]
    else:
        print "Please give a directory to upload"
        return

    def auth_callback(new_session_key):
        global session_key
        session_key = new_session_key

    fb.login(auth_callback)
    while session_key == None:
        pass

    tracks = upload.get_music_files(path)
    upload.upload_files(tracks, TextView())


class TextView(object):
    def init(self, msg, total_songs):
        print msg

    def update(self, msg, songs_left):
        print msg

    def error(self, msg):
        print "ERROR: "+msg

if __name__ == '__main__':
    main()
