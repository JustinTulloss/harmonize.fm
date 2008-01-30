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

        while readbytes>0:
            readstring = f.read(readbytes)
            s.update(readstring)
            readbytes = len(readstring)

        file["new"]=True
        file["sha"]= s.hexdigest()
        to = os.path.join(self.to, file["sha"])
        if not os.path.isabs(f.name):
            frm = os.path.join(self.frm, f.name)
        else:
            frm = f.name
        if (os.path.exists(to)):
            os.remove(frm) #the file already exists
            #TODO: There's a race condition here if two people are
            # uploading the same file at the same time. Tell the 
            # client to try re-uploading
            log.warn('%s already exists, removing', to)
            return False
        else:
            move(frm, to)

        file["fname"] = to
        return file
