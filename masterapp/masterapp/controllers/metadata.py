# vim:expandtab:smarttab
import logging
from masterapp.lib.base import *
from masterapp.lib.fbauth import (
    ensure_fb_session, 
    filter_friends,
    filter_any_friend
)
from sqlalchemy import sql, or_
from masterapp.model import \
    Song, Album, Artist, Owner, File, Session, User, Playlist, PlaylistSong
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
        'Artist_id',
        'Artist_name',
        'Artist_sort',
        'Artist_availsongs',
        'Artist_numalbums',
    ],
    'playlist': [],
    'friend': [
        'type',
        'Friend_id',
        'Friend_name',
    ],
}

class MetadataController(BaseController):
    """
    This class is for querying for metadata about songs. All of its functions
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

    def _dictionize_row(self, sqlrow, type):
        expanded = {}
        prefix = sqlrow.__class__.__name__
        for field in sqlrow.c.keys():
            key = prefix + '_' + field
            val = getattr(sqlrow, field)
            if isinstance(val, Decimal):#FIXME: The model should address this
                val = int(val)
            expanded[key] = val
        return expanded

    def _build_json_row(self, sqlrow, type):
        if hasattr(sqlrow, '__iter__'):
            expanded = {}
            for rowpart in sqlrow:
                expanded.update(self._build_json_row(rowpart, type))
            return expanded
        else:
            return self._dictionize_row(sqlrow, type)
        
    def _build_json(self, results, type):
        json = { "data": []}
        for row in results:
            json['data'].append(self._build_json_row(row, type))
            json['data'][len(json['data'])-1]['type']=type

        json['success']=True
        return json

    @jsonify
    def _json_failure(self, error='A problem occurred requesting your data'):
        return {'success':False, 'error':error, 'data':[]}

    def index(self):
        type = request.params.get('type')
        handler=self.datahandlers.get(type, self._json_failure)
        return handler()

    @jsonify
    def songs(self):
        qry = Session.query(Song).join('artist').\
            reset_joinpoint().join('album').\
            reset_joinpoint().join(['files', 'owners', 'user']).\
            add_entity(Album).add_entity(Artist)

        if request.params.get('artist'):
            qry = qry.filter(Artist.id == request.params.get('artist'))
        if request.params.get('album'):
            qry = filter_any_friend(qry)
            qry = qry.filter(Album.id== request.params.get('album'))
        else:
            qry = filter_friends(qry)
        if request.params.get('playlist'):
            qry = qry.filter(Playlist.id == request.params.get('playlist'))

        qry = qry.order_by([Artist.sort, Album.title, Song.tracknumber])
        results = qry.all()
        return self._build_json(results, 'song')

    @jsonify
    def albums(self):
        qry = Session.query(Album).join('artist').\
            reset_joinpoint().join(['songs', 'files', 'owners', 'user']).\
            add_entity(Artist)

        qry = filter_friends(qry)

        if request.params.get('artist'):
            qry = qry.filter(Artist.id == request.params.get('artist'))
        qry = qry.order_by([Artist.sort, Album.title])
        results = qry.all()
        return self._build_json(results, 'album')
        
    @jsonify
    def artists(self):
        qry = Session.query(Artist).join(['songs','files','owners', 'user'])
        qry = filter_friends(qry)
        qry = qry.order_by(Artist.sort)
        results = qry.all()
        return self._build_json(results, 'artist')
        
    @jsonify
    def friends(self):
        dtype = request.params.get('type')
        userStore = session['fbfriends']
        data=facebook.users.getInfo(userStore)

        qry = Session.query(Owner).join(['user'])
        cond = or_()
        for friend in data:
            cond.append(User.fbid == friend['uid'])
        qry = qry.filter(cond)
        qry = qry.order_by(User.fbid)
        results = qry.all()

        def _intersect(item):
            if len(results) > 0:
                if results[0].user.fbid == item['uid']:
                    item['Friend_name'] = item['name']
                    item['type'] = dtype
                    item['Friend_id'] = results[0].user.id
                    del item['name']
                    del item['uid']
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
    def playlists(self):
        qry = Session.query(Playlist).join('owner')
        qry = filter_friends(qry)
        qry = qry.order_by(Playlist.name)
        results = qry.all()
        return self._build_json(results, 'playlist')

    @jsonify
    def playlistsongs(self):
        qry = Session.query(PlaylistSong).join('playlist').reset_joinpoint(). \
            join('album').reset_joinpoint().join(['files', 'owners', 'user'])
        qry = filter_friends(qry)
        qry = qry.filter(Playlist.playlistid == request.params.get('playlist'))

        qry = qry.order_by(PlaylistSong.songindex)
        results = qry.all()
        return self._build_json(results, 'playlistsong')
