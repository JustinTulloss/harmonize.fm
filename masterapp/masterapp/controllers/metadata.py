# vim:expandtab:smarttab
import logging
from masterapp.lib.base import *
from masterapp.lib.fbauth import (
    ensure_fb_session, 
    filter_friends,
    filter_sql_friends,
    filter_any_friend
)
from sqlalchemy import sql, or_
from masterapp import model
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

fields = {
    'song': [
        'type',
        'Friend_id',
        'Song_id',
        'Song_tracknumber',
        'Song_title',
        'Song_length',
        'Album_title',
        'Album_totaltracks',
        'Artist_name',
    ],
    'album': [
        'type',
        'Friend_id',
        'Album_id',
        'Album_title',
        'Album_totaltracks',
        'Album_havesongs',
        'Album_length',
        'Album_year',
        'Artist_name',
    ],
    'artist': [
        'type',
        'Friend_id',
        'Artist_id',
        'Artist_name',
        'Artist_sort',
    ],
    'playlist': [],
    'friend': [
        'type',
        'Friend_id',
        'Friend_name',
    ],
}

dbfields = {}
for k, v in fields.items():
    cols = []
    for column in v:
        try:
            klass, field = column.split('_')
            cols.append(getattr(getattr(model, klass), field).label(column))
        except:
            pass
    dbfields[k] = cols

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

    def _filter_user(func):
        def filtered(self, *args):
            query = func(self, *args)
            friendid = request.params.get('friend')
            if not friendid:
                friendid = session['user'].id
            self.friend = friendid
            return filter_user(query, friendid)
        return filtered

    def _build_json(func):
        def builder(self, *args):
            query = func(self, *args)
            results = query.all()
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
                json['data'][len(json['data'])-1]['Friend_id'] = self.friend
            json['success']=True
            return json
        return builder

    @jsonify
    def _json_failure(self, error='A problem occurred requesting your data'):
        return {'success': False, 'error': error, 'data':[]}

    def index(self):
        type = request.params.get('type')
        handler=self.datahandlers.get(type, self._json_failure)
        return handler()

    @jsonify
    @_build_json
    @_filter_user
    def songs(self):
        qry = Session.query(*dbfields['song']).join(Song.artist).\
            reset_joinpoint().join(Album).group_by(Song)

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

    @jsonify
    @_build_json
    @_filter_user
    def albums(self):
        qry = Session.query(*dbfields['album']).join(Album.artist).\
            join(Album.songs).group_by(Album)
        if request.params.get('artist'):
            qry = qry.filter(Artist.id == request.params.get('artist'))
        qry = qry.order_by([Artist.sort, Album.title])
        return qry
        
    @jsonify
    @_build_json
    @_filter_user
    def artists(self):
        numalbums = Session.query(Album.artistid,
            sql.func.count('*').label('numalbums')
        ).group_by(Album.artistid).subquery()

        qry = Session.query(numalbums.c.numalbums, *dbfields['artist']).\
            join(Artist.albums).join(Song).group_by(Artist)
        qry = qry.order_by(Artist.sort)
        return qry
        
    @jsonify
    def friends(self):
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

    @jsonify
    @_build_json
    @_filter_user
    def playlists(self):
        qry = Session.query(Playlist).join('owner')
        qry = filter_friends(qry)
        qry = qry.order_by(Playlist.name)
        results = qry.all()
        return self._build_json(results, 'playlist')

    @jsonify
    @_build_json
    @_filter_user
    def playlistsongs(self):
        qry = Session.query(PlaylistSong).join('playlist').reset_joinpoint(). \
            join('album').reset_joinpoint().join(['files', 'owners', 'user'])
        qry = filter_friends(qry)
        qry = qry.filter(Playlist.playlistid == request.params.get('playlist'))

        qry = qry.order_by(PlaylistSong.songindex)
        results = qry.all()
        return self._build_json(results, 'playlistsong')
