import logging
import hashlib, os
from baseaction import BaseAction
from fileprocess.processingthread import na
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
        if not (file.has_key('usersha') and os.path.exists(file.get('fname'))):
            return file

        # Hash the untagged file
        f = open(file['fname'], 'rb')
        s = hashlib.sha1()
        readbytes = READCHUNK

        while readbytes>0:
            readstring = f.read(readbytes)
            s.update(readstring)
            readbytes = len(readstring)

        file['sha']= s.hexdigest()

        f.close()
        if file['sha'] != file['usersha']:
            log.info("The client's hash %s did not match ours %s, bailing"%
					 (file['usersha'], file['sha']))
            file['msg'] = "Hash mismatch"
            file['na'] = na.TRYAGAIN
            self.failure(file)
            return False

        return file
