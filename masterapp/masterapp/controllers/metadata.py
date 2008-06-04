# vim:expandtab:smarttab
import logging
import simplejson
from masterapp.lib.base import *
from masterapp.lib.fbauth import (
    ensure_fb_session, 
    filter_friends,
    filter_sql_friends,
    filter_any_friend
)
from sqlalchemy import sql, or_
from masterapp import model
from masterapp.config.schema import dbfields
from masterapp.model import (
    Song,
    Album, 
    Artist, 
    Owner, 
    File, 
    Session, 
    User, 
    Playlist, 
    PlaylistSong,
    filter_user
)
from pylons import config
from facebook import FacebookError
from facebook.wsgi import facebook
from operator import itemgetter
from functools import partial
from decimal import Decimal

log = logging.getLogger(__name__)

class MetadataController(BaseController):
    """
    This class is for querying for metadata about songs. All of its actions
    return JSON, so anybody using it should probably be ready to deal with
    that.
    """

    def __init__(self):
        super(MetadataController, self).__init__()
        self.datahandlers = {
            'artist': self.artists,
            'album': self.albums,
            'song': self.songs,
            'friend': self.friends,
            'playlist': self.playlists,
            'playlistsong': self.playlistsongs
        }

    def __before__(self):
        ensure_fb_session()

    def _pass_user(func):
        def pass_user(self, *args, **kwargs):
            friendid = request.params.get('friend')
            if not friendid:
                user = Session.query(User).get(session['userid'])
            else:
                # TODO: Make sure they're friends
                user = Session.query(User).get(friendid)
            return func(self, user, *args, **kwargs)
        return pass_user

    def _filter_user(func):
        def filtered(self, *args):
            query = func(self, *args)
            friendid = request.params.get('friend')
            if not friendid:
                friendid = session['userid']
            self.friendid = friendid
            return filter_user(query, friendid).all()
        return filtered
    
    def _build(self, results):
        json = { "data": []}
        for row in results:
            lrow = {}
            for key in row.keys():
                value = getattr(row, key)
                if isinstance(value, Decimal):
                    value = int(value)
                lrow[key] = value
            json['data'].append(lrow)
            json['data'][len(json['data'])-1]['type'] =\
                request.params.get('type')
            if hasattr(self, 'friendid'):
                json['data'][len(json['data'])-1]['Friend_id'] = self.friendid
        json['success']=True
        return json
        

    def _build_json(func):
        def wrapper(self, *args):
            return self._build(func(self, *args))
        return wrapper

    @cjsonify
    def _json_failure(self, error='A problem occurred requesting your data'):
        return {'success': False, 'error': error, 'data':[]}

    def index(self):
        type = request.params.get('type')
        handler=self.datahandlers.get(type, self._json_failure)
        return handler()

    @cjsonify
    @_build_json
    @_pass_user
    def songs(self, user):
        qry = user.song_query

        sort = [Artist.sort, Album.title, Song.tracknumber]
        if request.params.get('album'):
            qry = qry.filter(Album.id== request.params.get('album'))
            sort = [Song.tracknumber]
        elif request.params.get('artist'):
            qry = qry.filter(Artist.id == request.params.get('artist'))
        if request.params.get('playlist'):
            qry = qry.filter(Playlist.id == request.params.get('playlist'))

        qry = qry.order_by(sort)
        return qry

    @cjsonify
    @_build_json
    @_pass_user
    def albums(self, user):
        qry = user.album_query
        if request.params.get('artist'):
            qry = qry.filter(Artist.id == request.params.get('artist'))
        qry = qry.order_by([Artist.sort, Album.title])
        results = qry.all()
        return results
        
    @cjsonify
    @_build_json
    @_pass_user
    def artists(self, user):
        """
        numalbums = Session.query(Album.artistid,
            sql.func.count('*').label('numalbums')
        ).group_by(Album.artistid).subquery()

        qry = Session.query(numalbums.c.numalbums, *dbfields['artist']).\
            join(Artist.albums).join(Song).group_by(Artist)
        qry = qry.order_by(Artist.sort)
        """
        return user.artist_query.all()
        
    @cjsonify
    @_pass_user
    def friends(self, user):
        dtype = request.params.get('type')
        userStore = session['fbfriends']
        data=facebook.users.getInfo(userStore)

        qry = Session.query(User).join(['owners'])
        cond = or_()
        for friend in data:
            cond.append(User.fbid == friend['uid'])
        qry = qry.filter(cond)
        qry = qry.order_by(User.fbid)
        results = qry.all()

        def _intersect(item):
            if len(results) > 0:
                if results[0].fbid == item['uid']:
                    item['type'] = dtype
                    item['Friend_name'] = item['name']
                    item['Friend_id'] = results[0].id
                    del item['uid']
                    del item['name']
                    del results[0]
                    return True
                else:
                    return False
            else:
                return False

        # This is a bit confusing. It looks at all the friends you have that own
        # the app and then check to see if they have any songs. Those that do
        # get passed through and their names are passed back. We do this because
        # we fetch the name from facebook and the ownership information
        # from our own database.
        data = sorted(data, key=itemgetter('uid'))
        data = filter(_intersect, data)
        data = sorted(data, key=itemgetter('Friend_name'))

        return {'success':True, 'data':data}

    @cjsonify
    @_build_json
    @_pass_user
    def playlists(self, user):
        qry = Session.query(Playlist).join('owner')
        qry = filter_friends(qry)
        qry = qry.order_by(Playlist.name)
        results = qry.all()
        return self._build_json(results, 'playlist')

    @cjsonify
    @_build_json
    @_pass_user
    def playlistsongs(self, user):
        qry = Session.query(PlaylistSong).join('playlist').reset_joinpoint(). \
            join('album').reset_joinpoint().join(['files', 'owners', 'user'])
        qry = filter_friends(qry)
        qry = qry.filter(Playlist.playlistid == request.params.get('playlist'))

        qry = qry.order_by(PlaylistSong.songindex)
        results = qry.all()
        return self._build_json(results, 'playlistsong')

    def album_by_id(self, id):
        res = Session.query(*dbfields['album']).join(Album.artist).filter(Album.id==id).group_by(Album)
        json = self._build(res)
        json['data'][0]['type'] = 'album'
        json['data'][0]['Friend_id'] = request.params.get('friend')
        return simplejson.dumps(json)
