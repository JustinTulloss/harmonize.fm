# vim:expandtab:smarttab
import logging
import cjson
import random
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
    SongOwner,
    File, 
    Session, 
    User, 
    Playlist, 
    PlaylistSong,
    Spotlight
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
            'playlistsong': self.playlistsongs,
            'next_radio_song': self.next_radio_song,
            'find_spotlight_by_id': self.find_spotlight_by_id
        }

    def __before__(self):
        ensure_fb_session()

    def _pass_user(func):
        def pass_user(self, *args, **kwargs):
            user = self._get_user()
            return func(self, user, *args, **kwargs)
        return pass_user

    def _get_user(self):
        friendid = request.params.get('friend')
        if not friendid:
            user = Session.query(User).get(session['userid'])
        else:
            # TODO: Make sure they're friends
            user = Session.query(User).get(friendid)
        return user

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
        json['success']=True
        return json
        

    def _build_json(func):
        def wrapper(self, *args):
            return self._build(func(self, *args))
        return wrapper
        
    def _apply_offset(self, qry):
        if request.params.has_key('start') and request.params.has_key('limit'):
            if not (request.params.get('start') == '' or request.params.get('limit') == ''):            
                start = int(request.params.get('start'))
                limit = int(request.params.get('limit'))
                qry = qry.limit(limit)
                qry = qry.offset(start)
        return qry

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
        qry = self._apply_offset(qry)
        return qry

    @cjsonify
    @_build_json
    @_pass_user
    def albums(self, user):
        qry = user.album_query
        if request.params.get('artist'):
            qry = qry.filter(Artist.id == request.params.get('artist'))
        qry = qry.order_by([Artist.sort, Album.title])
        qry = self._apply_offset(qry)
        results = qry.all()
        return results
        
    @cjsonify
    @_build_json
    @_pass_user
    def artists(self, user):
        qry = user.artist_query
        qry = qry.order_by(Artist.sort)
        qry = self._apply_offset(qry)
        return qry.all()
        
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
        #qry = self._apply_offset(qry)
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
        qry = self._apply_offset(qry)
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
        qry = self._apply_offset(qry)
        results = qry.all()
        return self._build_json(results, 'playlistsong')

    def album(self, id):
        user = self._get_user()
        album = user.get_album_by_id(id)
        json = self._build([album])
        json['data'][0]['type'] = 'album'
        return cjson.encode(json)

    @cjsonify
    @_build_json
    @_pass_user
    def next_radio_song(self,user):
        #todo: replace this with recommendations
        
        userStore = session['fbfriends']
        fbids = []
        for user in userStore:
            fbids.append(user)
        #songlist is a list where each element is a song id.
        #this will be used to generate a random number between 0 and the number
        #of songs (the length of the list)        
        songlist = []
        data = Session.query(*dbfields['song']).join(Song.album).reset_joinpoint().join(Song.artist).reset_joinpoint().join(SongOwner,User)
        for uid in fbids:
            # grab each users songs and append their song_ids to songlist
            temp = data.filter(User.fbid == uid)
            for record in temp:
                songlist.append(record.Song_id)
        
        num_songs = len(songlist)
        song_index = random.randint(0,num_songs-1)
        song_id = songlist[song_index]
        
        #now grab the actual song data based on the song_id
        song = data.filter(Song.id == song_id)
        return song
        
    @cjsonify
    @_build_json
    @_pass_user
    def find_spotlight_by_id(self,user):
        if request.params.get('id') != '':
            qry = Session.query(*dbfields['spotlight']).join(Spotlight.album).join(Album.artist).filter(Spotlight.id == request.params.get('id')).filter(User.id == user.id)
            return qry.all()
        else:
            return "False"
        

    # right now this only returns true or false
    # depending on whether or not a spotlight exists
    # for the album    
    def find_spotlight_by_album(self):
        if not request.params.has_key('album_id'):
            return "False"
        
        album = Session.query(Album).filter(Album.id == request.params['album_id'])
        if album.first():
            qry = Session.query(Spotlight).filter(Spotlight.albumid == album[0].id).filter(Spotlight.uid == self._get_user().id).filter(Spotlight.active == 1)
            if qry.first():
                return "True"
            else:
                return "False"
            
        else:
            return "False"
        
        
    
