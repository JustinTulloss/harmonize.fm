#A simple file moving module that renames the file
#to its sha1 name in the media directory

import logging
from pylons import config
import os
import guid
from baseaction import BaseAction
import fileprocess
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
        log.debug('Moving %s', file['fname'])

        to = os.path.join(self.to, guid.generate())
        if not os.path.isabs(file['fname']):
            frm = os.path.join(self.frm, file['fname'])
        else:
            frm = file['fname']
        if not os.path.exists(frm):
            file['msg'] = "An Error occurred while processing file"
            file['na'] = fileprocess.na.TRYAGAIN
            self.cleanup(file)
            return False
        move(frm, to)

        file["fname"] = to
        return file
