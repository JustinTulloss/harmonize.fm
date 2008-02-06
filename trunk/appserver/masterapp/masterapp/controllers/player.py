import logging
import S3
from masterapp.lib.base import *
from masterapp.model import Song, Album, Artist, Owner, File, Session, TagData
from masterapp.model import songs_table, albums_table, files_table, owners_table
from masterapp.lib.profile import Profile
from sqlalchemy import sql, or_
from facebook import FacebookError
from facebook.wsgi import facebook
from pylons import config
import pylons

log = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = '17G635SNK33G1Y7NZ2R2'
AWS_SECRET_ACCESS_KEY = 'PHDzFig4NYRJoKKW/FerfhojljL+sbNyYB9bEpHs'

class PlayerController(BaseController):
    def __before__(self):
        action = request.environ['pylons.routes_dict']['action']
        c.facebook = facebook
        if not session.has_key('fbsession'):
            if facebook.check_session(request):
                session['fbsession']=facebook.session_key
                session['fbuid']=facebook.uid
                session['fbfriends']=facebook.friends.getAppUsers()
                session['fbfriends'].append(facebook.uid)
                session.save()
            else:
                next = '%s' % (request.environ['PATH_INFO'])
                if request.environ['QUERY_STRING'] != '':
                    next = '%s?%s' % (next, request.environ['QUERY_STRING'])
                url = facebook.get_login_url(next=next, canvas=False)
                facebook.redirect_to(url)
        else: 
            facebook.session_key = session['fbsession']
            facebook.uid = session['fbuid']

    def index(self):
        c.profile = Profile()
        return render('/player.mako')
    
    def enqueue(self):
        return request.POST["id"]
            
    def settings(self):
        return "This is the change settings form!"
    
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
                    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
                qsgen.set_expires_in(song.length*3)
                return qsgen.get('music.rubiconmusicplayer.com', file.sha)
        #if we get here, all files are in use! Damn it!
        return False

    @jsonify    
    def get_data(self):
        type = request.params.get('type')
        artist = request.params.get('artist')
        album = request.params.get('album')
        friend = request.params.get('friend')
        genre = request.params.get('genre')
        if type == 'album': 
            return self.get_albums()
        elif type == 'artist':
            return self.get_artists()
        elif type == 'genre':
            return self.get_genres(friend)
        elif type == 'song':
            return self.get_songs()
        elif type == 'friend':
            return self.get_friends()
        elif type == 'queue':
            return self.get_songs(type,artist,album,friend,genre)
        
        return qry
        
    def _build_json(self, results):
        dtype = request.params.get('type')
        json = { "data": []}
        for row in results:
            expanded = {}
            for field in row.c.keys():
                expanded[field] = getattr(row, field)
            json['data'].append(expanded)
            json['data'][len(json['data'])-1]['type']=dtype
        return json

    def _filter_friends(self, qry):
        # Friends filter
        fbclause = sql.expression.or_()
        for friend in session['fbfriends']:
            fbclause.append(Owner.fbid==friend)
        qry=qry.filter(fbclause)
        return qry

    def get_albums(self):
        qry = Session.query(Album).join(['songs', 'files', 'owners'])
        qry = self._filter_friends(qry)

        if not request.params.get('artist') == None:
            qry=qry.filter(Album.artist == request.params.get('artist'))
        if not request.params.get('friend') == None:
            qry=qry.filter(Owner.fbid == request.params.get('friend'))
        results = qry.all()
        return self._build_json(results)
        
    def get_songs(self):
        qry = Session.query(Song).join('album').reset_joinpoint().join(['files', 'owners'])
        qry = self._filter_friends(qry)

        if not request.params.get('artist') == None:
            qry=qry.filter(Album.artist == request.params.get('artist'))
        if not request.params.get('album') == None:
            qry=qry.filter(Album.albumid== request.params.get('album'))
        if not request.params.get('friend') == None:
            qry=qry.filter(Owner.fbid == request.params.get('friend'))

        results = qry.all()
        return self._build_json(results)

    def get_artists(self):
        qry = Session.query(Artist).join(['songs','files','owners'])
        qry=self._filter_friends(qry)
        if not request.params.get('friend') == None:
            qry=qry.filter(Owner.fbid == request.params.get('friend'))
        results = qry.all()
        return self._build_json(results)
        
    def get_friends(self):
        dtype = request.params.get('type')
        userStore = session['fbfriends']
        data=facebook.users.getInfo(userStore)
        for row in data:
            row['fbid']=row['uid']
            row['type']=dtype
        return dict(data=data)
	
    @jsonify
    def get_checked_friends(self):
        userStore = facebook.friends.getAppUsers()
        userList = facebook.users.getInfo(userStore)
        for user in userList:
            user["checked"]=self.get_active(user["uid"])
            #~ user['name']=user['name']
            #~ user['uid']=user['uid']
        
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

    def get_exartists(self,mygenre):
        albums = Session.execute("select distinct artist from songs,albums where songs.album_id = albums.id and albums.genre='%s' limit 3"
            % mygenre, mapper=Songs)
        similar = ""
        for song in albums:
            similar += song.artist + ", "
        return similar      

    def get_likesartists(self,myfid):
        albums = Session.execute("select distinct artist from songs,friend where songs.owner_id = friend.id and friend.id='%s' limit 3"
            % myfid, mapper=Friends)
        likes = ""
        for song in albums:
            likes += song.artist + ", "
        return likes            

    def home(self):
        pass
