import logging
from baseaction import BaseAction
from musicbrainz2.webservice import Query, TrackFilter, WebServiceError, ReleaseIncludes

log = logging.getLogger(__name__)

class BrainzTagger(BaseAction):
    def __init__(self):
        super(BrainzTagger, self).__init__()

    def process(self, file):
        mbquery = Query()
        # The implementation of the MB Library sucks, so I can't access
        # the filter in a normal way after I construct it. So I have to
        # construct it very carefully. Dynamic my ass. These are exactly
        # the types of things one should never see in Python --JMT
        filter = None
        if file.has_key('title') and \
            file.has_key('artist') and \
            file.has_key('album'):
            filter = TrackFilter(
                title = file['title'],
                artistName = file['artist'],
                releaseTitle = file['album'],
                limit = 1
            )
        elif file.has_key('title') and file.has_key('artist'):
            filter = TrackFilter(
                title = file['title'],
                artistName = file['artist'],
                limit = 1
            )
        elif file.has_key('title') and file.has_key('album'):
            filter = TrackFilter(
                title = file['title'],
                releaseTitle = file['album']
            )
        elif file.has_key('title'):
            filter = TrackFilter(title = file['title'], limit=1)
        else: #TODO: Analyze and try to do a PUID match.
            log.info('Analysis needs to be done on %s',file['fname'])
            return file

        result = mbquery.getTracks(filter)
        if len(result)== 0:
            #Uh oh, nothing found. TODO:What now??
            log.info('Brainz match not found for %s',file['fname'])
            return file
        result = result[0] #We just care about the best result
        if result.score < 80: #Not a sure match, let's just keep ours
            log.info('Brainz match not adequate for %s',file['fname'])
            return file

        # Get info on the album (TODO:Cache some albums)
        include = ReleaseIncludes(releaseEvents=True, tracks=True)
        album = mbquery.getReleaseById(result.track.releases[0].id, include=include)

        # Get info on the artist (TODO: Cache some artists)
        artist = mbquery.getArtistById(result.track.artist.id)

        # Fill out the tags. Oh yeah.
        file['title'] = result.track.title
        file['artist'] = result.track.artist.name
        file['artistsort'] = artist.sortName
        file['album'] = album.title
        file['length'] = result.track.duration #in seconds. Perfect.
        file['year'] = album.getEarliestReleaseDate().split('-')[0]
        file['tracknumber'] = result.track.releases[0].getTracksOffset()+1
        file['totaltracks'] = len(album.tracks)
        file['mbtrackid'] = result.track.id
        file['mbalbumid'] = album.id
        file['mbartistid'] = result.track.artist.id
        file['asin'] = album.asin #probably a good thing to have ;)

        log.debug('%s successfully tagged by MusicBrainz: %s', file['title'], file)

        return file
