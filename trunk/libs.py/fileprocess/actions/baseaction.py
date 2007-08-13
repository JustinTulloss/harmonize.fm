# The mother of all file actions
# Does all the ugly stuff, starts threads, defines queues, eats babies, etc.

from Queue import *
import threading

class BaseAction(object):
    def __init__(self):
        self.queue = Queue()
        self.nextqueue = None
        self._running = 1
        self._thread=threading.Thread(None, self._loop)
        self._thread.start()

    
    def _loop(self):
        while(self._running): #praying that reading this is atomic
            nf = self.queue.get()
            nf.seek(0)
            nextfile = self.process(nf)
            if self.nextqueue != None:
                self.nextqueue.put(nextfile)
    
    def stop(self):
        self._running = 0
        if self._thread.isAlive():
            self._thread.join()

    def start(self):
        self._running = 1
        if not self._thread.isAlive():
            self._thread.run()

    def process(self, nf):
        """
        Override this function
        """
        return nf
