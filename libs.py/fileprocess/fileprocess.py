# vim:expandtab:smarttab
#A thread that allows us to process files

from __future__ import with_statement
import sys
sys.path.insert(0, '..')
import pylons
import threading
from Queue import Queue, Empty
import socket
import cPickle
from configuration import *
pickle = cPickle

#The different handlers
from actions import *

config = {}

class MsgQueue(object):
    def __init__(self):
        self.msglock = threading.Lock()
        self.msgs = {}

    def add(self, fbsession, upload_status):
        """Adds the upload status to the queue for a given session key"""
        with self.msglock:
            if self.msgs.has_key(fbsession):
                self.msgs[fbsession].append(upload_status)
            else:
                self.msgs[fbsession] = [upload_status]
    
    def get(self, fbsession):
        """Returns a list of all messages for a given session key and removes
           them from the queue."""
        with self.msglock:
            if self.msgs.has_key(fbsession):
                res = self.msgs[fbsession]
                del self.msgs[fbsession]
                return res
            else:
                return []

msgs = MsgQueue()

class NextAction(object):
    def __init__(self):
        self.NOTHING = 0
        self.TRYAGAIN = 1
        self.FAILURE = 2
        self.AUTHENTICATE = 3

class UploadStatus(object):
    def __init__(self, message=None, nextaction=None, file=None):
        """
        assert file.has_key('fbsession')

        self.nextaction = nextaction
        self.message = message
        self.file = file

        msgs.add(file['fbsession'], self)
        """
        pass

na = NextAction()

class FileUploadThread(object):
    """
    A thread that processes files that have been uploaded.
    It doesn't really do anything except wait for things to go into the Queue.
    Once it discovers something in the queue, it goes down a list of functions
    that are registered to be notifified of new files being uploaded. 
    Once they are done, they callback into this thread and it will push the 
    completed file into the next queue for the next thing that wants to 
    know about file uploading
    """

    def __init__(self):
        super(FileUploadThread, self).__init__()
        self._endqueue = Queue()
        self.running = 1
        self._fqueue =  Queue()

        cleanup = Cleanup() # A Special thread for cleaning up errors

        self.handlers = [
            Mover(),
            TagGetter(),
            Hasher(),
            Transcoder(),
            DBChecker(),
            BrainzTagger(),
            AmazonCovers(),
            S3Uploader(),
            DBRecorder()
        ]

        # Set up our chain of handlers
        for x in range(len(self.handlers)-1):
            self.handlers[x].nextaction = self.handlers[x+1]
            self.handlers[x].cleanup_handler = cleanup

        # GO GO GO!
        self._thread = threading.Thread(None,self)
        self._thread.start()

    def process(self, file):
        self._fqueue.put(file)
   
    def __call__(self):
        while(self.running):
            newfile = self._fqueue.get()
            self.handlers[0].queue.put(newfile)

def main():
    # Initialize the processing thread
    fp = FileUploadThread()

    # Initialize the config
    global config
    config = debug_config
    if '--production' in sys.argv:
        config.update(production_config)

    # Initialize the file socket
    fsock = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM
    )
    fsock.connect(('localhost', 48260))
    fsock.listen(5)
    while True:
        pfile = ''
        csock, caddr = fsock.accept()
        while received != '':
            received = csock.recv(40)
            pfile = pfile + received

        file_queue.put(pickle.loads(pfile))

if __name__ == '__main__':
    main()
