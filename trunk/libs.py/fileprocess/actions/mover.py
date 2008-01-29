#A simple file moving module that renames the file
#to its sha1 name in the media directory

import logging
from pylons import config
import sha, os
from baseaction import BaseAction
from shutil import move

log = logging.getLogger(__name__)

READCHUNK = 1024 #1 kb at a time, don't want to stall the system

class Mover(BaseAction):
    
    def __init__(self):
        super(Mover, self).__init__()
        self.to = config['app_conf']['media_dir']
        self.frm = config['app_conf']['upload_dir']
    
    def process(self, file):
        """
        The overridden process function, moves the file and renames it.
        Assumes the file is rewound
        """
        log.debug('Moving %s', file['fname'])
        f = open(file["fname"], 'rb')
        s = sha.new()
        readbytes = READCHUNK

        while(readbytes):
            readstring = f.read(readbytes)
            s.update(readstring)
            readbytes = len(readstring)

        file["new"]=True
        file["sha"]= s.hexdigest()
        self.to = os.path.join(self.to, file["sha"])
        if not os.path.isabs(f.name):
            self.frm = os.path.join(self.frm, file.name)
        else:
            self.frm = f.name
        if (os.path.exists(self.to)):
            os.remove(self.frm) #the file already exists
            file["new"] = False
        else:
            move(self.frm, self.to)

        file["fname"] = self.to
        return file
