import logging
from baseaction import BaseAction
import os
from nextaction import na

log = logging.getLogger(__name__)

class Cleanup(BaseAction):
    """
    A special file action that is invoked when a file needs to be cleaned up.
    Unlike the other actions, this one doesn't return its file. This is a 
    terminal action.
    """
    def process(self, file):
        log.debug('Cleanup %s:%s', file.get('msg'), file.get('na'))

        if file.get('fname'):
            if os.path.exists(file['fname']):
                log.debug('Removing %s:%s', file.get('title'), file.get('fname'))
                os.remove(file['fname'])
