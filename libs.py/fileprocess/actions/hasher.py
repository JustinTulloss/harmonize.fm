import logging
import hashlib, os
from baseaction import BaseAction
import fileprocess

log = logging.getLogger(__name__)
READCHUNK = 1024 * 10 #10 kb at a time, don't want to stall the system

class Hasher(BaseAction):
    """
    This action hashes the file, which is important for figuring out if we have
    it already or not. It also compares the hash it gets with the hash the user
    claimed it had. This ensures that the file was completely and correctly 
    uploaded.
    """

    def process(self, file):
        assert file.has_key('usersha')

        # Hash the untagged file
        f = open(file['fname'], 'rb')
        s = hashlib.sha1()
        readbytes = READCHUNK

        while readbytes>0:
            readstring = f.read(readbytes)
            s.update(readstring)
            readbytes = len(readstring)

        file['sha']= s.hexdigest()

        if file['sha'] != file['usersha']:
            log.info("The client's hash %s did not match ours %s, bailing" %
					 (file['sha'], file['usersha']))
            file['msg'] = "Hash mismatch"
            file['na'] = fileprocess.na.TRYAGAIN
            self.cleanup(file)
            return False

        return file
