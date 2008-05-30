import logging
import S3
import os
from baseaction import BaseAction
import fileprocess
from fileprocess.configuration import config
from fileprocess.processingthread import na

log = logging.getLogger(__name__)

READCHUNK = 1024 *128 #128k at a time, i think that's fair

class S3Uploader(BaseAction):
    """
    This class uploads the file to S3. It's kind of aware of the fact that
    it's at the end of the upload pipeline since it always cleans up, but
    I'm really ok with that for now.
    """
    def process(self, file):
        assert file.has_key('sha') and file.has_key('fname')
        if config['S3.upload'] == False:
            log.warn("Removed %s because S3.upload flag is set to false", 
                file['fname']
            )
            self.cleanup(file)
            return file

        conn = S3.AWSAuthConnection(
            config['S3.accesskey'], 
            config['S3.secret']
        )

        def upload_file():
            try:
                fo = open(file['fname'],'rb')
            except IOError, e:
                file['msg'] = "An error occurred while committing file"
                file['na'] = na.TRYAGAIN
                self.cleanup(file)
                return False

            data = ''
            readbytes = READCHUNK
            bytes = fo.read(readbytes)
            while(len(bytes)>0):
                data += bytes
                bytes = fo.read(readbytes)
            fo.close()

            response=conn.put(config['S3.music_bucket'], file['sha'], data)
            return response

        message = ''
        while message != '200 OK':
            try:
                response = upload_file()
                if response:
                    message = response.message
                else:
                    return False
            except S3.httplib.HTTPException:
                message = 'EXCEPTION'
            
        log.info("%s successfully uploaded to S3", 
            file.get('title', 'Unknown Song'))
        return file
