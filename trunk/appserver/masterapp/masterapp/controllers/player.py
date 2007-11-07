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
        type = request.params.get('type')
        filters = request.params.get('filter')
        print type
        #print filters
        if type == 'album': 
            return self.get_albums(filters)    
        elif type == 'artist':
            return self.get_artists(filters)
        elif type == 'genre':
            return self.get_genres(filters)
        elif type == 'song':
            return self.get_songs(filters) 
                

    def get_albums(self, *filters):
        #myartist = request.params.get('artist')
        #myalbum = request.params.get('album')
        #myfriend = request.params.get('fid')
        tuples = Session.query(Albums).add_entity(Songs).join('songs').all()
        for ar in tuples:
            print ar[0].album_title
        # row[0] is for album data, row[1] is for song data 
        json = {  
                 "data" : [
                        {
                         "type":"album",
                         "artist": "%s" % (tuples[row][1].artist), 
                         "year": tuples[row][0].year, 
                         "genre": "%s" % (tuples[row][0].genre),
                         "album": "%s" % (tuples[row][0].album_title), 
                         "tracknumber": tuples[row][1].tracknumber,
                         "totaltracks": tuples[row][0].totaltracks
                        } for row in range(len(tuples))
                    ]
               }   
        return json  
        
    def get_songs(self, *filters):     
        #mytype = request.params.get('type')
        #myalbum = request.params.get('album')
        #myfriend = request.params.get('fid')
        tuples = Session.query(Albums).add_entity(Songs).join('songs').all()
        # row[0] is for album data, row[1] is for song data 
        json = { 
                 "data" : [
                        {
                         "type":"song", 
                         "title": "%s" % (tuples[row][1].title), 
                         "artist": "%s" % (tuples[row][1].artist), 
                         "year": tuples[row][0].year, 
                         "genre": "%s" % (tuples[row][0].genre),
                         "album": "%s" % (tuples[row][0].album_title), 
                         "tracknumber": tuples[row][1].tracknumber,
                         "recs": tuples[row][1].recommendations
                        } for row in range(len(tuples))
                    ]
               }   
        return json
        
    def get_artists(self, *filters):
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
                         "artist": "%s" % tuples[row][0]
                        } for row in range(len(tuples))
                    ]
               }   
        return json          
        
    def get_genres(self, *filters):
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
                         "genre": "%s" % tuples[row][0]
                        } for row in range(len(tuples))
                    ]
               }   
        return json  

    def home(self):
        pass
