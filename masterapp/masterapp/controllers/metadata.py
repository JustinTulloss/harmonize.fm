# vim:expandtab:smarttab
import logging
import cjson
import random
from masterapp.lib.base import *
from masterapp.lib.decorators import *
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

    @cjsonify
    def _json_failure(self, error='A problem occurred requesting your data'):
        return {'success': False, 'error': error, 'data':[]}

    def index(self):
        type = request.params.get('type')
        handler=self.datahandlers.get(type, self._json_failure)
        return handler()

    @cjsonify
    @d_build_json
    @_pass_user
    def songs(self, user):
        qry = user.song_query

        sort = [Artist.sort, Album.title, Song.tracknumber]
        if request.params.get('album'):
            qry = qry.filter(Album.id== request.params.get('album'))
            sort = [Song.tracknumber]
        elif request.params.get('artist'):
            qry = qry.filter(Artist.id == request.params.get('artist'))
        elif request.params.get('playlist'):
            qry = qry.reset_joinpoint().join(Song.playlistsongs).\
                filter(PlaylistSong.playlistid == 
                        int(request.params['playlist'])).\
                order_by(PlaylistSong.songindex)

        qry = qry.order_by(sort)
        return qry

    @cjsonify
    @d_build_json
    @_pass_user
    def albums(self, user):
        qry = user.album_query
        if request.params.get('artist'):
            qry = qry.filter(Artist.id == request.params.get('artist'))
        qry = qry.order_by([Artist.sort, Album.title])
        results = qry.all()
        return results
        
    @cjsonify
    @d_build_json
    @_pass_user
    def artists(self, user):
        qry = user.artist_query
        qry = qry.order_by(Artist.sort)
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
    @d_build_json
    @_pass_user
    def playlists(self, user):
        qry = Session.query(*dbfields['playlist']).join(Playlist.owner).\
               filter(Playlist.ownerid == user.id).order_by(Playlist.name)
        return qry.all()

    def album(self, id):
        user = self._get_user()
        album = user.get_album_by_id(id)
        json = self.build_json([album])
        json['data'][0]['type'] = 'album'
        return cjson.encode(json)

    @cjsonify
    @d_build_json
    @_pass_user
    def next_radio_song(self,user):
        #todo: replace this with actual randomizing
        #      and correct record returns
        
        userStore = session['fbfriends']
        users=facebook.users.getInfo(userStore)
        fbids = []
        for user in users:
            fbids.append(user['uid'])
        #songlist is a list where each element is a song id.
        #this will be used to generate a random number between 0 and the number
        #of songs (the length of the list)        
        songlist = []
        data = Session.query(*dbfields['song']).join(Song.album).reset_joinpoint().join(Song.artist).reset_joinpoint().join(File,Owner,User)
        for uid in fbids:
            # grab each users songs and append their song_ids to songlist
            temp = data.filter(User.fbid == uid)
            for record in temp:
                songlist.append(record.Song_id)
        num_songs = len(songlist)
        song_index = random.randint(0,num_songs) #replace with a random number generator
        song_id = songlist[song_index]
        
        #now grab the actual song data based on the song_id
        song = data.filter(Song.id == song_id)
        #song = song.group_by(Song)
        #song = song.all()
        return song
