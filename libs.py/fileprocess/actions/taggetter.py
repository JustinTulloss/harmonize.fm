import logging
import hashlib, os
import re, copy
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

    def __init__(self, **kwargs):
        super(TagGetter, self).__init__(**kwargs)

        self.tracknum_strip = re.compile('[^0-9/]')
        self.ttrack_find = re.compile('([0-9])*/?([0-9])*')

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

        # Extra tags that I can figure out
        tracknumber = file.get('tracknumber')
        if tracknumber:
            file['tracknumber'] = self.tracknum_strip.sub('', file['tracknumber'])

            tparts = self.ttrack_find.findall(file['tracknumber'])[0]
            oldtracknum = copy.copy(file['tracknumber'])
            try:
                file['tracknumber'] = int(tparts[0])
                file['tracknumber'] = int(tparts[1])
            except ValueError, e:
                # Sometimes we don't have one of the values we were looking for
                file['tracknumber'] = oldtracknum

        file['duration'] = int(audio.info.length*1000)

        audio.delete() #remove the ID3 tags, we don't care for them

        log.debug("Tagged %s", file.get('title'))
        return file
