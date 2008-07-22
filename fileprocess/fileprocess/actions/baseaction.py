# The mother of all file actions
# Does all the ugly stuff, starts threads, defines queues, eats babies, etc.
from Queue import *
from ..processingthread import na, get_fp
import logging
import threading
import os
log = logging.getLogger(__name__)

class BaseAction(object):

    def __init__(self, cleanup=None, nextaction = None):
        self.queue = Queue()
        self.nextaction = nextaction
        self.cleanup_handler = cleanup
        self._running = 1
        self._thread = threading.Thread(None, self._loop)
        self._thread.setDaemon(True)
        self._thread.start()
    
    def _loop(self):
        while(self._running):
            nf = self.queue.get()
            try:
                nextfile = self.process(nf)
            except Exception, e:
                log.exception(e)
                self.failure(nf)
                nextfile = False

            if nextfile and self.nextaction:
                self.nextaction.put(nextfile)
    
    def stop(self):
        self._running = 0
        if self._thread.isAlive():
            self._thread.join()

    def start(self):
        self._running = 1
        if not self._thread.isAlive():
            self._thread.run()

    def failure(self, file):
        if file.get('failures')>3:
            file['msg'] = "Upload had an unexpected failure"
            file['na']  = na.FAILURE
            self.cleanup(file)
            alert("fileprocess exception", file)
        else:
            if file.has_key('failures'):
                file['failures'] = file['failures']+1
            else:
                file['failures'] = 0
            fp = get_fp()
            if fp:
                fp.process(file)
            else:
                self.cleanup(file)
        
    def cleanup(self, file):
        if self.cleanup_handler != None:
            self.cleanup_handler.queue.put(file)

    def put(self, nf):
        if self.can_skip(nf):
            if self.nextaction != None:
                self.nextaction.put(nf)
        else:
            self.queue.put(nf)

    def can_skip(self, nf):
        """For actions like Transcoder that certain files can skip completely"""
        return False

    def process(self, nf):
        """
        Override this function
        """
        return nf
