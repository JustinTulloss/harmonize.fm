# vim:expandtab:smarttab
import logging
from masterapp.lib.base import *
from masterapp.lib.fbauth import ensure_fb_session, filter_friends,\
    get_user_info
from masterapp.lib.decorators import pass_user
from facebook.wsgi import facebook
from masterapp.model import \
        Session, User, Album, Artist, Song, Playlist, Recommendation, Whitelist
from routes import url_for

log = logging.getLogger(__name__)

class RecommendController(BaseController):

    def __before__(self):
        ensure_fb_session()

    def whitelist_user(self, user):
        # first check to see if the user is already in our database:
        qry = Session.query(User).filter(User.fbid == user)
        if qry.count() != 0:
            # user is already a member
            return '1'
        # now we check to see if they're already on the whitelist
        qry = Session.query(Whitelist).filter(Whitelist.fbid == user)
        if qry.count() != 0:
            # the user is already on the whitelist
            return '1'
        w = Whitelist(fbid=user, registered=False)
        Session.save(w)
        Session.commit()
        return '1'


    @pass_user
    def album(self, user, **kwargs):
        if not kwargs.get('entity') and kwargs.get('friend'):
            abort(400)
        album = Session.query(Album).get(kwargs['entity'])
        if not album:
            abort(404)
        c.entity = album.title
        c.recommender = user
        c.recommendee = kwargs['friend']
        c.href = 'http://%s/player#/browse/friend=%s/album=%s/song' % \
            (request.host, session['userid'], kwargs['entity'])
        fbml = render('facebook/recommend.fbml.mako')
        facebook.notifications.send(c.recommendee, fbml)
        subject = '%s has recommended you an album' % user.name
        facebook.notifications.sendEmail(c.recommendee, subject, fbml=fbml)
    
        rec = Recommendation(c.recommender.id, int(c.recommendee), 
                albumid=album.id)
        Session.save(rec)
        Session.commit()
        self.whitelist_user(c.recommendee)
        return '1'

    @pass_user
    def artist(self, user, **kwargs):
        if not kwargs.get('entity') and kwargs.get('friend'):
            abort(400)
        artist = Session.query(Artist).get(kwargs['entity'])
        if not artist:
            abort(404)
        c.entity = artist.name
        c.recommender = user
        c.recommendee = kwargs['friend']
        c.href = 'http://%s/player#/browse/friend=%s/artist=%s/album' % \
            (request.host, session['userid'], kwargs['entity'])
        facebook.notifications.send(c.recommendee,
            render('facebook/recommend.fbml.mako'))

        self.whitelist_user(c.recommendee)
        return '1'

    @pass_user
    def song(self, user, **kwargs):
        if not kwargs.get('entity') and kwargs.get('friend'):
            abort(400)
        song = Session.query(Song).get(kwargs['entity'])
        if not song:
            abort(404)
        c.entity = song.title
        c.recommender = user
        c.recommendee = kwargs['friend']
        c.href = \
            'http://%s/player#/browse/friend=%s/artist=%s/album=%s/song=%s/song' %\
            (request.host, session['userid'], song.artistid, 
                song.albumid, song.id)
        fbml = render('facebook/recommend.fbml.mako')
        facebook.notifications.send(c.recommendee, fbml)
        subject = '%s has recommended you a song' % (user.name)
        facebook.notifications.sendEmail(c.recommendee, subject, fbml=fbml)

        rec = Recommendation(c.recommender.id, int(c.recommendee), 
                songid=song.id)
        Session.save(rec)
        Session.commit()
        self.whitelist_user(c.recommendee)
        return '1'

    @pass_user
    def playlist(self, user, **kwargs):
        if not kwargs.get('entity') and kwargs.get('friend'):
            abort(400)
        playlist = Session.query(Playlist).get(kwargs['entity'])
        if not playlist:
            abort(404)
        c.entity = playlist.name
        c.recommender = user
        c.recommendee = kwargs['friend']
        c.href = 'http://%s/player#/browse/friend=%s/playlist=%s/playlistsong' % \
            (request.host, session['userid'], kwargs['entity'])
        fbml = render('facebook/recommend.fbml.mako')
        facebook.notifications.send(c.recommendee, fbml)
        subject = '%s has recommended you a playlist' % user.name
        facebook.notifications.sendEmail(c.recommendee, subject, fbml=fbml)

        rec = Recommendation(c.recommender.id, int(c.recommendee), 
                playlistid=playlist.id)
        Session.save(rec)
        Session.commit()
        self.whitelist_user(c.recommendee)
        return '1'
