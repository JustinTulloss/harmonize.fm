# vim:expandtab:smarttab
import logging
import S3
from masterapp.lib.base import *
from masterapp.model import \
    Song, Album, Artist, Owner, File, Session, User, Playlist
from masterapp.lib.profile import Profile
from sqlalchemy import sql, or_
from facebook import FacebookError
from facebook.wsgi import facebook
from pylons import config
import pylons

log = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = '17G635SNK33G1Y7NZ2R2'
AWS_SECRET_ACCESS_KEY = 'PHDzFig4NYRJoKKW/FerfhojljL+sbNyYB9bEpHs'

DEFAULT_EXPIRATION = 5 #minutes to expire a song access URL

class PlayerController(BaseController):
    def __init__(self):
        super(PlayerController, self).__init__()
        self.datahandlers = {
            'artist': self._get_artists,
            'album': self._get_albums,
            'song':self._get_songs,
            'playlist': self._get_playlists,
            'friend': self._get_friends
        }


    def __before__(self):
        action = request.environ['pylons.routes_dict']['action']
        c.facebook = facebook
        if not session.has_key('fbsession'):
            if facebook.check_session(request):
                session['fbsession']=facebook.session_key
                session['fbuid']=facebook.uid
                session['user'] = Session.query(User).filter(
                    User.fbid==facebook.uid).first()
                session['fbfriends']=facebook.friends.getAppUsers()
                session['fbfriends'].append(facebook.uid)
                session.save()
            else:
                next = '%s' % (request.environ['PATH_INFO'])
                url = facebook.get_login_url(next=next, canvas=False)
                facebook.redirect_to(url)
        else: 
            facebook.session_key = session['fbsession']
            facebook.uid = session['fbuid']

    def index(self):
        c.profile = Profile()
        return render('/player.mako')
    
    def get_song_url(self, id):
        """
        Fetches the S3 authenticated url of a song.
        Right now, this provides no security at all since anybody with a 
        facebook login can request a url. However, now it's possible to track
        who's doing what, and if we can come up with conclusive proof that
        somebody is stealing music through our logs, we can ban them.
        """
        song = Session.query(Song).filter(Song.id==id).first()
        for file in song.files:
            if file.inuse == False:
                qsgen = S3.QueryStringAuthGenerator(
                    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
                )
                if song.length>0:
                    qsgen.set_expires_in(song.length*3)
                else:
                    qsgen.set_expires_in(DEFAULT_EXPIRATION*60)

                return qsgen.get('music.rubiconmusicplayer.com', file.sha)
        #if we get here, all files are in use! Damn it!
        return False

    @jsonify    
    def get_data(self):
        type = request.params.get('type')
        handler=self.datahandlers[type]
        return handler()

    # TODO: I don't want to think about it now, but these two functions would
    # be cleaner if they were recursive. Do that.
    def _expand_row(self, sqlrow):
        expanded = {}
        for field in sqlrow.c.keys():
            expanded[field] = getattr(sqlrow, field)
        return expanded

    def _build_json(self, results):
        dtype = request.params.get('type')
        json = { "data": []}
        for row in results:
            if type(row) == tuple: #Is this really dirty? it feels dirty
                expanded = {}
                for entity in row:
                    expanded.update(self._expand_row(entity))
                json['data'].append(expanded)
            else:
                json['data'].append(self._expand_row(row))
            json['data'][len(json['data'])-1]['type']=dtype
        return json

    def _filter_friends(self, qry):
        """
        This function creates a giant SQL OR statement that restricts
        the files you can select from to files owned by any of your friends.
        It assumes you are joined to the Users table.
        """
        fbclause = sql.expression.or_()
        for friend in session['fbfriends']:
            fbclause.append(User.fbid==friend)
        qry = qry.filter(fbclause)
        return qry

    def _get_songs(self):
        qry = Session.query(Song).join('album').\
            reset_joinpoint().join(['files', 'owners', 'user']).add_entity(Album)
        qry = self._filter_friends(qry)

        if not request.params.get('artist') == None:
            qry = qry.filter(Album.artist == request.params.get('artist'))
        if not request.params.get('album') == None:
            qry = qry.filter(Album.albumid== request.params.get('album'))
        if not request.params.get('friend') == None:
            qry = qry.filter(User.id == request.params.get('friend'))

        qry = qry.order_by([Album.artistsort, Album.album, Song.tracknumber])
        results = qry.all()
        return self._build_json(results)

    def _get_albums(self):
        qry = Session.query(Album).join(['songs', 'files', 'owners', 'user'])
        qry = self._filter_friends(qry)

        if not request.params.get('artist') == None:
            qry = qry.filter(Album.artist == request.params.get('artist'))
        if not request.params.get('friend') == None:
            qry = qry.filter(User.id == request.params.get('friend'))
        qry = qry.order_by([Album.artistsort, Album.album])
        results = qry.all()
        return self._build_json(results)
        
    def _get_artists(self):
        qry = Session.query(Artist).join(['songs','files','owners', 'user'])
        qry = self._filter_friends(qry)
        if not request.params.get('friend') == None:
            qry = qry.filter(User.id == request.params.get('friend'))
        qry = qry.order_by(Artist.artistsort)
        results = qry.all()
        return self._build_json(results)
        
    def _get_friends(self):
        dtype = request.params.get('type')
        userStore = session['fbfriends']
        data=facebook.users.getInfo(userStore)
        for row in data:
            row['fbid']=row['uid']
            row['type']=dtype
        return dict(data=data)

    def _get_playlists(self):
        qry = Session.query(Playlist).join('owner')
        qry = qry.filter(User.id == session['user'].id)
        qry = qry.order_by(Playlist.name)
        results = qry.all()
        return self._build_json(results)
	
    @jsonify
    def get_checked_friends(self):
        userStore = facebook.friends.getAppUsers()
        userList = facebook.users.getInfo(userStore)
        for user in userList:
            user["checked"]=self.get_active(user["uid"])
        
        userDict = dict(data = userList) 
        return userDict
	
    def get_active(self, uid):
        if uid == 1908861:
            return True	
        else:
            return False
	
    def add_rec(self):
        type = request.params.get('type')
        myid = request.params.get('id')
        if type == 'album': #recommending entire album
            myalbum = Session.query(Songs).filter_by(album_id=myid).all()
            for mysong in myalbum:
                mysong.recommendations = mysong.recommendations + 1
        elif type == 'song': #individual song
            mysong = Session.query(Songs).filter_by(id=myid).one()
            mysong.recommendations = mysong.recommendations + 1
        elif type == 'artist':
            myalbum = Session.query(Songs).filter_by(artist=myid).all()
            for mysong in myalbum:
                mysong.recommendations = mysong.recommendations + 1
        else:
            return "Failure"
        #Session.save(mysong)  - this should work and use less resources...
        Session.commit()
        return "Success"    
