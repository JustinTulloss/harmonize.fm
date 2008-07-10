# vim:expandtab:smarttab
import logging
import os

from sqlalchemy.sql import and_
from masterapp.lib.base import *
from masterapp.lib.decorators import pass_user, cjsonify, d_build_json
from masterapp.lib.fbauth import ensure_fb_session
from masterapp.config.schema import dbfields
from masterapp.model import (
    Session, 
    User, 
    File, 
    Album,
    Artist,
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
        ensure_fb_session()

    def album(self, id):
        if not request.params.has_key('comment') or not id:
            abort(400)

        comment = request.params['comment']

        album = Session.query(Album).get(id)
        if album:
            spotlight = Spotlight(album = album, comment=comment)
            self._spotlight(spotlight)
            return str(spotlight.id)
        else:
            abort(404)

    def playlist(self, id):
        if not request.params.has_key('comment') or not id:
            abort(400)

        comment = request.params['comment']

        playlist = Session.query(Playlist).get(id)
        if playlist:
            spotlight = Spotlight(playlist = playlist, comment=comment)
            self._spotlight(spotlight)
            return str(spotlight.id)
        else:
            abort(404)

    def _spotlight(self, spotlight):
        user = Session.query(User).get(session['userid'])
        user.add_spotlight(spotlight)
        Session.commit()

    def edit(self, id):
        if not request.params.has_key('comment') or not id:
            abort(400)

        #id = request.params.get('spot_id')
        comment = request.params.get('comment')
        spotlight = Session.query(Spotlight).filter(Spotlight.id == id)[0]
        user = Session.query(User).get(session['userid'])
        if not spotlight or not spotlight in user.spotlights:
            abort(404)

        spotlight.comment = comment
        Session.add(spotlight)
        Session.commit()
        
        return "1"

    def delete(self,id):
        if not id:
            abort(400)
        user = Session.query(User).get(session['userid'])
        spot = Session.query(Spotlight).get(id)
        if not spot or not spot in user.spotlights:
            abort(404)

        Session.delete(spot)
        Session.commit()
        user.update_profile()
        return "1"

    @cjsonify
    @d_build_json
    @pass_user
    def find_album(self, user, **kwargs):
        id = kwargs['id']
        if not id:
            abort(400)
        qry = Session.query(*dbfields['spotlight']).join(Spotlight.album).\
            join(Album.artist).filter(Spotlight.id == id).\
            filter(User.id == user.id)
        return qry.all()
        
    @cjsonify
    @d_build_json
    @pass_user
    def find_playlist(self, user, **kwargs):
        id = kwargs['id']
        if not id:
            abort(400)
        qry = Session.query(*dbfields['spotlight']).\
        join(Spotlight.playlist).filter(Spotlight.id == id).\
        filter(User.id == user.id).limit(1)
        return qry.all()
    
    # right now this only returns true or false
    # depending on whether or not a spotlight exists
    # for the album    
    @pass_user
    def find_by_album(self, user, **kwargs):
        id = kwargs['id']
        if not id:
            abort(400)
        album = Session.query(Album).filter(Album.id == id)
        if album.first():
            qry = Session.query(Spotlight).filter(and_(
                    Spotlight.albumid == album[0].id,
                    Spotlight.uid == user.id,
                    Spotlight.active == 1))
            if qry.first():
                return "1"
            else:
                return "0"
        else:
            return "0"

    #this returns true or false depending on whether or not the spotlight already exists
    @pass_user
    def find_by_playlist(self,user, **kwargs):
        id = kwargs['id']
        if not id:
            abort(400)
        
        playlist = Session.query(Playlist).filter(Playlist.id == id)
        if playlist.first():
            qry = Session.query(Spotlight).filter(and_(
                    Spotlight.playlistid == playlist[0].id,
                    Spotlight.uid == user.id,
                    Spotlight.active == 1))
            if qry.first():
                return "1"
        return "0"
