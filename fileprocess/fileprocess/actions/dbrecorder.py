import logging
import os
from mock import Mock
from ..processingthread import na
from baseaction import BaseAction
from sqlalchemy import and_, engine_from_config
from pylons import config as pconfig
from fileprocess.configuration import config

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

    def __init__(self, *arg, **kwargs):
        super(DBRecorder, self).__init__(*arg, **kwargs)
        pconfig['pylons.g'] = Mock()
        pconfig['pylons.g'].sa_engine = engine_from_config(config,
            prefix = 'sqlalchemy.default.'
        )
        from masterapp import model
        self.model = model


    def process(self, file):
        assert file.has_key('dbuser')
        
        song = None
        puid = None
        if file.has_key('mbtrackid'):
            #Insert a new song if it does not exist
            qry = self.model.Session.query(self.model.Song).filter(
                self.model.Song.mbid==file["mbtrackid"]
            )
            song = qry.first()
        elif file.has_key('puid'):
            # If it has a puid but isn't in MB, assume that anything we get is
            # the same song since it's not reasonable to assume that an unknown
            # song is on multiple releases
            puid = self.model.Session.query(self.model.Puid).filter(
                self.model.Puid.puid == file['puid']
            ).first()
            if qry:
                song = qry.song

        if not puid:
            song = self.create_song(file)

        if not puid and file.has_key('puid'):
            puid = self.model.Puid()
            puid.song = song
            puid.puid = file['puid']
            self.model.Session.add(puid)

        dbfile = None
        if file.has_key('sha'):
            # Create a new file associated with the song we found or created
            dbfile = self.model.File()
            dbfile.sha = file['sha']
            dbfile.song = song
            log.debug("New file %s added to files", file['sha'])
            self.model.Session.save(dbfile)

        # add the file to this user's library
        owner = self.model.Owner()
        owner.user = file['dbuser']
        owner.song = song
        owner.file = dbfile
        log.debug("Adding %s to %s's music", file.get('title'), file['fbid'])
        self.model.Session.save(owner)

        log.info('%s by %s successfully inserted into the database', 
            file.get('title'), file.get('artist'))

        try:
            self.model.Session.commit() # Woot! Write baby, write!

            # Put all the database ids in the file dict
            file['dbownerid'] = owner.id
            file['dbsongid'] = song.id
            file['dbalbumid'] = song.album.id
            file['dbartistid'] = song.artist.id

        except Exception, e:
            log.warn("Could not commit %s: %s", file['title'], e)
            self.model.Session.rollback()
            file['msg'] = "File could not be committed to database"
            file['na'] = na.FAILURE
        finally:
            self.model.Session.remove()
            return file



    def create_song(self, file):
        song = self.model.Song(
            title = file.get('title'),
            length = file.get('duration'),
            tracknumber = file.get('tracknumber'),
            mbid = file.get('mbtrackid')
        )
        log.debug("Saving new song %s", song.title)

        if file.has_key('mbartistid') and file.has_key('mbalbumid'):
            # Insert a new artist if it does not exist
            qry = self.model.Session.query(self.model.Artist).filter(
                self.model.Artist.mbid == file['mbartistid']
            )
            artist = qry.first()

            # Insert a new album if it does not exist
            qry = self.model.Session.query(self.model.Album).filter(
                self.model.Album.mbid == file['mbalbumid']
            )
            album = qry.first()
        else:
            # Without MBids, we just kind of guess with tags
            qry = self.model.Session.query(self.model.Artist, self.model.Album).filter(
                self.model.Artist.name == file['artist'],
                self.model.Album.artist.name == file['artist'],
                self.model.Album.title == file['album']
            )
            artist, album = qry.first()

        if not artist:
            artist = self.create_artist(file)
        if not album:
            album = self.create_album(file, artist)

        song.album = album
        song.artist = artist
        self.model.Session.add(song)

        return song

    def create_album(self, file, artist):
        album = self.model.Album(
            title = file.get('album'),
            mbid = file.get('mbalbumid'),
            asin = file.get('asin'),
            year = file.get('year'),
            totaltracks = file.get('totaltracks'),
            smallart = file.get('smallart'),
            medart = file.get('medart'),
            largeart = file.get('largeart'),
            swatch = file.get('swatch')
        )
        if file.has_key('mbalbumartistid'):
            qry = self.model.Session.query(self.model.Artist).filter(
                self.model.Artist.mbid == file.get('mbalbumartistid')
            )
            artist = qry.first()

        if not artist:
            artist = self.create_artist(file, albumartist=True)
        album.artist = artist
        log.debug("Saving new album %s", album.title)
        self.model.Session.add(album)
        return album

    def create_artist(self, file, albumartist = False):
        artist = self.model.Artist()
        if albumartist:
            artist.mbid = file.get('mbalbumartistid')
            artist.name = file.get('albumartist')
            artist.sort = file.get('albumartistsort')
        else:
            artist.mbid = file.get('mbartistid')
            artist.name = file.get('artist')
            artist.sort = file.get('artistsort')

        log.debug("Saving new artist %s", artist.name)
        self.model.Session.add(artist)
        return artist
