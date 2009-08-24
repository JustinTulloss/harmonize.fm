# vim:expandtab:smarttab
#A thread that allows us to process files
from __future__ import with_statement

import sys, os

# processing module changes names in 2.6
try:
    import multiprocessing as mp
except ImportError:
    import processing as mp

import threading

import time
from amqplib import client_0_8 as amqp
from configuration import *
import logging

#The different handlers
from actions import *

log = None

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
            #AmazonCovers(), # Excluded until we include signature in ECS request
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
        process = mp.Process(target = handler.start)
        #process = threading.Thread(group = None, target = handler.start)
        process.setDaemon(True)
        process.start()
        self.children.append(process)

def main():
    # Initialize the config
    global config
    lconfig = base_logging
    if '--production' in sys.argv:
        update_config(production_config)
        lupdate_config(production_logging)
    elif '--live' in sys.argv:
        update_config(production_config)
        update_config(live_config)
        lupdate_config(production_logging)
    else:
        update_config(dev_config)
        lupdate_config(dev_logging)


    # Initialize Logging
    global log
    if '--debug' in sys.argv:
        lconfig['level'] = logging.DEBUG
    logging.basicConfig(**lconfig)
    log = logging.getLogger(__name__)
    handler = lconfig['handler'](*lconfig['handler_args'])
    log.addHandler(handler)

    log.debug('Starting with config: %s and logging %s',
        config, lconfig)

    fp = FileUploadThread()

if __name__ == '__main__':
    print "Starting file upload process"
    main()
