import logging
from baseaction import BaseAction
import os
from ..processingthread import UploadStatus, na

log = logging.getLogger(__name__)

class Cleanup(BaseAction):
    """
    A special file action that is invoked when a file needs to be cleaned up.
    Unlike the other actions, this one doesn't return its file. This is a 
    terminal action.
    """
    def process(self, file):
        us = UploadStatus(
            file.get('msg', "File Successfully Uploaded"),
            file.get('na', na.NOTHING),
            file
        )
        log.debug('Cleanup %s:%s', file.get('msg'), file.get('na'))

        if os.path.exists(file.get('fname')):
            log.debug('Removing %s:%s', file.get('title'), file.get('fname'))
            os.remove(file['fname'])
