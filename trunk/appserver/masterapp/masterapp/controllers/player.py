from masterapp.lib.base import *
from masterapp.model import Songs, Albums, Session
from masterapp.lib.profile import Profile
import pylons
#from pylons.decorators import jsonify


class PlayerController(BaseController):
    def index(self):
        c.profile = Profile()
        return render('/player.mako')
    
    def enqueue(self):
        return request.POST["id"]
            
    def settings(self):
        return "This is the change settings form!"
    
    def artists(self):
        artists = Session.query(Songs).all()
        for row in artists:
            print row
        return artists
    
    @jsonify    
    def get_data(self):
        filters = 0
        type = request.params.get('type')
        artist = request.params.get('artist')
        album = request.params.get('album')
        print type
        print artist
        print album
        #print filters
        if type == 'album': 
            return self.get_albums(artist)    
        elif type == 'artist':
            return self.get_artists(filters)
        elif type == 'genre':
            return self.get_genres(filters)
        elif type == 'song':
            return self.get_songs(artist,album) 
                

    def get_albums(self, myartist):
        
        if myartist == None:            
            #tuples = Session.query(Albums).add_entity(Songs).join('songs').all()
            tuples = Session.execute("select distinct album_title,artist,year,genre,totaltracks from albums, songs where albums.id = songs.album_id",mapper=Albums, mapper=Songs).fetchall()
        else:
            tuples = Session.execute("select distinct album_title,artist,year,genre,totaltracks from albums, songs where albums.id = songs.album_id and songs.artist = '%s'" % myartist,mapper=Albums, mapper=Songs).fetchall()
        json = {  
                 "data" : [
                        {
                         "type":"album",
                         "artist": "%s" % (row.artist), 
                         "year": row.year, 
                         "genre": "%s" % (row.genre),
                         "album": "%s" % (row.album_title), 
                         "totaltracks": row.totaltracks
                        } for row in tuples
                    ]
               }   
        return json  
        
    def get_songs(self, myartist, myalbum):     
        #mytype = request.params.get('type')
        #myalbum = request.params.get('album')
        #myfriend = request.params.get('fid')
        if myartist == None: #list all albums
            tuples = Session.execute("select * from albums,songs where albums.id = songs.album_id", mapper=Albums, mapper=Songs).fetchall()
        else:
            if myalbum == None: #filter only by artist
                tuples = Session.execute("select * from albums,songs where albums.id = songs.album_id and songs.artist = '%s'" % myartist, mapper=Albums, mapper=Songs).fetchall()
            else: # filter by artist and album
                tuples = Session.execute("select * from albums,songs where albums.id = songs.album_id and albums.album_title = '%s' and songs.artist = '%s'" % (myalbum,myartist), mapper=Albums, mapper=Songs).fetchall()

        # row[0] is for album data, row[1] is for song data 
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
                         "recs": row.recommendations
                        } for row in tuples
                    ]
               }   
        return json
        
    def get_artists(self, filters):
        #myartist = request.params.get('artist')
        #myalbum = request.params.get('album')
        #myfriend = request.params.get('fid')
        #tuples = Session.query(Songs).select([songs_table.c.artist], distinct=True).all()
        #tuples = Songs.select([Songs.c.artist], distinct=True)
        tuples = Session.execute("select distinct artist from songs",mapper=Songs).fetchall()
        #fetchall returns a list
        #row[0] is the bare artist
        json = {  
                 "data" : [
                        {
                         "type":"artist",
                         "artist": "%s" % row.artist
                        } for row in tuples
                    ]
               }   
        return json          
        
    def get_genres(self, filters):
        #myartist = request.params.get('artist')
        #myalbum = request.params.get('album')
        #myfriend = request.params.get('fid')
        tuples = Session.execute("select distinct genre from albums",mapper=Albums).fetchall()
        #fetchall returns a list
        # row[0] is the bare genre
        json = { 
                 "data" : [
                        {
                         "type":"genre",
                         "genre": "%s" % row.genre
                        } for row in tuples
                    ]
               }   
        return json  
        
    def get_friends(self, filters):
        tuples = Session.query(Friends).all()
        json = {
                 "data" : [
                        {
                         "type":"friends",
                         "name": "%s" % tuples[row].name
                        } for row in range(len(tuples))
                    ]
               }   
        return json          
        
    def add_rec(self):
        songid = request.params.get('songid')
        mysong = Session.query(Songs).filter_by(id=songid).one()
        mysong.recommendations = mysong.recommendations + 1
        Session.save()

    def home(self):
        pass
