#A thread that allows us to process files
import pylons
import threading
from Queue import Queue, Empty

#The different handlers, eventually to be done elsewhere?
from factions.fmover import FMover

file_queue = Queue()

from Queue import Queue
class FileUploadThread(object):
    """
    A thread that processes files that have been uploaded.
    It doesn't reall do anything except wait for things to go into the Queue.
    Once it discovers something in the queue, it goes down a list of functions
    that are registered to be notifified of new files being uploaded. 
    Once they are done, they callback into this thread and it will push the 
    completed file into the next queue for the next thing that wants to 
    know about file uploading
    """

    def __init__(self):
        super(FileUploadThread, self).__init__()
        self.handlers = []
        self._endqueue = Queue()
        self.running = 1
        #TODO: Move this class initialization to some config file?
        self.handlers.insert(0, FMover())

        # Set up our chain of handlers
        for x in range(len(self.handlers)-1):
            self.handlers[x].nextqueue = self.handlers[x+1].queue

        self.handlers[len(self.handlers)-1].nextqueue = self._endqueue

        #GO GO GO!
        self._thread = threading.Thread(None,self)
        self._thread.start()
   
    def __call__(self):
        while(self.running):
            newfile = file_queue.get()
            self.handlers[0].queue.put(newfile)

