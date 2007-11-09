from masterapp.lib.base import *
from masterapp.model import Songs, Albums, Friends, Session
from masterapp.lib.profile import Profile
import pylons

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
        fid = request.params.get('fid')
        if type == 'album': 
            return self.get_albums(artist,fid)    
        elif type == 'artist':
            return self.get_artists(fid)
        elif type == 'genre':
            return self.get_genres(fid)
        elif type == 'song':
            return self.get_songs(type,artist,album,fid) 
        elif type == 'friend':
            return self.get_friends()
        elif type == 'queue':
            return self.get_songs(type,artist,album,fid)
        
    def get_albums(self, myartist, myfid):                
        if myfid == None:
            if myartist == None:
                tuples = Session.execute("select distinct album_title,artist,year,genre,owner_id,count(songs.id) as totaltracks,albums.id as albumid from albums, songs where albums.id = songs.album_id group by albumid", mapper=Songs).fetchall()        
            else:
                tuples = Session.execute("select distinct album_title,artist,year,genre,owner_id,count(songs.id) as totaltracks,albums.id as albumid from albums, songs where albums.id = songs.album_id and songs.artist = '%s' group by albumid" % myartist, mapper=Songs).fetchall()
        else: #we have a fid to filter on            
            if myartist == None:
                tuples = Session.execute("select distinct album_title,artist,year,genre,totaltracks,owner_id,count(songs.id) as totaltracks,albums.id as albumid from albums, songs where albums.id = songs.album_id and songs.owner_id = %d group by albumid" % myfid, mapper=Songs).fetchall()
            else: # we have fid and artist
                tuples = Session.execute("select distinct album_title,artist,year,genre,totaltracks,owner_id,count(songs.id) as totaltracks,albums.id as albumid from albums, songs where albums.id = songs.album_id and songs.owner_id = %d and songs.artist = '%s' group by albumid" % (myfid, myartist), mapper=Songs).fetchall()
        json = {  
                 "data" : [
                        {
                         "type":"album",
                         "artist": "%s" % row.artist, 
                         "year": row.year, 
                         "genre": "%s" % row.genre,
                         "album": "%s" % row.album_title, 
                         "totaltracks": row.totaltracks,
                         "albumlength": "%s" % self.get_album_length(row.albumid,None),
                         "ownerid": row.owner_id
                        } for row in tuples
                    ]
               }   
        return json  
        
    def get_songs(self, type, myartist, myalbum, myfid):     
    
        if myfid == None:
            if myartist == None: #list all albums
                tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id = songs.album_id", mapper=Songs).fetchall()
            else:
                if myalbum == None: #filter only by artist
                    tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id = songs.album_id and songs.artist = '%s'" % myartist, mapper=Songs).fetchall()
                else: # filter by artist and album
                    tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id = songs.album_id and albums.album_title = '%s' and songs.artist = '%s'" % (myalbum,myartist), mapper=Songs).fetchall()
        else: # we have fid to filter on
            if myartist == None:
                tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id = songs.album_id and songs.owner_id = %d" % myfid, mapper=Songs).fetchall()
            else:
                if myalbum == None: # filter only by artist and fid
                    tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id = songs.album_id and songs.owner_id = %d and songs.artist = '%s'" % (myfid, myartist), mapper=Songs).fetchall()
                else: #filter on artist,album,fid
                    tuples = Session.execute("select *,songs.id as songid from albums,songs where albums.id = songs.album_id and songs.owner_id = %d and songs.artist = '%s' and albums.album_title='%s'" % (myfid, myartist,myalbum), mapper=Songs).fetchall()
                    
        if type == 'song':
            json = { 
                     "data" : [
                            {
                             "type":"song", 
                             "title": "%s" % row.title, 
                             "artist": "%s" % row.artist, 
                             "year": row.year, 
                             "genre": "%s" % row.genre,
                             "album": "%s" % row.album_title, 
                             "tracknumber": row.tracknumber,
                             "recs": row.recommendations,
                             "ownerid": row.owner_id
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
        
    def get_artists(self, myfid):
        if myfid == None:
            tuples = Session.execute("select artist, count( distinct album_id ) as totalalbums,count(*) as totaltracks from songs group by artist",mapper=Songs).fetchall()
        else:
            tuples = Session.execute("select artist, count( distinct album_id ) as totalalbums,count(*) as totaltracks from songs where owner_id=%d group by artist" % myfid,mapper=Songs).fetchall()
        
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
                         "ownerid": myfid                         
                        } for row in tuples
                    ]
               }   
        return json          
        
    def get_genres(self, myfid):
        if myfid == None:
            tuples = Session.execute("select distinct genre from albums",mapper=Albums).fetchall()
        else:
            tuples = Session.execute("select distinct genre from albums where owner_id=%d" % myfid,mapper=Albums).fetchall()
        #fetchall returns a list
        # row[0] is the bare genre
        json = { 
                 "data" : [
                        {
                         "type":"genre",
                         "genre": "%s" % row.genre,
                         "ownerid": myfid
                        } for row in tuples
                    ]
               }   
        return json  
        
    def get_friends(self):
        tuples = Session.query(Friends).all()
        json = {
                 "data" : [
                        {
                         "type":"friend",
                         "id": "%d" % tuples[row].id,
                         "name": "%s" % tuples[row].name
                        } for row in range(len(tuples))
                    ]
               }   
        return json          
        
    def add_rec(self):
        songid = request.params.get('songid')
        albumid = request.params.get('albumid')
        if songid == None and albumid != None: #recommending entire album
            myalbum = Session.query(Songs).filter_by(album_id=albumid).all()
            for mysong in myalbum:
                mysong.recommendations = mysong.recommendations + 1
        elif songid != None: #individual song
            mysong = Session.query(Songs).filter_by(id=songid).one()
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
        

    def home(self):
        pass
