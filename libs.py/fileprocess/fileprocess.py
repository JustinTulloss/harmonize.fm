#A thread that allows us to process files
from __future__ import with_statement
import pylons
import threading
from Queue import Queue, Empty

#The different handlers, eventually to be done elsewhere?
from actions import *

file_queue = Queue()
msglock = threading.Lock()

class NextAction(object):
    def __init__(self):
        self.NOTHING = 0
        self.TRYAGAIN = 1
        self.FAILURE = 2
        self.AUTHENTICATE = 3

class UploadStatus(object):
    def __init__(self, message=None, nextaction=None, file=None):
        assert file.has_key('session')
        assert file['session'] is not None

        self.nextaction = nextaction
        self.message = message
        self.file = file

        with msglock:
            file['session'].get('uploadmsgs').append(self)
            file['session'].save()

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

        self.handlers = [
            Mover(),
            FacebookAction(),
            TagGetter(),
            DBChecker(),
            BrainzTagger(),
            DBRecorder(),
            S3Uploader()
        ]

        # Set up our chain of handlers
        for x in range(len(self.handlers)-1):
            self.handlers[x].nextqueue = self.handlers[x+1].queue

        #self.handlers[len(self.handlers)-1].nextqueue = self._endqueue

        #GO GO GO!
        self._thread = threading.Thread(None,self)
        self._thread.start()
   
    def __call__(self):
        while(self.running):
            newfile = file_queue.get()
            self.handlers[0].queue.put(newfile)
