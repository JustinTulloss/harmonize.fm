import logging
import cPickle as pickle
import os
from .processingthread import na
from baseaction import BaseAction
from fileprocess.configuration import config

log = logging.getLogger(__name__)

class TagSaver(BaseAction):
    def process(self, file):
        """
        Saves off old tags to persistent storage for future reference.
        """
        try:
            tagshelf = open(config['tagshelf'], 'ab')
            pickle.dump(file, tagshelf, 2)
            tagshelf.close()
        except Exception, e:
            log.info("Exception occurred while saving tags: %s", e)

        return file
