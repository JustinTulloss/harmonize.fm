# -*- coding: utf-8 -*-
"""
The below functions were stolen from picard, with modifications

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

import logging
from tag_utils import get_year, totaltracks
from picard.similarity import similarity2
from musicbrainz2.webservice import Release

log = logging.getLogger(__name__)

TRACK_THRESHOLD = .70
def compare_to_release(file, release):
    """
    Compare cluster metadata to a MusicBrainz release.
    
    Weigths:
      * title                = 12
      * artist name          = 6
      * number of tracks     = 5
      * year of release      = 4
      * type is album        = 3
      * album is official    = 3
      * num of release events= 2

    """
    total = 0.0

    a = file['album']
    b = release.title
    if a and b:
        total += similarity2(a, b) * 17.0 / 33.0

    a = file['artist']
    b = release.artist.name
    if a and b:
        total += similarity2(a, b) * 6.0 / 33.0

    a = file.get('date')
    b = get_year(release)
    if a and b:
        total += 1.0-abs(cmp(a, b)) * 4.0 / 33.0

    a = totaltracks(file)
    b = len(release.tracks)
    if a > b:
        score = 0.0
    elif a < b:
        score = 0.3
    else:
        score = 1.0
    total += score * 5.0 / 33.0

    if release.TYPE_OFFICIAL in release.types:
        total += 3.0/33.0

    if release.TYPE_ALBUM in release.types:
        total += 3.0/33.0

    return total

def match_file_to_release(file, release):
    """Match files on tracks on this album, based on metadata similarity."""
    trackl = []
    trackd = {}
    for track in release.tracks:
        trackd[track.id] = track
        trackl.append({
            'id': track.id,
            'releaseid': release.id,
            'title': track.title,
            'album': release.title,
            'artist': release.artist.name,
            'duration': track.duration,
            'tracknumber': release.tracks.index(track) + 1,
            'totaltracks': len(release.tracks),
            'date': get_year(release),
            'types': release.types
        })
        
    result = match_file_to_track(file, trackl)
    if result:
        result = trackd[result['id']]
    return result

def match_file_to_track(file, tracks):
    matches = []
    for track in tracks:
        if file.get('mbtrackid') == track['id']:
            matches.append((2.0, track))
            break
        sim = compare_meta(file, track)
        matches.append((sim, track))

    if len(matches) <= 0:
        return False

    matches.sort(reverse=True)
    log.debug('Track matches: %r', matches)

    if matches[0][0] > TRACK_THRESHOLD:
        return matches[0][1]
    return False

def compare_meta(file, track):
    """
    Compare file metadata to a MusicBrainz track.

    Weights:
      * title                = 15
      * artist name          = 6
      * release name         = 8
      * length               = 10
      * number of tracks     = 4
      * track placement      = 5
      * official release     = 5
      * album release        = 3
      * cached release       = 4

    """
    total = 0.0
    parts = []

    log.debug("Comparing %s and %s", file, track)

    a = file.get('title')
    b = track.get('title')
    if a and b:
        parts.append((similarity2(a, b), 15))
        total += 15

    a = file.get('artist')
    b = track.get('artist')
    if a and b:
        parts.append((similarity2(a, b), 6))
        total += 6

    a = file.get('album')
    b = track.get('album')
    if a and b:
        parts.append((similarity2(a, b), 8))
        total += 8

    a = file.get('date')
    b = track.get('date')
    if a and b:
        score = 1.0 - abs(cmp(a,b))
        parts.append((score, 5))
        total += 5

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

    a = track.get('types')
    b = Release()
    if a:
        if b.TYPE_OFFICIAL in a:
            parts.append((1.0, 5))
        if b.TYPE_ALBUM in a:
            parts.append((1.0, 3))
        total += 8

    return reduce(lambda x, y: x + y[0] * y[1] / total, parts, 0.0)
