# vim:expandtab:smarttab
import logging
import S3
from masterapp.lib.base import *
from masterapp.model import Session, File, Song, Album
from mako.template import Template
from pylons import config

log = logging.getLogger(__name__)

DEFAULT_EXPIRATION = 30 #minutes to expire a song access URL

class AdminController(BaseController):

    def index(self):
        return render('/admin.mako')

    def rmentities(self):
        c.albums = Session.query(Album).all()
        c.songs = Session.query(Song).all()
        return render('/admin/rmentities.mako')

    def rmsongs(self):
        self._rmentity(Song)

    def rmalbums(self):
        self._rmentity(Album)

    def _rmentity(self, rmclass):
        for id in request.params.iterkeys():
            entity = Session.query(rmclass).get(id)
            if entity:
                Session.delete(entity)
        Session.commit()
        redirect_to(action='rmentities')
        
    def s3cleanup(self):
        a = S3.AWSAuthConnection(config['S3.accesskey'], config['S3.secret'])
        files = a.list_bucket(config['S3.music_bucket']).entries
        for file in files:
            db=Session.query(File).filter(File.sha==file.key).first()
            if db:
                files.remove(file)
        removed =[]
        for file in files:
            removed.append(file.key)
            if request.params.get('doit'):
                a.delete(config['S3.music_bucket'], file.key)

        return removed
