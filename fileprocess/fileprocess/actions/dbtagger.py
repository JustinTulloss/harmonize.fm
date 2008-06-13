import logging
from mock import Mock
from baseaction import BaseAction
from tag_compare import (
    compare_to_release,
    match_file_to_release,
    match_file_to_track
)
from pylons import config as pconfig
from sqlalchemy import engine_from_config
from sqlalchemy import engine
from fileprocess.configuration import config
log = logging.getLogger(__name__)

class DBTagger(BaseAction):
    def __init__(self, *args):
        # Hook up to the database
        pconfig['pylons.g'] = Mock()
        pconfig['pylons.g'].sa_engine = engine_from_config(config,
            prefix = 'sqlalchemy.default.'
        )
        from masterapp import model
        from masterapp.config.schema import dbfields
        self.model = model

    def process(self, file):
        if not file.has_key('puid'):
            return file

        # Get the songs that have this PUID
        songmatches = self.model.Session.query(self.model.Song).join(self.model.Puid).\
            filter(self.model.Puid.puid == file['puid']).all()

        # Make sure this file matches one of the songs with this PUID
        trackl = []
        trackd = {}
        for track in songmatches:
            trackd[track.mbid] = track
            trackl.append({
                'id': track.mbid,
                'releaseid': track.album.mbid,
                'title': track.title,
                'album': track.album.title,
                'artist': track.album.artist.name,
                'duration': track.length,
                'tracknumber': track.tracknumber,
                'totaltracks': track.album.totaltracks,
                'date': track.album.year,
            })
            
        result = match_file_to_track(file, trackl)
        if result:
            match = trackd[result['id']]
        else:
            # Didn't find any tracks in the current db that match this one
            return file
        
        # Check to see if the user already owns this song
        owner = self.model.Session.query(self.model.Owner).\
            filter(self.model.Owner.song == match).\
            filter(self.model.Owner.user == file['dbuser']).first()
        if owner:
            #Just bail now, this file's already been uploaded
            log.debug('%s has already been uploaded by %s', 
                file.get('fname'), file['fbid'])
            file['msg'] = "File has already been uploaded by user"
            file['na'] = na.NOTHING
            self.cleanup(file)
            return False

        # Create a new owner indicating they own the matched song
        nowner = self.model.Owner()
        nowner.song = match
        nowner.user = file['dbuser']
        self.model.Session.add(nowner)
        self.model.Session.commit()

        file['dbsongid'] = match.id
        file['dbartistid'] = match.artist.id
        file['dbalbumid'] = match.album.id
        return file
