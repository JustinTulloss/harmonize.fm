# vim:expandtab:smarttab
import logging
from masterapp.lib.base import *
from masterapp.lib.fbauth import ensure_fb_session, filter_friends,\
    get_user_info
from masterapp.lib.decorators import pass_user
from facebook.wsgi import facebook
from masterapp.model import Session, User, Album, Artist, Song, Playlist
from routes import url_for

log = logging.getLogger(__name__)

class RecommendController(BaseController):

    def __before__(self):
        ensure_fb_session()

    @pass_user
    def album(self, user, **kwargs):
        album = Session.query(Album).get(kwargs['entity'])
        c.entity = album.title
        c.recommender = Session.query(User).get(session['userid'])
        c.recommendee = kwargs['friend']
        c.href = 'http://%s/player#/bc/friend=%s/album=%s/song?source=4' % \
            (request.host, session['userid'], kwargs['entity'])
        facebook.notifications.send(c.recommendee,
            render('facebook/recommend.fbml.mako'))
        return True

    @pass_user
    def artist(self, user, **kwargs):
        artist = Session.query(Artist).get(kwargs['entity'])
        c.entity = artist.name
        c.recommender = Session.query(User).get(session['userid'])
        c.recommendee = kwargs['friend']
        c.href = 'http://%s/player#/bc/friend=%s/artist=%s/album?source=4' % \
            (request.host, session['userid'], kwargs['entity'])
        facebook.notifications.send(c.recommendee,
            render('facebook/recommend.fbml.mako'))
        return True

    @pass_user
    def song(self, user, **kwargs):
        song = Session.query(Song).get(kwargs['entity'])
        c.entity = song.title
        c.recommender = Session.query(User).get(session['userid'])
        c.recommendee = kwargs['friend']
        c.href = \
            'http://%s/player#/bc/friend=%s/artist=%s/album=%s/song=%s/song?source=4' %\
            (request.host, session['userid'], song.artistid, 
                song.albumid, song.id)
        facebook.notifications.send(c.recommendee,
            render('facebook/recommend.fbml.mako'))
        return True

    @pass_user
    def playlist(self, user, **kwargs):
        playlist = Session.query(Playlist).get(kwargs['entity'])
        c.entity = playlist.name
        c.recommender = Session.query(User).get(session['userid'])
        c.recommendee = kwargs['friend']
        c.href = 'http://%s/player#/bc/friend=%s/playlist=%s/playlistsong?source=4' % \
            (request.host, session['userid'], kwargs['entity'])
        facebook.notifications.send(c.recommendee,
            render('facebook/recommend.fbml.mako'))
        return True
