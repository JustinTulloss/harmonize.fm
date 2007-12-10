from masterapp.lib.base import *
from masterapp.model import Songs, Albums, Friends, Session
from masterapp.model import songs_table, albums_table, friend_table
from masterapp.lib.profile import Profile
from sqlalchemy import sql
import pylons

#The types we can search for an their associated returned fields
#TODO: This currently defines both valid filters and the schema.
#      Make a new struct that defines valid filters
schema = {
    'album': (
        'artist',
        'year', 
        'genre', 
        'album', 
        'album_id', 
        'totaltracks',
        'albumlength',
        #'ownerid',
        'recs'),
    'artist':(
        'artist',
        'totalalbums',
        'totaltracks',
        'artistlength',
        #'ownerid',
        'recs'),
    'song':(
        'title',
        'artist',
        'songid',
        'year',
        'genre',
        'album',
        'tracknumber',
        'recs',
        #'ownerid',
        'filename'),
    'genre':(
        'genre',
        'numartists',
        'exartists',
        #'ownerid'
        ),
    'friend':(
        'friend',
        'name',
        'numartists',
        'numalbums',
        'likesartists'),
    'fid':(),
    'album_id':()
}

class PlayerController(BaseController):
    def index(self):
        c.profile = Profile()
        return render('/player.mako')
    
    def enqueue(self):
        return request.POST["id"]
            
    def settings(self):
        return "This is the change settings form!"
    
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
            return self.get_songs(type,artist,album,friend,genre) 
        elif type == 'friend':
            return self.get_friends()
        elif type == 'queue':
            return self.get_songs(type,artist,album,friend,genre)
        

    def _qualify_sql(self):
        qualifiers = sql.and_()
        for key,param in request.params.iteritems():
            if(schema.has_key(key)):
                qualifiers.append(getattr(songs_table.c, key)==param)
        return qualifiers
        
    def get_albums(self):
        qualifiers = self._qualify_sql()
        if (len(qualifiers)==0):
            qualifiers = songs_table.c.album_id == albums_table.c.id
        else:
            qualifiers.append(songs_table.c.album_id == albums_table.c.id)

        qry = sql.select(
            [
                songs_table, 
                albums_table, 
                albums_table.c.id.label('albumid'), 
                sql.func.sum(songs_table.c.recommendations).label('recs'),
                sql.func.sum(songs_table.c.length).label('albumlength')
            ],qualifiers).distinct().group_by(albums_table.c.id)

        results = Session.execute(qry)
        return self.build_json(results)

    def build_json(self, results):
        dtype = request.params.get('type')
        json = { "data": []}
        for row in results:
            expanded = dict([(field, row[field]) for field in schema[dtype]])
            json['data'].append(expanded)
            json['data'][len(json['data'])-1]['type']=dtype
        return json  
        
    def get_songs(self, type, myartist, myalbum, myfid, mygenre):     
        qualifiers = self._qualify_sql()

        if (len(qualifiers)==0):
            qualifiers = songs_table.c.album_id == albums_table.c.id
        else:
            qualifiers.append(songs_table.c.album_id == albums_table.c.id)

        qry = sql.select(
            [
                songs_table, 
                albums_table, 
                albums_table.c.id.label('albumid'), 
                songs_table.c.id.label('songid'), 
                songs_table.c.recommendations.label('recs')
            ],qualifiers)

        results = Session.execute(qry)
        return self.build_json(results)

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
        tuples = Session.execute("select friend.id as friendid,name, count(distinct artist) as numartists, \
                    count(distinct albums.id) as numalbums from friend,songs,albums where friend.id = songs.owner_id and \
                    songs.album_id = albums.id group by friendid",mapper=Friends).fetchall()
        json = {
                 "data" : [
                        {
                         "type":"friend",
                         "friend": row.friendid,
                         "name": "%s" % row.name,
                         "numartists": row.numartists,
                         "numalbums": row.numalbums,
                         "likesartists": self.get_likesartists(row.friendid)
                        } for row in tuples
                    ]
               }   
        return json          
        
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
