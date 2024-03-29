#!/usr/bin/env python
# vim:expandtab:smarttab
#A thread that allows us to process files
import sys, os

# processing module changes names in 2.6 (FUTURE READY!!!)
try:
    import multiprocessing as mp
except ImportError:
    import processing as mp

import threading

import time
from amqplib import client_0_8 as amqp
from configuration import *
import logging

log = logging.getLogger(__name__)

#The different handlers
from actions import *

class FileProcessor(object):

    def __init__(self):
        self.running = 1

        self._connection = amqp.Connection(
                host = "localhost:5672",
                userid = "guest",
                password = "guest",
                virtual_host = config['amqp_vhost'],
                insist = False)
        self._channel = self._connection.channel()
        self._channel.exchange_declare(
                exchange = 'fileprocess',
                type = "direct",
                durable = True,
                auto_delete = False)

        self.children = [] # child processes to monitor
        self.handlers = [
            Hasher(),
            PuidGenerator(),
            TagGetter(),
            #TagSaver(), # Need to come up with a better way of doing this.
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

        # GO GO GO!
        while True:
            time.sleep(600)


    def _start_child(self, handler):
        log.info('Starting %s' % handler)
        #process = mp.Process(target = handler.start)
        process = threading.Thread(group = None, target = handler.start)
        process.setDaemon(True)
        process.start()
        self.children.append(process)
