# -*- coding: utf-8 -*-
# Justin Tulloss
#
# Reworked 04/12/08 to use the picard method of doing things:
#   1. Lookup album
#   2. Try to match track with album
#   3. If it doesn't match, lookup track

from __future__ import with_statement
import logging
import threading
import pdb
from baseaction import BaseAction
import fileprocess
import time
from musicbrainz2.webservice import (
    Query, 
    TrackFilter, 
    WebServiceError, 
    ReleaseFilter,
    ReleaseIncludes)
from musicbrainz2 import model
from pylons import config
from picard.similarity import similarity2

log = logging.getLogger(__name__)

class BrainzTagger(BaseAction):
    __weights = [
        ('title', 22),
        ('artist', 6),
        ('album', 12),
        ('tracknumber', 6),
        ('totaltracks', 5),
    ]

    def __init__(self, *args):
        super(BrainzTagger, self).__init__(args)

        # Keyed by musicbrainz ids
        self.artistcache = dict()
        self.albumcache = dict()

        # Keyed by tuple(album, artist, totaltracks)
        self.releasecache = dict()

        self.lastquery = 0 #time of last query

    def process(self, file):
        mbquery = Query()

        filter = None
        if not file.has_key('title'):
            #TODO: Analyze and try to do a PUID match.
            log.info('No title, analysis needs to be done on %s',
                file.get('fname'))
            file['msg'] = "File does not have tags"
            file['na'] = fileprocess.na.FAILURE
            self.cleanup(file)
            return False

        # Query the album and then see if this track belongs
        if (file.has_key('artist') and file.has_key('album')):
            cachekey = (
                file['album'],
                file['artist'],
                self._totaltracks(file)
            )
            release = self.releasecache.get(cachekey)
            if release:
                mbtrack = self._match_file_to_release(file, release)
                if mbtrack:
                    return self._cash_out(file, mbtrack, release, release.artist)
            else:
                release = self._find_album(file, cachekey)
                if release:
                    self.releasecache[cachekey] = release
                    mbtrack = self._match_file_to_release(file, release)
                    if mbtrack != False:
                        return self._cash_out(file, mbtrack, release, release.artist)

        # Could not match against an existing album, do a file analysis
        result = self._find_track(file)
        if not result:
            return False


        # Get info on the album, cache it for future songs
        mbalbumid = result.track.releases[0].id
        if self.albumcache.has_key(mbalbumid):
            album = self.albumcache[mbalbumid]
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
                return False
            self.albumcache[mbalbumid]= album

        # Get info on the artist, cache it for future songs
        mbartistid = result.track.artist.id
        if self.artistcache.has_key(mbartistid):
            artist = self.artistcache[mbartistid]
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
        file[u'artistsort'] = artist.sortName
        file[u'album'] = album.title
        file[u'duration'] = track.duration #in milliseconds
        year = self._year(album)
        if year:
            file[u'date'] = year
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

        log.debug('%s successfully tagged by MusicBrainz', track.title)
        return file
        
    def _weed(self, results, threshold):
        for r in results:
            if r.score < threshold:
                results.remove(r)
        return results

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
            pdb.set_trace()
            file['msg'] = "Could not contact tagging service"
            file['na'] = fileprocess.na.TRYAGAIN
            self.cleanup(file)
            return False

    def _totaltracks(self, file):
        if file.get('totaltracks'):
            return int(file.get('totaltracks'))
        if file.get('tracknumber'):
            if str(file.get('tracknumber')).find('/')>=0:
                return int(str(file.get('tracknumber')).rpartition('/')[2])

    def _year(self, release):
        try:
            return release.getEarliestReleaseDate().split('-')[0]
        except:
            return None
    
    def _find_album(self, file, cachekey):
        filter = ReleaseFilter(
            title = cachekey[0],
            artist = cachekey[1],
            count = cachekey[2]
        )
        mbquery = Query()
        releases = self._query_brainz(file, mbquery.getReleases, filter)
        include = ReleaseIncludes(tracks=True, artist=True, releaseEvents=True)
        matches = []
        for release in releases:
            release = self._query_brainz(
                file, 
                mbquery.getReleaseById,
                release.release.id, 
                include
            )
            mtuple = (self._compare_to_release(file, release), release)
            matches.append(mtuple)
        pdb.set_trace()
        if len(matches) <= 0:
            return False

        matches.sort(reverse = True)
        log.debug("Release Matches: %r", matches)
        
        if matches[0][0] > config.get('brainz.album_threshold', .8):
            return release

        return False
    
    def _find_track(self, file):
        mbquery = Query()

        # This defines the order we'll do queries (params from bottom to top)
        arglist = [
            ('title', 'release'),
            ('title', 'artist'),
            ('title', 'artist', 'release'),
            ('title', 'release', 'releasetype'),
            ('title', 'artist',  'releasetype'),
            ('title', 'artist', 'release', 'releasetype')
        ]
        # This defines the value of the above parameters
        args = {
            'title': file.get('title'), 
            'artist': file.get('artist'),
            'release': file.get('album'),
            'releasetype': 'Album',
        }
        result = []
        # The implementation of the MB Library sucks, so I can't access
        # the filter in a normal way after I construct it. So I have to
        # construct it very carefully. Dynamic my ass. These are exactly
        # the types of things one should never see in Python --JMT
        while len(result) == 0 and len(arglist)>0:
            fargs = {}
            for arg in arglist.pop():
                fargs[arg] = args[arg]
            filter = TrackFilter(**fargs)
            log.debug("querying brainz for %s", fargs)
            result = self._query_brainz(file,mbquery.getTracks,filter)
            if result == False:
                return False

        if len(result)== 0:
            #Uh oh, nothing found. TODO:What now??
            log.info('Brainz match not found for %s',file.get('title'))
            file['msg'] = "No tags found for file"
            file['na'] = fileprocess.na.FAILURE
            self.cleanup(file)
            return False

        pdb.set_trace()
        trackl = []
        trackd = {}
        for track in result:
            trackd[track.track.id] = track
            trackl.append({
                'id': track.track.id,
                'title': track.track.title,
                'album': track.track.releases[0].title,
                'artist': track.track.artist.name,
                'duration': track.track.duration,
                'tracknumber': track.track.releases[0].getTracksOffset()+1,
                'totaltracks': track.track.releases[0].tracksCount,
            })

        result = self._match_file_to_track(file, trackl)
        if result:
            return trackd[result['id']]
        else:
            self.cleanup(file)
            return False

    """
    The below functions were stolen from picard, with slight modifications

     Picard, the next-generation MusicBrainz tagger
     Copyright (C) 2004 Robert Kaye
     Copyright (C) 2006 Lukáš Lalinský
     Copyright (C) 2008 Justin Tulloss
    
     This program is free software; you can redistribute it and/or
     modify it under the terms of the GNU General Public License
     as published by the Free Software Foundation; either version 2
     of the License, or (at your option) any later version.
    
     This program is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.

     You should have received a copy of the GNU General Public License
     along with this program; if not, write to the Free Software
     Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
    """

    def _compare_to_release(self, file, release):
        """
        Compare cluster metadata to a MusicBrainz release.

        Weigths:
          * title                = 12
          * artist name          = 6
          * number of tracks     = 5
          * year of release      = 4

        TODO:
          * prioritize official albums over compilations (optional?)
        """
        total = 0.0

        a = file['album']
        b = release.title
        if a and b:
            total += similarity2(a, b) * 17.0 / 27.0

        a = file['artist']
        b = release.artist.name
        if a and b:
            total += similarity2(a, b) * 6.0 / 27.0

        a = file['date']
        b = self._year(release)
        if a and b:
            total += 1.0-abs(cmp(a, b)) * 4.0 / 27.0

        a = self._totaltracks(file)
        b = len(release.tracks)
        if a > b:
            score = 0.0
        elif a < b:
            score = 0.3
        else:
            score = 1.0
        total += score * 5.0 / 27.0

        return total

    def _match_file_to_release(self, file, release):
        """Match files on tracks on this album, based on metadata similarity."""
        trackl = []
        trackd = {}
        for track in release.tracks:
            trackd[track.id] = track
            trackl.append({
                'id': track.id,
                'title': track.title,
                'album': release.title,
                'artist': release.artist.name,
                'duration': track.duration,
                'tracknumber': release.tracks.index(track) + 1,
                'totaltracks': len(release.tracks),
                'date': self._year(release)
            })
            
        result = self._match_file_to_track(file, trackl)
        if result:
            result = trackd[result['id']]
        return result

    def _match_file_to_track(self, file, tracks):
        matches = []
        for track in tracks:
            if file.get('mbtrackid') == track['id']:
                matches.append((2.0, track))
                break
            sim = self._compare_meta(file, track)
            matches.append((sim, track))

        if len(matches) <= 0:
            return False

        matches.sort(reverse=True)
        log.debug('Track matches: %r', matches)

        if matches[0][0] > config.get('brainz.track_threshold', .5):
            return matches[0][1]
        return False

    def _compare_meta(self, file, track):
        """
        Compare file metadata to a MusicBrainz track.

        Weigths:
          * title                = 13
          * artist name          = 4
          * release name         = 5
          * length               = 10
          * number of tracks     = 3
          * release data         = 3
          * track placement      = 5

        """
        total = 0.0
        parts = []

        a = file.get('title')
        b = track.get('title')
        if a and b:
            parts.append((similarity2(a, b), 13))
            total += 13

        a = file.get('artist')
        b = track.get('artist')
        if a and b:
            parts.append((similarity2(a, b), 4))
            total += 4

        a = file.get('album')
        b = track.get('album')
        if a and b:
            parts.append((similarity2(a, b), 5))
            total += 5

        a = file.get('date')
        b = track.get('date')
        if a and b:
            score = 1.0 - abs(cmp(a,b))
            parts.append((score, 3))
            total += 3

        a = file.get('tracknumber')
        b = track.get('tracknumber')
        if a and b:
            a = int(a)
            b = int(b)
            score = 1.0 - abs(cmp(a,b))
            parts.append((score, 5))
            total += 5

        a = file.get('duration')
        b = track.get('duration')
        if a and b:
            score = 1.0 - min(abs(a - b), 30000) / 30000.0
            parts.append((score, 10))
            total += 10

        a = file.get('totaltracks')
        b = track.get('totaltracks')
        if a and b:
            a = int(a)
            b = int(b)
            try:
                if a > b:
                    score = 0.0
                elif a < b:
                    score = 0.3
                else:
                    score = 1.0
                parts.append((score, 4))
                total += 4
            except ValueError:
                pass

        return reduce(lambda x, y: x + y[0] * y[1] / total, parts, 0.0)
