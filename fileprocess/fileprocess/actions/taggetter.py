# vim:expandtab:smarttab
import logging
import hashlib, os
import re, copy
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.mp4 import MP4, MP4StreamInfoError
from baseaction import BaseAction
import fileprocess
from fileprocess.processingthread import na

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
        self.ttrack_find = re.compile('([0-9]*)/?([0-9]*)')

    def clean_tags(self, file):
        file = self.update_tracknum(file)
        file = self.scrub_commas(file)
        if not file.get('artist') and file.has_key('composer'):
            file['artist'] = file['composer']
        return file

    def process(self, file):
        """This is rediculously easy with easyid3"""

        if file.has_key('fname'):
            if not os.path.exists(file.get('fname')):
                file = self.clean_tags(file)
                return file
        else:
            file = self.clean_tags(file)
            return file

        try:
            #some mp4s look like mp3s, do it in this order instead
            audio = MP4(file['fname'])
            update_mp4(audio, file)

            file['filetype'] = 'mp4'
        except MP4StreamInfoError:
            try:
                audio = MP3(file['fname'], ID3=EasyID3)
                file['filetype'] = 'mp3'

                # EasyID3 pulls every tag out as a list, which is annoying
                # I join the lists here for ease of processing later.
                for key in audio.keys():
                    if isinstance(audio[key], list):
                        file[key] = ','.join(audio[key])
            except HeaderNotFoundError:
                log.info("A non-mp3 file was uploaded")
                file['msg'] = "File was not an MP3 or MP4"
                file['na'] = na.FAILURE
                self.cleanup(file)
                return False

        # Extra tags that I can figure out
        file = self.clean_tags(file)

        file['duration'] = int(audio.info.length*1000)
        file['bitrate'] = int(audio.info.bitrate)
        file['size'] = os.stat(file['fname'])[os.path.stat.ST_SIZE]
        if file.get('date'):
            file['date'] = file['date'].split('-')[0]

        #audio.delete() #remove the ID3 tags, we don't care for them

        newname = '%s.%s' % (file['fname'], file['filetype'])
        os.rename(file['fname'], newname)
        file['fname'] = newname
        log.debug("Tagged %s: %s", file.get('title'), file)
        return file

    def update_tracknum(self, file):
        tracknumber = file.get('tracknumber')
        if type(tracknumber) in [str, unicode]:
            file['tracknumber'] = self.tracknum_strip.sub('', file['tracknumber'])

            tparts = self.ttrack_find.findall(file['tracknumber'])[0]
            oldtracknum = copy.copy(file['tracknumber'])
            try:
                file['tracknumber'] = int(tparts[0])
                file['totaltracks'] = int(tparts[1])
            except ValueError, e:
                # Sometimes we don't have one of the values we were looking for
                oldtracknum = oldtracknum.split('/')[0]
                if oldtracknum == '':
                    oldtracknum = '0'
                file['tracknumber'] = oldtracknum
        return file

    def scrub_commas(self, file):
        """
        For some reason, mutagen sometimes goes nuts and puts tons of commas in
        the tags. Instead of fixing this, I'm just going to scrub them out for
        now since I don't have a file on me that it does this for --JMT
        """
        for key,tag in file.iteritems():
            if hasattr(tag, 'strip'):
                file[key] = tag.strip(',')
        return file

def update_mp4(mp4obj, tagobj):
    """Extracts easyid3 tags from an MP4 object and puts them into tagobj"""
    valid_keys = [
        ('\xa9alb', 'album'),
        ('\xa9wrt', 'composer'),
        ('\xa9gen', 'genre'),
        ('\xa9day', 'date'),
        #no lyricist field
        ('\xa9nam', 'title'),
        #no version field
        ('\xa9ART', 'artist'),
        #('trkn', 'tracknumber')
        #missing asin, mbalbumartistid, mbalbumid, mbtrackid
    ]

    for key, field_name in valid_keys:
        if mp4obj.has_key(key):
            if isinstance(mp4obj[key], list):
                tagobj[field_name] = ','.join(mp4obj[key])
    
    if mp4obj.has_key('trkn') and len(mp4obj['trkn']) > 0:
        trkn = mp4obj['trkn'][0]
        if type(trkn) == tuple and len(trkn) == 2:
            tagobj['tracknumber'], tagobj['totaltracks'] = trkn
        elif type(trkn) == unicode:
            tagobj['tracknumber'] = trkn
        else:
            log.info('Unknown type of mp4 track number: %s' % trkn)

