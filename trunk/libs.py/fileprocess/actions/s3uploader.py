import logging
import S3
import os
from baseaction import BaseAction

log = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = '17G635SNK33G1Y7NZ2R2'
AWS_SECRET_ACCESS_KEY = 'PHDzFig4NYRJoKKW/FerfhojljL+sbNyYB9bEpHs'

BUCKET = 'music.rubiconmusicplayer.com'

READCHUNK = 1024 *128 #128k at a time, i think that's fair

class S3Uploader(BaseAction):
    def process(self, file):
        conn = S3.AWSAuthConnection(
            AWS_ACCESS_KEY_ID, 
            AWS_SECRET_ACCESS_KEY)
        fo = open(file['fname'],'rb')

        data = ''
        readbytes = READCHUNK
        bytes = fo.read(readbytes)
        while(len(bytes)>0):
            data += bytes
            bytes = fo.read(readbytes)
        fo.close()

        response=conn.put(BUCKET, file['sha'], data)
        if (response.message == '200 OK'):
            os.remove(file['fname'])
            file['fname'] = '/'.join([conn.server, BUCKET, file['sha']])
            log.debug("%s successfully uploaded to S3", file['title'])
        else:
            log.error(response.message)

        return file
