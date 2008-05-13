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

    def _dictionize_row(self, sqlrow):
        expanded = {}
        for field in sqlrow.c.keys():
            val = getattr(sqlrow, field)
            if isinstance(val, Decimal):#FIXME: The model should address this
                val = int(val)
            expanded[field] = val
        return expanded

    def _build_json_row(self, sqlrow):
        if hasattr(sqlrow, '__iter__'):
            expanded = {}
            for rowpart in sqlrow:
                expanded.update(self._build_json_row(rowpart))
            return expanded
        else:
            return self._dictionize_row(sqlrow)
        
    def _build_json(self, results):
        dtype = request.params.get('type')
        json = { "data": []}

        for row in results:
            json['data'].append(self._build_json_row(row))
            json['data'][len(json['data'])-1]['type']=dtype

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
        qry = Session.query(Song).join('album').\
            reset_joinpoint().join(['files', 'owners', 'user']).add_entity(Album)


        if request.params.get('artist'):
            qry = qry.filter(Album.artist == request.params.get('artist'))
        if request.params.get('album'):
            qry = filter_any_friend(qry)
            qry = qry.filter(Album.albumid== request.params.get('album'))
        else:
            qry = filter_friends(qry)
        if request.params.get('playlist'):
            qry = qry.filter(Playlist.id == request.params.get('playlist'))

        qry = qry.order_by([Album.artistsort, Album.album, Song.tracknumber])
        results = qry.all()
        return self._build_json(results)

    @jsonify
    def albums(self):
        qry = Session.query(Album).join(['songs', 'files', 'owners', 'user'])
        qry = filter_friends(qry)

        if request.params.get('artist'):
            qry = qry.filter(Album.artist == request.params.get('artist'))
        qry = qry.order_by([Album.artistsort, Album.album])
        results = qry.all()
        return self._build_json(results)
        
    @jsonify
    def artists(self):
        qry = Session.query(Artist).join(['songs','files','owners', 'user'])
        qry = filter_friends(qry)
        qry = qry.order_by(Artist.artistsort)
        results = qry.all()
        return self._build_json(results)
        
    @jsonify
    def friends(self):
        dtype = request.params.get('type')
        userStore = session['fbfriends']
        data=facebook.users.getInfo(userStore)

        # TODO: Join this with the owners table and make sure they actually own
        # files
        qry = Session.query(User)
        cond = or_()
        for friend in data:
            cond.append(User.fbid == friend['uid'])
        qry = qry.filter(cond)
        qry = qry.order_by(User.fbid)
        results = qry.all()

        def _intersect(item):
            if len(results)>0:
                if results[0].fbid == item['uid']:
                    del results[0]
                    return True
                else:
                    return False
            else:
                return False

        data = sorted(data, key=itemgetter('uid'))
        data = filter(_intersect, data)

        for row in data:
            row['fbid']=row['uid']
            row['friend'] = row['name']
            row['type']=dtype
        return {'success':True, 'data':data}

    @jsonify
    def playlists(self):
        qry = Session.query(Playlist).join('owner')
        qry = filter_friends(qry)
        qry = qry.order_by(Playlist.name)
        results = qry.all()
        return self._build_json(results)

    @jsonify
    def playlistsongs(self):
        qry = Session.query(PlaylistSong).join('playlist').reset_joinpoint(). \
            join('album').reset_joinpoint().join(['files', 'owners', 'user'])
        qry = filter_friends(qry)
        qry = qry.filter(Playlist.playlistid == request.params.get('playlist'))

        qry = qry.order_by(PlaylistSong.songindex)
        results = qry.all()
        return self._build_json(results)

