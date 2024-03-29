import logging
import re
import os
from mock import Mock
from nextaction import na
from dbchecker import DBChecker
from sqlalchemy import and_, engine_from_config
from pylons import config as pconfig
from fileprocess.configuration import config

log = logging.getLogger(__name__)

class DBRecorder(DBChecker):
    """
    This action takes a dictionary of music data and inserts it into the database

    There are certain assumptions here. One is that this is a file that has not
    been seen before. It has a unique sha in the system. It might not be a 
    unique song (hence the query by mbid), but the sha has not been seen before.
    Therefore, we need to create a new Owner and a new File after we get the
    correct metadata in place.
    """
    sorter = re.compile('^([!@#$%^&*\-_+=<>,.;:\'{}|`~".()\[\]\\\]+|the )',
        re.IGNORECASE)

    def process(self, file):
        assert file.has_key('dbuserid')

        try:
            self.model.Session()
            user = self.model.Session.query(self.model.User).get(file['dbuserid'])

            # This checks based on the raw tags. If they match, it does everything i
            # need and returns False. If they don't match, i need to create the song
            if not self._check(file, user):
                self.cleanup(file)
                return False

            song = self.create_song(file)
            if file.has_key('puid'):
                if file['puid']:
                    puid = self.model.Session.query(self.model.Puid).filter(
                        self.model.Puid.puid == file['puid']
                    ).first()
                    if file.get('puid'):
                        puid = self.model.Puid()
                        puid.song = song
                        puid.puid = file['puid']


            dbfile = None
            if file.has_key('sha'):
                dbfile = self.model.Session.query(self.model.File).filter(
                    self.model.File.sha == file['sha']
                ).first()
                if not dbfile:
                    # Create a new file associated with the song we found or created
                    dbfile = self.model.File(
                        sha = file['sha'],
                        bitrate = file.get('bitrate'),
                        size = file.get('size'),
                        song = song
                    )
                    log.debug("New file %s added to files", file['sha'])

                # Mark the owner of this fine file
                fowner = self.model.Owner(file=dbfile, user=user)
                self.model.Session.add_all([dbfile, fowner])

            # add the file to this user's library
            owner = user.add_song(song)
            log.debug("Adding %s to %s's music", file.get('title'), file['fbid'])

            self.model.Session.add(song)
            self.model.Session.commit() # Woot! Write baby, write!

            log.info('%s by %s successfully inserted into the database', 
                file.get('title'), file.get('artist'))

            # Put all the database ids in the file dict
            file['dbownerid'] = owner.id
            file['dbsongid'] = song.id
            file['dbalbumid'] = song.album.id
            file['dbartistid'] = song.artist.id

        except Exception, e:
            log.exception("Could not commit %s: %s", file.get('title'))
            self.model.Session.rollback()
            raise
        finally:
            log.debug('Clearing and closing Session')
            self.model.Session.expunge_all()
            self.model.Session.close()

        return file

    def create_song(self, file):
        if file.get('fname') == None:
            assert file.get('puid') != None, \
                "File must have puid if you don't upload it"
            # This song is different tag version of a song we've seen
            othersong = self.model.Session.query(self.model.Song).join(
                self.model.Puid).filter(
                self.model.Puid.puid == file['puid']
            ).first()
            file['sha'] = othersong.sha
            file['size'] = othersong.size
            file['bitrate'] = othersong.bitrate

        song = self.model.Song(
            title = file.get('title'),
            length = file.get('duration'),
            tracknumber = file.get('tracknumber'),
            mbid = file.get('mbtrackid'),
            sha = file['sha'],
            size = file['size'],
            bitrate = file.get('bitrate'),
        )
        log.debug("Saving new song %s", song.title)

        artist = None
        album = None
        # Guess if we have seen this before based on tags
        qry = self.model.Session.query(self.model.Artist).\
            filter(self.model.Artist.name == file['artist'])
        artist = qry.first()

        if not artist:
            artist = self.create_artist(file)
        else:
            if not artist.mbid and file.get('mbartistid'):
                artist.mbid = file.get('mbartistid')
                self.model.Session.add(artist)

        albumartist = artist
        if file.get('albumartist'):
            if file['albumartist'] != file['artist']:
                qry = self.model.Session.query(self.model.Artist).\
                    filter(self.model.Artist.name == file['albumartist'])
                albumartist = qry.first()


        if not file.get('album'):
            file['album'] = 'Unknown Album'
        qry = self.model.Session.query(self.model.Album).\
            join(self.model.Album.artist).\
            filter(self.model.Album.title == file['album']).\
            filter(self.model.Album.artist == albumartist)
        album = qry.first()

        if not album:
            album = self.create_album(file, artist)
        else:
            if not album.mbid and file.get('mbalbumid'):
                album.mbid = file.get('mbalbumid')
            if not album.asin and file.get('asin'):
                album.asin = file.get('asin')
            if not album.smallart and file.get('smallart'):
                album.smallart = file.get('smallart')
            if not album.medart and file.get('medart'):
                album.medart = file.get('medart')
            if not album.swatch and file.get('swatch'):
                album.swatch = file['swatch']
            if not album.year and file.get('year'):
                album.year = file['year']

        song.album = album
        song.artist = artist

        return song

    def create_album(self, file, artist):
        album = self.model.Album(
            title = file.get('album'),
            mbid = file.get('mbalbumid'),
            asin = file.get('asin'),
            mp3_asin = file.get('mp3_asin'),
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
            sortname = self.sorter.sub('', file.get('albumartist'))
            artist.sort = sortname if sortname else file.get('albumartist')
        else:
            artist.mbid = file.get('mbartistid')
            artist.name = file.get('artist')
            sortname = self.sorter.sub('', file.get('artist'))
            artist.sort = sortname if sortname else file.get('artist')

        log.debug("Saving new artist %s", artist.name)
        self.model.Session.add(artist)
        return artist
