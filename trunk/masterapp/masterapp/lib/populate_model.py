from masterapp import model
"""
Fake Data. Sorry, I really don't care to put this elsewhere
"""
mockfbids = {'brian':1908861,'justin':1909354, 'alex':1906752, 'beth':1906978}

import logging, hashlib
log = logging.getLogger(__name__)

from tagdata import tagdata
from random import seed, randint
from sqlalchemy.sql import and_
seed()

def populate():
    """
    This function takes generated tag data which should already be present
    in tagdata.py and puts it into whatever database is currently in effect.
    It pretends there's a random number of different files that are the
    same song and a random number of owners of any particular file.
    """

    #setup users
    for fbid in mockfbids.itervalues():
        user = model.User(fbid)
        model.Session.save(user)

    model.Session.commit()

    for track in tagdata:
        # Check to see if this song exists
        song = model.Session.query(model.Song).filter(
            model.Song.title == track.get('title')
        ).first()
        if song != None:
            continue

        # Setup song
        song = model.Song()
        song.title = track.get('title')
        song.tracknumber = track.get('tracknumber')
        song.length = track.get('length')

        # Setup album (or skip it if it doesn't have one)
        if not track.has_key('album'):
            continue

        album = model.Session.query(model.Album).filter(
            model.Album.album==track['album']).first()
        if album == None:
            album = model.Album()
            _assign_anything(track, album)
            album.year = track.get('date')
            model.Session.save(album)
            model.Session.commit()

        song.albumid = album.albumid
        model.Session.save(song)
        model.Session.commit()

        #Setup files and owners
        for i in range(1, randint(1,5)):
            sha = hashlib.sha1()
            sha.update(song.title)
            sha.update(str(i))
            file=model.File(sha.hexdigest(), song.id)
            model.Session.save(file)
            model.Session.commit()

            # This selects anywhere from 1-3 owners per file and assigns
            # a random owner to it 
            for i in range(1, randint(1,3)):
                owner = model.Owner(randint(1,len(mockfbids)), file.id)
                model.Session.save(owner)
            model.Session.commit()


def _assign_anything(track, obj):
    for key,value in track.iteritems():
        try:
            setattr(obj, key, value)
        except Exception, e:
            log.info("Could not assign %s to %s", key, type(obj))
