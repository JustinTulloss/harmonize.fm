from mutagen.easyid3 import EasyID3
from baseaction import BaseAction

class TagGetter(BaseAction):
    """
    This class gets tags out of a file. It's takes the tags from the uploaded file,
    which is pretty dangerous. We'll move it to a hopefully more reliable 
    musicbrainz based system when somebody codes that.
    """
    def process(self, file):
        """This is rediculously easy with easyid3"""
        audio = EasyID3(file["fname"])
        file.update(audio)
        comma = ', '
        for k in file.keys():
            file[k] = comma.join(file[k])
        return file
