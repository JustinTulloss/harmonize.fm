from __future__ import with_statement
import logging
import threading
from baseaction import BaseAction
import fileprocess
from musicbrainz2.webservice import Query, TrackFilter, WebServiceError, ReleaseIncludes

log = logging.getLogger(__name__)

class BrainzTagger(BaseAction):
    def __init__(self, *args):
        super(BrainzTagger, self).__init__(args)
        self.artistcache = dict()
        self.albumcache = dict()
        self.cachelock = threading.Lock()

    def process(self, file):
        mbquery = Query()

        # The implementation of the MB Library sucks, so I can't access
        # the filter in a normal way after I construct it. So I have to
        # construct it very carefully. Dynamic my ass. These are exactly
        # the types of things one should never see in Python --JMT
        filter = None
        if not file.has_key('title'):
            #TODO: Analyze and try to do a PUID match.
            log.info('Analysis needs to be done on %s',file.get('fname'))
            fileprocess.UploadStatus("File had no tags", fileprocess.na.FAILURE, file)
            return False

        arglist = [
            ['title', 'releaseTitle'],
            ['title', 'artistName'],
            ['title', 'artistName', 'releaseTitle']
        ]
        args = {
            'title': file.get('title'), 
            'artistName': file.get('artist'),
            'releaseTitle': file.get('album')
        }
        result = []
        while len(result) == 0 and len(arglist)>0:
            fargs = {}
            for arg in arglist.pop():
                fargs[arg] = args[arg]
            filter = TrackFilter(**fargs)
            try:
                result = mbquery.getTracks(filter)
            except WebServiceError, e:
                log.warn(
                    "There was a problem with MusicBrainz, bailing on %s: %s", 
                    args, e
                ) 
                fileprocess.UploadStatus("Could not contact tagging service", 
                    fileprocess.na.TRYAGAIN, file)
                return False

        if len(result)== 0:
            #Uh oh, nothing found. TODO:What now??
            log.info('Brainz match not found for %s',file.get('title'))
            fileprocess.UploadStatus("No tags found for file", fileprocess.na.FAILURE, file)
            return False

        if len(result)>1:
            for r in result:
                if r.score < 80:
                    result.remove(r)
            if len(result) == 0:
                log.info('Brainz match not adequate for %s',file.get('title'))
                fileprocess.UploadStatus("Could not find accurate tags for file", 
                    fileprocess.na.FAILURE, file)
                return False
            if len(result)>1:
                #TODO: Run a PUID analysis
                log.info("Found multiple versions of %s", file.get('title'))
                fileprocess.UploadStatus("Too many versions of tags found", fileprocess.na.FAILURE, file)
                return False

        result = result[0]

        # Get info on the album, cache it for future songs
        mbalbumid = result.track.releases[0].id
        if self.albumcache.has_key(mbalbumid):
            album = self.albumcache[mbalbumid]
        else:
            with self.cachelock:
                include = ReleaseIncludes(releaseEvents=True, tracks=True)
                album = mbquery.getReleaseById(mbalbumid, include=include)
                self.albumcache[mbalbumid]= album

        # Get info on the artist, cache it for future songs
        mbartistid = result.track.artist.id
        if self.artistcache.has_key(mbartistid):
            artist = self.artistcache[mbartistid]
        else:
            with self.cachelock:
                artist = mbquery.getArtistById(mbartistid)
                self.artistcache[mbartistid] = artist

        # Fill out the tags. Oh yeah.
        file['title'] = result.track.title
        file['artist'] = result.track.artist.name
        file['artistsort'] = artist.sortName
        file['album'] = album.title
        file['length'] = result.track.duration #in milliseconds
        try:
            file['year'] = album.getEarliestReleaseDate().split('-')[0]
        except:
            pass
        file['tracknumber'] = result.track.releases[0].getTracksOffset()+1
        file['totaltracks'] = len(album.tracks)

        # The musicbrainz ids are urls. I just keep the actual id part
        file['mbtrackid'] = result.track.id.rsplit('/').pop()
        file['mbalbumid'] = album.id.rsplit('/').pop()
        file['mbartistid'] = result.track.artist.id.rsplit('/').pop()
        file['asin'] = album.asin #probably a good thing to have ;)

        log.debug('%s successfully tagged by MusicBrainz', file.get('title'))

        return file
