import logging
import S3
from masterapp.lib.base import *
from masterapp.model import Song, Album, Owner, File, Session, TagData
from masterapp.model import songs_table, albums_table, files_table, owners_table
from masterapp.lib.profile import Profile
from sqlalchemy import sql
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
            return self.get_artists(friend,genre)
        elif type == 'genre':
            return self.get_genres(friend)
        elif type == 'song':
            return self.get_songs()
        elif type == 'friend':
            return self.get_friends()
        elif type == 'queue':
            return self.get_songs(type,artist,album,friend,genre)
        
    def _qualify_sql(self, qry):
        if not request.params.get('artist') == None:
            qry.filter(TagData.artist == request.params.get('artist'))
        if not request.params.get('album') == None:
            qry.filter(TagData.album == request.params.get('album'))
        if not request.params.get('friend') == None:
            qry.filter(TagData.owner.fbid == request.params.get('friend'))
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

    def get_albums(self):
        qry = Session.query(TagData)
        qry = self._qualify_sql(qry)
        results = qry.all()
        return self._build_json(results)
        
    def get_songs(self):
        qry = Session.query(TagData)
        qry = self._qualify_sql(qry)
        results = qry.all()
        return self._build_json(results)

    def get_artists(self, myfid, mygenre):
        if myfid == None:
            if mygenre == None: #dont filter on anything
                tuples = Session.execute("select artist, count( distinct album_id ) as totalalbums,count(*) as totaltracks, \
                    sum(recommendations) as recs from songs group by artist",mapper=Songs).fetchall()
            else: #filter only on genre
                tuples = Session.execute("select artist, count( distinct album_id ) as totalalbums,count(*) as totaltracks, \
                    sum(recommendations) as recs from songs,albums where songs.album_id = albums.id and genre='%s' \
                    group by artist" % mygenre,mapper=Songs).fetchall()                
        else:
            if mygenre == None: #filter on fid only
                tuples = Session.execute("select artist, count( distinct album_id ) as totalalbums,count(*) as totaltracks, \
                    sum(recommendations) as recs from songs where owner_id = %s group by artist" % myfid, mapper=Songs).fetchall()
            else:
                tuples = Session.execute("select artist, count( distinct album_id ) as totalalbums,count(*) as totaltracks, \
                    sum(recommendations) as recs from songs,albums where songs.album_id = albums.id and genre = %s and \
                    owner_id=%s group by artist" % (mygenre,myfid),mapper=Songs).fetchall()
        #fetchall returns a list
        #row[0] is the bare artist
        json = {  
                 "data" : [
                        {
                         "type":"artist",
                         "artist": "%s" % row.artist,
                         "totalalbums": row.totalalbums,
                         "totaltracks": row.totaltracks,
                         "artistlength": "%s" % self.get_album_length(None,row.artist),                         
                         "ownerid": myfid,
                         "recs": row.recs
                        } for row in tuples
                    ]
               }   
        return json          
        
    def get_genres(self, myfid):
        if myfid == None:
            tuples = Session.execute("select genre,count(distinct artist) as numartists,count(distinct albums.id)\
                        as numalbums from albums,songs where albums.id = songs.album_id group by genre",mapper=Albums).fetchall()
        else:
            tuples = Session.execute("select genre,count(distinct artist) as numartists,count(distinct albums.id)\
                        as numalbums from albums,songs where albums.id = songs.album_id and owner_id=%s group by genre" % myfid,mapper=Albums).fetchall()
        #fetchall returns a list
        # row[0] is the bare genre
        json = { 
                 "data" : [
                        {
                         "type":"genre",
                         "genre": "%s" % row.genre,
                         "numartists": "%s" % row.numartists,
                         "numalbums": "%s" % row.numalbums,
                         "exartists": "%s" % self.get_exartists(row.genre),
                         "ownerid": myfid
                        } for row in tuples
                    ]
               }   
        return json  
        
    def get_friends(self):
        userStore = facebook.friends.getAppUsers()
        return dict(data = facebook.users.getInfo(userStore))
	
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
        
    
        
    def get_album_length(self,albumid,myartist):
        if albumid == None:
            album = Session.query(Songs).filter_by(artist=myartist).all()
        else:
            album = Session.query(Songs).filter_by(album_id=albumid).all()
        
        totalsecs = 0
        totalmins = 0
        for song in album:
            #Assuming length of a song is string in minutes:secs format
            mylist = song.length.split(":")
            totalsecs += int(mylist[1])
            totalmins += int(mylist[0])
        extramin = totalsecs / 60
        secs = totalsecs % 60
        min = totalmins + extramin
        return ("%s:%s" % (min,secs)) 
        
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
