import logging
import os
import fileprocess
from baseaction import BaseAction
from sqlalchemy import and_, engine_from_config
from pylons import config as pconfig
from mock import Mock
from filemq.configuration import config
from nextaction import na
from sqlalchemy.exceptions import OperationalError

log = logging.getLogger(__name__)

class DBChecker(BaseAction):
    """
    This class checks to see if the user is established, whether or not this
    file has been uploaded by this user, and whether or not this file
    has been uploaded by any user. Pretty much just tries to see whether
    we need to continue with the less pleasant pieces of processing this file
    """

    def __init__(self, *args, **kwargs):
        super(DBChecker, self).__init__(*args, **kwargs)
        pconfig['pylons.g'] = Mock()
        pconfig['pylons.g'].sa_engine = engine_from_config(config,
            prefix = 'sqlalchemy.default.'
        )
        from masterapp import model
        self.model = model

    def process(self, file):
        assert file and len(file)>0 and \
            file.has_key('fbid')
        self.model.Session()

        try:
            # Get this user, create him if he doesn't exist
            qry = self.model.Session.query(self.model.User).filter(
                self.model.User.fbid == file['fbid']
            )
            user = qry.first()
            if user == None:
                user = self.model.User(file['fbid'])
                self.model.Session.save(user)
                self.model.Session.commit()

            file['dbuserid'] = user.id

            return self._check(file, user)
        except OperationalError:
            self.model.Session.rollback()
            log.warn("Database error occurred, bailing on %s", file)
            raise
        finally:
            self.model.Session.expunge_all()
            self.model.Session.close()

    def _success(self, file):
        self.model.Session.commit()
        self.cleanup(file)
        return False

    def _check(self, file, user):
        song = None
        if file.has_key('title') and file.has_key('album') and \
                file.has_key('artist'):
            qry = self.model.Session.query(self.model.Song).join(
                self.model.Song.artist, self.model.Song.album).filter(
                self.model.Artist.name == file['artist']).filter(
                self.model.Album.title == file['album']).filter(
                self.model.Song.title == file['title'])
            song = qry.first()

        if not song:
            return file

        # Check to see if this user owns this songs
        owner = self.model.Session.query(self.model.SongOwner).filter(
            and_(self.model.SongOwner.songid==song.id, 
                self.model.SongOwner.uid == user.id)
        ).first()
        if owner:
            # This file has already been uploaded by this fella
            log.debug('%s has already been uploaded by %s', 
                file.get('fname'), file['fbid'])
            file['msg'] = "File has already been uploaded by user"
            file['na'] = na.NOTHING
            self.cleanup(file)
            return False

        # Make a new PUID if this puid !exist
        if file.get('puid'):
            puid = self.model.Session.query(self.model.Puid).\
                filter(self.model.Puid.puid == file['puid']).first()
            if not puid:
                puid = self.model.Puid()
                puid.song = song
                puid.puid = file['puid']
                self.model.Session.add(puid)

        # Make a new owner
        owner = user.add_song(song)

        # Check the quality of this song if an actual file was uploaded
        if file.has_key('sha'):
            dbfile = self.model.Session.query(self.model.File).filter_by(
                sha = file['sha']).first()
            if dbfile:
                # This file has been uploaded, we've created a user, we
                # happy
                return self._success(file)
            else:
                # Create a new file associated with the song we found or created
                dbfile = self.model.File(
                    sha = file['sha'],
                    bitrate = file.get('bitrate'),
                    size = file.get('size'),
                    song = song
                )
                log.debug("New file %s added to files", file['sha'])

                if dbfile.bitrate > song.bitrate and \
                        dbfile.bitrate < config['maxkbps']:
                    # Found a higher quality song
                    song.sha = file.get('sha')
                    song.bitrate = file.get('bitrate')
                    song.size = file.get('size')
                
                # Mark the owner of this fine file
                fowner = self.model.Owner(file=dbfile, user=user)
                self.model.Session.add_all([dbfile, fowner])

        return self._success(file)
                    
