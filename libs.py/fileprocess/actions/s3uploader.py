import logging
import S3
import os
from baseaction import BaseAction
import fileprocess
from pylons import config

log = logging.getLogger(__name__)

READCHUNK = 1024 *128 #128k at a time, i think that's fair

class S3Uploader(BaseAction):
    def process(self, file):
        if config['S3.upload'] == 'false':
            log.warn("Removed %s because S3.upload flag is set to false", 
                file['fname']
            )
            self.cleanup(file)
            return False

        conn = S3.AWSAuthConnection(
            config['S3.accesskey'], 
            config['S3.secret']
        )
        fo = open(file['fname'],'rb')

        data = ''
        readbytes = READCHUNK
        bytes = fo.read(readbytes)
        while(len(bytes)>0):
            data += bytes
            bytes = fo.read(readbytes)
        fo.close()

        response=conn.put(config['S3.music_bucket'], file['sha'], data)
        if (response.message == '200 OK'):
            os.remove(file['fname'])
            file['fname'] = '/'.join([
                conn.server, 
                config['S3.music_bucket'], 
                file['sha']
            ])
            log.info("%s successfully uploaded to S3", file['title'])
        else:
            log.error(response.message)
            file['msg'] = "Could not save file"
            file['na'] = fileprocess.na.TRYAGAIN
            self.cleanup(file)
            return False

        self.cleanup(file)
        return False
