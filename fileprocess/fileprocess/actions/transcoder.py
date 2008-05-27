# vim:expandtab:smarttab
import logging, os, fileprocess
import os.path as path
from fileprocess.configuration import config
from baseaction import BaseAction
import guid

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
        if new_file['filetype'] == 'mp3':
            return True
        else: return False

    def process(self, file):
        assert file and len(file)>0

        if file['filetype'] == 'mp3':
            return file
        elif file['filetype'] == 'mp4':
            #This will not work on windows
            if not self.enabled:
                log.info('mp4 file uploaded, but no transcoders available')
                file['msg'] = 'No transcoder available'
                file['na'] = fileprocess.na.FAILURE
                self.cleanup(file)
                return False

            new_fname = path.join(config['media_dir'], guid.generate())

            res = os.system(
               'nice -n +17 faad -q -o - %s | nice -n +17 lame -S -b 128 - %s' %
                                (file['fname'], new_fname))
            if res != 0:
                log.info('Error transcoding mp4 file')
                file['msg'] = 'Transcoding error'
                file['na'] = fileprocess.na.FAILURE
                os.remove(new_fname)
                self.cleanup(file)
                return False
            
            os.remove(file['fname'])
            file['fname'] = new_fname

            return file
        else:
            log.info('Unknown filetype encountered')
            file['msg'] = 'Unknown file encoding'
            file['na'] = fileprocess.na.FAILURE
            self.cleanup(file)
            return False

        
