# vim:expandtab:smarttab
#A thread that allows us to process files
from __future__ import with_statement

import sys, os

# processing module changes names in 2.6
try:
    import multiprocessing as mp
except ImportError:
    import processing as mp

import time
from amqplib import client_0_8 as amqp
from configuration import config

#The different handlers
from actions import *

class NextAction(object):
    def __init__(self):
        self.NOTHING = 0
        self.TRYAGAIN = 1
        self.FAILURE = 2
        self.AUTHENTICATE = 3

class UploadStatus(object):
    def __init__(self, message=None, nextaction=None, file=None):
        pass

na = NextAction()

class FileUploadThread(object):

    def __init__(self):
        self.running = 1

        self._connection = amqp.Connection(
                host = "localhost:5672",
                userid = "guest",
                password = "guest",
                virtual_host = "/",
                insist = False)
        self._channel = self._connection.channel()
        self._channel.exchange_declare(
                exchange = "fileprocess",
                type = "direct",
                durable = True,
                auto_delete = False)

        self.children = [] # child processes to monitor
        self.handlers = [
            Hasher(),
            PuidGenerator(),
            TagGetter(),
            TagSaver(),
            Transcoder(),
            S3Uploader(),
            DBChecker(),
            BrainzTagger(),
            AmazonCovers(),
            CheckForBadAsin(),
            AmazonASINConvert(),
            DBRecorder(),
            Cleanup()
        ]

        # Set up our chain of handlers
        self.handlers[0].consuming = "start_fileprocessing"
        self._start_child(self.handlers[0])
        for x in xrange(1, len(self.handlers)):
            self.handlers[x].consuming = self.handlers[x-1].message_key
            self._start_child(self.handlers[x])

        # A Special child for cleaning up errors
        cleanup = Cleanup(consuming="cleanup")
        self._start_child(cleanup)

        # GO GO GO! (Monitor our children)
        while True:
            for child in self.children:
                if not child.isAlive():
                    child.start()
            time.sleep(60)


    def _start_child(self, handler):
        process = mp.Process(target = handler.start)
        process.setDaemon(True)
        process.start()
        self.children.append(process)

if __name__ == '__main__':
    print "Starting file upload process"
    f = FileUploadThread()
