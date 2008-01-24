import logging
from mutagen.easyid3 import EasyID3
from baseaction import BaseAction

log = logging.getLogger(__name__)

class TagGetter(BaseAction):
    """
    This class gets tags out of a file. It's takes the tags from the uploaded file,
    which is pretty dangerous. We'll move it to a hopefully more reliable 
    musicbrainz based system when somebody codes that.
    """
    def process(self, file):
        """This is rediculously easy with easyid3"""
        #if file["new"] == False:
        #    return file

        audio = EasyID3(file["fname"])
        comma = ','
        file.update(audio)
        #EasyID3 pulls every tag out as a list, which is kind of annoying.
        #I join the lists here for ease of processing later.
        for k in audio.keys():
            file[k] = comma.join(file[k])

        log.debug("File object tagged: " + str(file))
        return file
