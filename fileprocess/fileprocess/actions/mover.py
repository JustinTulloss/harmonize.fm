# A simple file moving module that renames the file
# to its sha1 name in the media directory

import logging
import os
import guid
from baseaction import BaseAction
from ..processingthread import na
from fileprocess.configuration import config
from shutil import move

log = logging.getLogger(__name__)

class Mover(BaseAction):
    
    def __init__(self):
        super(Mover, self).__init__()
        self.to = config['media_dir']
        self.frm = config['upload_dir']
    
    def process(self, file):
        """
        The overridden process function, moves the file and renames it.
        Assumes the file is rewound
        """
        if not file.has_key('fname'):
            return file

        log.debug('Moving %s', file['fname'])

        to = os.path.join(self.to, guid.generate())
        if not os.path.isabs(file['fname']):
            frm = os.path.join(self.frm, file['fname'])
        else:
            frm = file['fname']
        if not os.path.exists(frm):
            log.info("Given filename does not exist, bailing")
            file['msg'] = "File does not exist"
            file['na'] = na.FAILURE
            self.cleanup(file)
            return False
            
        move(frm, to)

        file["fname"] = to
        return file
