# vim:expandtab:smarttab
import logging
import cjson
import random
from masterapp.lib.base import *
from masterapp.lib.decorators import *
from masterapp.lib.fbauth import (
    ensure_fb_session, 
    filter_friends,
    filter_any_friend
)
from sqlalchemy import sql, or_, and_
from masterapp import model
from masterapp.config.schema import dbfields
from masterapp.model import (
    Song,
    Album, 
    Artist, 
    Owner,
    SongOwner,
    RemovedOwner,
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
from masterapp.lib.snippets import build_json, get_user

from ecs import *
import xml.dom.minidom
from masterapp.lib.amazon import *

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
            'next_radio_song': self.next_radio_song
        }
        self.id_map = {
            'artist': Artist.id,
            'album': Album.id,
            'song': Song.id,
            'friend': User.id,
            'playlist': Playlist.id
        }

    def __before__(self):
        ensure_fb_session()

    def _apply_offset(self, qry):
        if request.params.get('start') and request.params.get('limit'):
            qry = qry[int(request.params['start']):int(request.params['limit'])]
        return qry

    @cjsonify
    def _json_failure(self, error='A problem occurred requesting your data'):
        return {'success': False, 'error': error, 'data':[]}

    def index(self):
        type = request.params.get('type')
        handler=self.datahandlers.get(type, self._json_failure)
        return handler()

    @pass_user
    def remove(self, user, **kwargs):
        type = kwargs['type']
        id = kwargs['id']
        if not type or not id:
            abort(400)
        songs = user.song_query.filter(self.id_map[type]==id)
        if not songs:
            abort(404)
        for song in songs:
            user.remove_song(song)

        try:
            Session.commit()
        except Exception, e:
            Session.rollback()
            raise
        return '1'

    @cjsonify
    @d_build_json
    @pass_user
    def songs(self, user, **kwargs):
        qry = user.song_query
        
        sort = [Artist.sort, Album.title, Song.tracknumber]
        if request.params.get('song'):
            qry = qry.filter(Song.id == request.params.get('song'))
        elif request.params.get('album'):
            qry = qry.filter(Album.id== request.params.get('album'))
            sort = [Song.tracknumber]
        elif request.params.get('playlist'):
            qry = qry.reset_joinpoint().join(Song.playlistsongs).\
                filter(PlaylistSong.playlistid == 
                        int(request.params.get('playlist'))).\
                order_by(PlaylistSong.songindex)
        elif request.params.get('artist'):
            qry = qry.filter(Artist.id == request.params.get('artist'))

        qry = qry.order_by(sort)
        qry = self._apply_offset(qry)
        return qry

    @cjsonify
    @d_build_json
    @pass_user
    def albums(self, user, **kwargs):
        qry = user.album_query
        if request.params.get('artist'):
            qry = qry.filter(Artist.id == request.params.get('artist'))
        qry = qry.order_by([Artist.sort, Album.title])
        qry = self._apply_offset(qry)
        results = qry
        return results
        
    @cjsonify
    @d_build_json
    @pass_user
    def artists(self, user, **kwags):
        qry = user.artist_query
        qry = qry.order_by(Artist.sort)
        qry = self._apply_offset(qry)
        return qry
        
    @cjsonify
    @pass_user
    def friends(self, user, **kwargs):
        dtype = request.params.get('type')
        if request.params.get('all') == 'true':
            data = user.allfriends
        elif request.params.has_key('nonapp') and request.params.get('nonapp') == 'true':
            data = []
            friendfbids = [friend.fbid for friend in user.friends]
            
            for friend in user.allfriends:
                # check to see if the user is part of the database yet
                if not friend['uid'] in friendfbids:
                    data.append(friend)
        else:
            data = []
            for dbfriend in user.friends:
                data.append({
                    'Friend_name': dbfriend.name,
                    'Friend_id': dbfriend.id,
                    'Friend_songcount': dbfriend.songcount,
                    'Friend_albumcount': dbfriend.albumcount,
                    'Friend_tastes': dbfriend.musictastes,
                    'type': 'friend'
                })

            data = sorted(data, key=itemgetter('Friend_name'))
        return {'success':True, 'data':data}

    @cjsonify
    @d_build_json
    @pass_user
    def playlists(self, user, **kwargs):
        qry = Session.query(Playlist.ownerid.label('Friend_id'), 
                            *dbfields['playlist']).\
                join(Playlist.owner).\
                filter(Playlist.ownerid == user.id).order_by(Playlist.name)
        return qry.all()
        
    def album(self, id):
        if not id:
            abort(400)
        user = get_user()
        album = user.get_album_by_id(id)
        if not album:
            abort(404)
        json = build_json([album])
        json['data'][0]['type'] = 'album'
        return cjson.encode(json)
        
    def playlist(self, id):
        if not id:
            abort(400)
        user = get_user()
        playlist = user.get_playlist_by_id(id)
        if not playlist:
            abort(404)
        json = build_json([playlist])
        json['data'][0]['type'] = 'playlist'
        return cjson.encode(json)

    def song(self, id):
        if not id:
            abort(400)
        user = get_user()
        song = user.get_song_by_id(id)
        if not song:
            abort(404)
        json = build_json([song])
        json['data'][0]['type'] = 'song'
        return cjson.encode(json)

    @cjsonify
    @d_build_json
    @pass_user
    def next_radio_song(self,user, **kwargs):
        #TODO: replace this with recommendations
        
        #songlist is a list where each element is a song id.
        #this will be used to generate a random number between 0 and the number
        #of songs (the length of the list)        
        songlist = []
        data = Session.query(*dbfields['song']).\
            join(Song.album).reset_joinpoint().\
            join(Song.artist).reset_joinpoint().\
            join(SongOwner)
        for friend in user.friends:
            # grab each users songs and append their song_ids to songlist
            temp = data.filter(SongOwner.uid == friend.id)
            for record in temp:
                songlist.append(record.Song_id)
        
        num_songs = len(songlist)
        if num_songs == 0:
            abort(404)
        song_index = random.randint(0,num_songs-1)
        song_id = songlist[song_index]
        
        #now grab the actual song data based on the song_id
        song = data.filter(Song.id == song_id)
        return song
        
