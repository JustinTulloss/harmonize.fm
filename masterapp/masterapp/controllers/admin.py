# vim:expandtab:smarttab
import logging
import S3
from masterapp.lib.base import *
from masterapp.model import Session, User, Song, Album
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
        
