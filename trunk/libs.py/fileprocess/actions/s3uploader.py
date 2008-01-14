import S3
from baseaction import BaseAction

AWS_ACCESS_KEY_ID = '17G635SNK33G1Y7NZ2R2'
AWS_SECRET_ACCESS_KEY = 'PHDzFig4NYRJoKKW/FerfhojljL+sbNyYB9bEpHs'

BUCKET = 'music.rubiconmusicplayer.com'

READCHUNK = 1024 *128 #128k at a time, i think that's fair

class S3Uploader(BaseAction):
    def __init__(self):
        super(S3Uploader, self).__init__()
        # TODO:We keep this connection around forever. I'm not sure
        # how to recover if it fails/gets disconnected yet
        self._conn = S3.AWSAuthConnection(
            AWS_ACCESS_KEY_ID, 
            AWS_SECRET_ACCESS_KEY)

    def process(self, file):
        fo = open(file['fname'],'rb')

        data = ''
        readbytes = READCHUNK
        bytes = fo.read(readbytes)
        while(len(bytes)>0):
            data += bytes
            bytes = fo.read(readbytes)
        fo.close()

        response=self._conn.put(BUCKET, file['sha'], data)
        if (response.message == '200 OK'):
            os.remove(file['fname'])
            file['fname'] = '/'.join([self._conn.server, BUCKET, file['sha']])
        else:
            print response.message #need a logging mechanism of sorts

        return file
