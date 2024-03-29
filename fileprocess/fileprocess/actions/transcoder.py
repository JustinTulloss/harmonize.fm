# vim:expandtab:smarttab
import logging, os, fileprocess
import os.path as path
from fileprocess.configuration import config
from fileprocess.processingthread import na
from baseaction import BaseAction
import guid
from hashlib import sha1

log = logging.getLogger(__name__)

class Transcoder(BaseAction):
    """
    This class converts a file from mp4 to mp3 if its file['filetype'] is 
    mp4. It will name the new file <hash>.mp3 and remove the original file
    """

    def __init__(self, **kwargs):
        super(Transcoder, self).__init__(**kwargs)

        self.enabled = os.system(
                    'which faad 1> /dev/null 2> /dev/null'
                    +'&& which lame 1> /dev/null 2> /dev/null') == 0

    def can_skip(self, new_file):
        if not new_file.has_key('filetype'):
            return True
        if new_file['filetype'] == 'mp3':
            return True
        else: return False

    def process(self, file):
        assert file and len(file)>0

        if not file.has_key('filetype'):
            return file

        if file['filetype'] == 'mp3':
            return file
        elif file['filetype'] == 'mp4':
            #This will not work on windows
            if not self.enabled:
                log.info('mp4 file uploaded, but no transcoders available')
                file['msg'] = 'No transcoder available'
                file['na'] = na.FAILURE
                self.cleanup(file)
                return False

            new_fname = \
                path.join(config['upload_dir'], file['fbid'], guid.generate())

            res = os.system(
               'nice -n +17 faad -q -o - %s 2>/dev/null | nice -n +17 lame --quiet -b 128 - %s' %
                                (file['fname'], new_fname))
            if res != 0:
                log.info('Error transcoding mp4 file')
                file['msg'] = 'Transcoding error'
                file['na'] = na.FAILURE
                if os.path.exists(new_fname):
                    os.remove(new_fname)
                self.cleanup(file)
                return False
            
            os.remove(file['fname'])
            file['fname'] = new_fname

            new_sha = sha1(open(new_fname, 'rb').read()).hexdigest()
            new_fname = path.join(config['upload_dir'], file['fbid'], new_sha)
            try:
                os.rename(file['fname'], new_fname)
            except OSError:
                self.cleanup(file)
                return False

            file['fname'] = new_fname
            file['usersha'] = new_sha

            return file
        else:
            log.info('Unknown filetype encountered')
            file['msg'] = 'Unknown file encoding'
            file['na'] = na.FAILURE
            self.cleanup(file)
            return False

        
