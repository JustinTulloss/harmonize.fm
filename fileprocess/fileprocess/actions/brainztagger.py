# -*- coding: utf-8 -*-
# Justin Tulloss
#
# Reworked 04/12/08 to use the picard method of doing things:
#   1. Lookup album
#   2. Try to match track with album
#   3. If it doesn't match, lookup track
#
# Reworked 06/12/2008 to use PUIDs that are generated client-side --JMT
# Added real caching 06/17/2008 --JMT
# Reworked 06/25/08 make it so that it doesn't replace the album name --JMT

from __future__ import with_statement
import logging
import threading
from baseaction import BaseAction
from ..processingthread import na
import time
from musicbrainz2.webservice import (
    Query, 
    TrackFilter, 
    WebServiceError, 
    ReleaseFilter,
    ReleaseIncludes)
from musicbrainz2 import model
from fileprocess.configuration import config
from tag_compare import (
    compare_to_release,
    match_file_to_release,
    match_file_to_track
)

from tag_utils import totaltracks, get_year

log = logging.getLogger(__name__)
CACHE_EXPIRATION = 60*60

class BrainzTagger(BaseAction):
    def __init__(self, *args):
        super(BrainzTagger, self).__init__(args)

        # Keyed by musicbrainz ids
        from fileprocess.processingthread import caches
        self.artistcache = caches.get_cache(
            'brainz.artists',
            expires = CACHE_EXPIRATION
        )
        self.albumcache = caches.get_cache(
            'brainz.albums',
            expires = CACHE_EXPIRATION
        )

        # Keyed by tuple(album, artist, totaltracks)
        self.releasecache = caches.get_cache(
            'brainz.releases',
            expires = CACHE_EXPIRATION
        )

        self.lastquery = 0 #time of last query

    def process(self, file):
        mbquery = Query()

        filter = None
        if not file.has_key('puid'):
            return file # Just keep the tags we have

        if file['puid'] == None:
            return file

        # Query the album and then see if this track belongs
        cachekey = None
        if (file.has_key('artist') or file.has_key('album')):
            cachekey = (
                file.get('album'),
                file.get('artist'),
            )
            if self.releasecache.has_key(cachekey):
                releases = self.releasecache.get(cachekey)
                for release in releases:
                    log.debug("Checking releasecache for %s", cachekey)
                    mbtrack = match_file_to_release(file, release)
                    if mbtrack:
                        if mbtrack.artist:
                            artist = mbtrack.artist
                        else:
                            artist = release.artist
                        log.debug("Release matched! %s on %s by %s",
                            mbtrack.title, release.title, artist.name)
                        return self._cash_out(file, mbtrack, release, artist)

        # Could not match against an existing album, do a file analysis
        log.debug("Could not match %s on %s in the release cache",
            file.get('title'), file.get('album'))
        result = self._find_track(file)
        if not result:
            return file

        # Get info on the album, cache it for future songs
        mbalbumid = result.track.releases[0].id
        if self.albumcache.has_key(mbalbumid):
            album = self.albumcache.get(mbalbumid)
        else:
            include = ReleaseIncludes(
                releaseEvents=True,
                tracks=True,
                artist=True)
            album = self._query_brainz(
                file,
                mbquery.getReleaseById,
                mbalbumid, 
                include = include
            )
            if album == False:
                return file
            self.albumcache[mbalbumid]= album
            log.debug("Inserting things into the releasecache")
            key = (file.get('album'), file.get('artist'))
            if self.releasecache.has_key(key):
                self.releasecache[key].append(album)
            else:
                self.releasecache[key] = [album]

        # Get info on the artist, cache it for future songs
        mbartistid = result.track.artist.id
        if self.artistcache.has_key(mbartistid):
            artist = self.artistcache.get(mbartistid)
        else:
            artist = self._query_brainz(file,mbquery.getArtistById, mbartistid)
            if artist == False:
                return False
            self.artistcache[mbartistid] = artist

        # Fill out the tags. Oh yeah.
        return self._cash_out(file, result.track, album, artist)

    def _cash_out(self, file, track, album, artist):
        file[u'title'] = track.title
        file[u'artist'] = artist.name
        if not file.get('album'):
            file['album'] = album.title
        file[u'duration'] = track.duration #in milliseconds
        year = get_year(album)
        if year:
            file[u'date'] = year
            file[u'year'] = year

        if len(track.releases) > 0:
            file[u'tracknumber'] = track.releases[0].getTracksOffset()+1
        else: 
            file[u'tracknumber'] = album.tracks.index(track) + 1
        file[u'totaltracks'] = len(album.tracks)

        # The musicbrainz ids are urls. I just keep the actual id part
        file[u'mbtrackid'] = track.id.rsplit('/').pop()
        file[u'mbalbumid'] = album.id.rsplit('/').pop()
        file[u'mbartistid'] = artist.id.rsplit('/').pop()
        file[u'asin'] = album.asin #probably a good thing to have

        # Album artist stuff
        try:
            file[u'mbalbumartistid'] = album.artist.id.rsplit('/').pop()
            file[u'albumartist'] = album.artist.name
        except:
            file[u'mbalbumartistid'] = file['mbartistid']
            file[u'albumartist'] = file['artist']

        log.debug('%s successfully tagged by MusicBrainz', track.title)
        return file
        
    def _query_brainz(self, file, callable, *args, **kwargs):
        try:
            sincelast = time.time()-self.lastquery
            if sincelast < 1:
                time.sleep(1-sincelast) #We're only allowed to make 1 request/second
            result = callable(*args, **kwargs)
            self.lastquery = time.time()
            return result
        except WebServiceError, e:
            log.warn(
                "There was a problem with MusicBrainz, bailing on %s: %s", 
                args, e
            ) 
            file['msg'] = "Could not contact tagging service"
            file['na'] = na.TRYAGAIN
            self.cleanup(file)
            return False

    def _find_track(self, file):
        mbquery = Query()

        filter = TrackFilter(puid = file['puid'])
        result = self._query_brainz(file,mbquery.getTracks, filter)
        if not result:
            return False

        if len(result)== 0:
            #Uh oh, nothing found.
            return file

        trackl = []
        trackd = {}
        include = ReleaseIncludes(releaseEvents = True, tracks = True)
        for track in result:
            trackd[track.track.id] = track

            log.debug("Looking up %s with score %s", 
                track.track.title,
                track.score
            )
            release = self._query_brainz(
                file, 
                mbquery.getReleaseById, 
                track.track.releases[0].id,
                include = include
            )
            trackl.append({
                'id': track.track.id,
                'title': track.track.title,
                'album': track.track.releases[0].title,
                'artist': track.track.artist.name,
                'duration': track.track.duration,
                'releaseid': track.track.releases[0].id,
                'tracknumber': track.track.releases[0].getTracksOffset()+1,
                'totaltracks': len(release.tracks),
                'date': get_year(release),
                'types': release.types
            })

        result = match_file_to_track(file, trackl)
        if result:
            return trackd[result['id']]
        else:
            return False
