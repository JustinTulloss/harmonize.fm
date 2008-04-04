import logging
import hashlib, os
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3, HeaderNotFoundError
from baseaction import BaseAction
import fileprocess

log = logging.getLogger(__name__)

class TagGetter(BaseAction):
    """
    This class gets tags out of a file. It's takes the tags from the uploaded 
    file, which is pretty dangerous. We'll move it to a hopefully more reliable 
    musicbrainz based system when somebody codes that.
    """

    def process(self, file):
        """This is rediculously easy with easyid3"""

        try:
            audio = MP3(file['fname'], ID3=EasyID3)
        except HeaderNotFoundError:
            log.info("A non-mp3 file was uploaded")
            file['msg'] = "File was not an MP3"
            file['na'] = fileprocess.na.FAILURE
            self.cleanup(file)
            return False

        file.update(audio)
        # EasyID3 pulls every tag out as a list, which is kind of annoying.
        # I join the lists here for ease of processing later.
        for k in audio.keys():
            file[k] = ','.join(file[k])

        audio.delete() #remove the ID3 tags, we don't care for them

        log.debug("Tagged %s", file.get('title'))
        return file
