from masterapp.lib.base import *
from masterapp.model import Songs, Albums, Friends, Session
from masterapp.model import songs_table, albums_table, friend_table
from masterapp.lib.profile import Profile
from sqlalchemy import sql
import pylons

#The types we can search for an their associated returned fields
schema = {
    'album': (
        'artist',
        'year', 
        'genre', 
        'album_title', 
        'albumid', 
        'totaltracks',
        'albumlength',
        #'ownerid',
        'recs'),
    'artist':(
        'artist',
        'totalalbums',
        'totaltracks',
        'artistlength',
        'ownerid',
        'recs'),
    'songs':(
        'title',
        'artist',
        'songid',
        'year',
        'genre',
        'album',
        'tracknumber',
        'recs',
        'ownerid',
        'filename'),
    'genre':(
        'genre',
        'numartists',
        'exartists',
        'ownerid'),
    'friend':(
        'friend',
        'name',
        'numartists',
        'numalbums',
        'likesartists'),
    'fid':()
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
            return self.get_albums(artist,friend,genre)    
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
        

    def get_albums(self, myartist, myfid, mygenre):                
        #Builds the "AND" part of the sql statement
        #The & is overloaded to create the correct SQL
        qualifiers = sql.and_()
        for key,param in request.params.iteritems():
            if(schema.has_key(key)):
                qualifiers.append(getattr(songs_table.c, key)==param)

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
    
        if myfid == None:
            if myartist == None: #no fid or artist to filter on
                if mygenre == None:     #no filters
                    tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id = \
                        songs.album_id", mapper=Songs).fetchall()
                else:  #filter only on genre
                    tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id = \
                        songs.album_id and albums.genre='%s'" % mygenre, mapper=Songs).fetchall()                    
            else: #filter by artist
                if myalbum == None: #filter by artist
                    if mygenre == None:     #only filter by artist                
                        tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id \
                            = songs.album_id and songs.artist = '%s'" % myartist, mapper=Songs).fetchall()
                    else: #filter by artist and genre
                        tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id \
                            = songs.album_id and songs.artist = '%s' and albums.genre='%s'" % (myartist,mygenre), mapper=Songs).fetchall()
                    
                else: # filter by artist and album
                    if mygenre == None:
                        tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id \
                            = songs.album_id and albums.album_title = '%s' and songs.artist = '%s'" % 
                            (myalbum,myartist), mapper=Songs).fetchall()
                    else: #filter on artist/album/genre
                        tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id \
                            = songs.album_id and albums.album_title = '%s' and songs.artist = '%s' and albums.genre='%s'" % 
                            (myalbum,myartist,mygenre), mapper=Songs).fetchall()
        else: # we have fid to filter on
            if myartist == None:
                if mygenre == None:
                    tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id = \
                        songs.album_id and songs.owner_id = %s" % myfid, mapper=Songs).fetchall()
                else:
                    tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id = \
                        songs.album_id and songs.owner_id = %s and albums.genre='%s'" % (myfid,mygenre), mapper=Songs).fetchall()              
            else:
                if myalbum == None: # filter only by artist and fid
                    if mygenre == None:
                        tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id \
                            = songs.album_id and songs.owner_id = %s and songs.artist = '%s'" % (myfid, myartist), mapper=Songs).fetchall()
                    else: #filter on genre/artist/fid
                        tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id \
                            = songs.album_id and songs.owner_id = %s and songs.artist = '%s' and albums.genre='%s'"
                            % (myfid, myartist,mygenre), mapper=Songs).fetchall()                        
                else: #filter on artist,album,fid
                    if mygenre == None:                        
                        tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id \
                            = songs.album_id and songs.owner_id = %s and songs.artist = '%s' and albums.album_title='%s'" 
                            % (myfid, myartist,myalbum), mapper=Songs).fetchall()
                    else: # filter on fid,artist,album,genre
                        tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id \
                            = songs.album_id and songs.owner_id = %s and songs.artist = '%s' and albums.album_title='%s'\
                            and albums.genre='%s'" % (myfid, myartist,myalbum,mygenre), mapper=Songs).fetchall()                        
                        
        if type == 'song':
            json = { 
                     "data" : [
                            {
                             "type":"song", 
                             "title": "%s" % row.title, 
                             "artist": "%s" % row.artist, 
                             "songid": row.songid,
                             "year": row.year, 
                             "genre": "%s" % row.genre,
                             "album": "%s" % row.album_title, 
                             "tracknumber": row.tracknumber,
                             "recs": row.recommendations,
                             "ownerid": row.owner_id,
                             "filename": row.filename
                            } for row in tuples
                        ]
                   }   
        elif type == 'queue':
            json = { 
                     "data" : [
                            {
                             "type":"queue", 
                             "text": "%s" % row.title, 
                             "id": row.songid, 
                             "leaf": "true"                     
                            } for row in tuples
                        ]
                   }  
        return json
        
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
