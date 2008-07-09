# vim:expandtab:smarttab
import logging
import os

from masterapp.lib.base import *
from masterapp.lib.decorators import pass_user
from masterapp.lib.fbauth import ensure_fb_session
from masterapp.model import (
    Session, 
    User, 
    File, 
    Album,
    Playlist,
    BlogEntry, 
    Spotlight,
    SpotlightComment,
    Song)
from pylons import config
import pylons

import masterapp.lib.snippets as snippets

log = logging.getLogger(__name__)

class SpotlightController(BaseController):
    def __before__(self):
        if not ensure_fb_session():
            redirect_to("/request/invitation")

    def album(self, id):
        if not request.params.has_key('comment') or not id:
            abort(400)

        comment = request.params['comment']

        album = Session.query(Album).get(id)
        if album:
            spotlight = Spotlight(album = album, comment=comment)
            self._spotlight(spotlight)
        else:
            abort(404)

        return '1'

    def playlist(self, id):
        if not request.params.has_key('comment') or not id:
            abort(400)

        comment = request.params['comment']

        playlist = Session.query(Playlist).get(id)
        if playlist:
            spotlight = Spotlight(playlist = playlist, comment=comment)
            self._spotlight(spotlight)
        else:
            abort(404)

        return '1'

    def _spotlight(self, spotlight):
        user = Session.query(User).get(session['userid'])
        user.add_spotlight(spotlight)
        Session.commit()

    def edit(self):
        if not request.params.has_key('comment'):
            return "False"
        elif not request.params.has_key('spot_id'):
            return "False"
        id = request.params.get('spot_id')
        comment = request.params.get('comment')
        spotlight = Session.query(Spotlight).filter(Spotlight.id == id)[0]
        spotlight.comment = comment
        Session.commit()
        
        return "True"

    def delete(self,id):
        spot = Session.query(Spotlight).get(id)
        if (spot):
            Session.delete(spot)
            Session.commit()
            self.update_fbml()
            return "True"
        else:
            return "False"
