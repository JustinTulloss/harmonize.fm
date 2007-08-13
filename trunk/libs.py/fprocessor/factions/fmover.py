#A simple file moving module that renames the file
#to its sha1 name in the media directory

from paste.deploy import CONFIG
import sha, os
from fbaseaction import FBaseAction
from shutil import move

READCHUNK = 1024 #1 kb at a time, don't want to stall the system

class FMover(FBaseAction):
    
    def __init__(self):
        super(FMover, self).__init__()
        self.to = CONFIG['app_conf']['media_dir']
        self.frm = CONFIG['app_conf']['upload_dir']
    
    def process(self, file):
        """
        The overridden process function, moves the file and renames it.
        Assumes the file is rewound
        """
        f = open(file, 'rb')
        s = sha.new()
        readbytes = READCHUNK

        while(readbytes):
            readstring = f.read(readbytes)
            s.update(readstring)
            readbytes = len(readstring)

        self.to = os.path.join(self.to, s.hexdigest())
        if not os.path.isabs(file.name):
            self.frm = os.path.join(self.frm, file.name)
        else:
            self.frm = file.name
        try:
            move(self.frm, self.to)
        except IOError:
            os.remove(self.frm) #the file already exists
        return self.to
