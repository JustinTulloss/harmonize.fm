import logging
import os
from baseaction import BaseAction
from sqlalchemy import and_

log = logging.getLogger(__name__)

class DBRecorder(BaseAction):
    """
    This action takes a dictionary of music data and inserts it into the database

    There are certain assumptions here. One is that this is a file that has not
    been seen before. It has a unique sha in the system. It might not be a 
    unique song (hence the query by mbid), but the sha has not been seen before.
    Therefore, we need to create a new Owner and a new File after we get the
    correct metadata in place.
    """

    def process(self, file):
        assert file.has_key('mbtrackid') and file.has_key('mbalbumid') \
            and file.has_key('dbuser')
        
        if hasattr(self, 'model') == False:
            from masterapp import model
            self.model = model

        #Insert a new song if it does not exist
        qry = self.model.Session.query(self.model.Song).filter(
            self.model.Song.mbid==file["mbtrackid"]
        )
        song = qry.first()
        if song == None:
            song = self.create_song(file)

        file['dbsong'] = song

        # Create a new file associated with the song we found or created
        dbfile = self.model.File()
        dbfile.sha = file['sha']
        dbfile.song = song
        log.debug("New file %s added to files", file['sha'])
        self.model.Session.save(dbfile)
        file['dbfile'] = dbfile

        # add the file to this user's library
        owner = self.model.Owner()
        owner.user = file['dbuser']
        owner.recommendations = 0
        owner.playcount = 0
        owner.file = dbfile
        log.debug("Adding %s to %s's music", file.get('title'), file['fbid'])
        self.model.Session.save(owner)
        file['dbowner'] = owner

        log.info('%s by %s successfully inserted into the database', 
            file.get('title'), file.get('artist'))

        self.model.Session.commit() # Woot! Write baby, write!
        self.model.Session.remove()
        return file

    def create_song(self, file):
        song = self.model.Song()
        song.title = file.get('title')
        song.length = file.get('length')
        song.tracknumber = file.get('tracknumber')
        song.mbid = file['mbtrackid']
        log.debug("Saving new song %s", song.title)

        # Insert a new album if it does not exist
        qry = self.model.Session.query(self.model.Album).filter(
            self.model.Album.mbid == file['mbalbumid']
        )
        album = qry.first()
        if album == None:
            album = self.create_album(file)

        song.album = album
        self.model.Session.save(song)
        file['dbalbum'] = album
        return song

    def create_album(self, file):
        album = self.model.Album()
        for key in file.keys():
            try:
                setattr(album, key, file[key])
            except:
                pass #This just means the album table doesn't store that piece of info
        album.title = file['album']
        album.mbid = file['mbalbumid']
        log.debug("Saving new album %s", album.title)
        self.model.Session.save(album)
        return album
