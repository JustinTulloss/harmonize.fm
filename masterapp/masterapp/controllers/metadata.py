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
            'next_radio_song': self.next_radio_song,
            'find_spotlight_by_id': self.find_spotlight_by_id
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
        songs = user.song_query.filter(self.id_map[type]==id)
        for song in songs:
            movedowner = RemovedOwner(
                song=Session.query(Song).get(song.Song_id),
                user=user
            )
            Session.add(movedowner)

            owner = Session.query(SongOwner).\
                filter(SongOwner.songid == song.Song_id).\
                filter(SongOwner.user == user).first()
            Session.delete(owner) 

        try:
            Session.commit()
        except Exception, e:
            Session.rollback()
            raise


    @cjsonify
    @d_build_json
    @pass_user
    def songs(self, user):
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
    def albums(self, user):
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
    def artists(self, user):
        qry = user.artist_query
        qry = qry.order_by(Artist.sort)
        qry = self._apply_offset(qry)
        return qry
        
    @cjsonify
    @pass_user
    def friends(self, user):
        dtype = request.params.get('type')
        if request.params.get('all') == 'true':
            data = user.allfriends
        else:
            data = user.friends
            qry = Session.query(User).join(User.owners)
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
    @d_build_json
    @pass_user
    def playlists(self, user):
        qry = Session.query(Playlist.ownerid.label('Friend_id'), 
                            *dbfields['playlist']).\
                join(Playlist.owner).\
                filter(Playlist.ownerid == user.id).order_by(Playlist.name)
        return qry.all()
        
    def album(self, id):
        user = get_user()
        album = user.get_album_by_id(id)
        json = build_json([album])
        json['data'][0]['type'] = 'album'
        return cjson.encode(json)
        
    def playlist(self, id):
        user = get_user()
        playlist = user.get_playlist_by_id(id)
        json = build_json([playlist])
        json['data'][0]['type'] = 'playlist'
        return cjson.encode(json)

    @cjsonify
    @d_build_json
    @pass_user
    def next_radio_song(self,user, **kwargs):
        #todo: replace this with recommendations
        
        fbids = []
        for friend in user.friends:
            fbids.append(friend['uid'])
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
    @d_build_json
    @pass_user
    def find_spotlight_by_id(self,user, **kwargs):
        if request.params.get('id') != '':
            qry = Session.query(*dbfields['spotlight']).join(Spotlight.album).join(Album.artist).filter(Spotlight.id == request.params.get('id')).filter(User.id == user.id)
            return qry.all()
        else:
            return "False"
        
    @cjsonify
    @d_build_json
    @pass_user
    def find_playlist_spotlight_by_id(self, user, **kwargs):
        if request.params.get('id') != '':
            qry = Session.query(*dbfields['spotlight']).join(Spotlight.playlist).filter(Spotlight.id == request.params.get('id')).filter(User.id == user.id).limit(1)
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
            qry = Session.query(Spotlight).filter(and_(
                    Spotlight.albumid == album[0].id,
                    Spotlight.uid == get_user().id,
                    Spotlight.active == 1))
            if qry.first():
                return "True"
            else:
                return "False"
            
        else:
            return "False"

    #this returns true or false depending on whether or not the spotlight already exists
    def find_spotlight_by_playlist(self):
        if not request.params.has_key('playlist_id'):
            return "False"
        
        playlist = Session.query(Playlist).filter(Playlist.id == request.params['playlist_id'])
        if playlist.first():
            qry = Session.query(Spotlight).filter(and_(
                    Spotlight.playlistid == playlist[0].id,
                    Spotlight.uid == get_user().id,
                    Spotlight.active == 1))
            if qry.first():
                return "True"
            else:
                return "False"
            
        else:
            return "False"

    def get_asin(self):
        if not request.params.has_key('id'):
            return "0"
        return get_asin(request.params.get('id'),'song')
