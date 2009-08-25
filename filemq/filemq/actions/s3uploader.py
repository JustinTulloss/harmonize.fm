import logging
import S3
import os
from baseaction import BaseAction
from filemq.configuration import config
from nextaction import na
from socket import sslerror
from httplib import error

log = logging.getLogger(__name__)

READCHUNK = 1024 *128 #128k at a time, i think that's fair

class S3Uploader(BaseAction):
    """
    This class uploads the file to S3. It's kind of aware of the fact that
    it's at the end of the upload pipeline since it always cleans up, but
    I'm really ok with that for now.
    """
    def process(self, file):
        if not (file.has_key('sha') and file.has_key('fname')):
            return file

        if config['S3.upload'] == False:
            log.warn("Not uploading %s because S3.upload flag is set to false", 
                file['fname']
            )
            return file

        conn = S3.AWSAuthConnection(
            config['S3.accesskey'], 
            config['S3.secret']
        )

        # Check to see if this file already exists
        try:
            exists = conn.list_bucket(config['S3.music_bucket'],
                {'prefix': file['sha']}).entries
            if exists:
                return file
        except error, e:
            log.warn("could not check for %s: %s", file['sha'], e)

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

            try:
                response=conn.put(config['S3.music_bucket'], file['sha'], data)
            except sslerror, e:
                log.info("SSL error uploading %s, trying again: %s",
                    file['title'], e)
            return response

        message = ''
        while message != '200 OK':
            try:
                response = upload_file()
                if response:
                    if hasattr(response, 'message'):
                        message = response.message
                    else:
                        message = 'tryingagain'
                else:
                    return False
            except S3.httplib.HTTPException:
                message = 'EXCEPTION'
            
        log.info("%s successfully uploaded to S3", 
            file.get('title', 'Unknown Song'))
        return file
