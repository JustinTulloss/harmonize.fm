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
    def get_albums(self):
        myartist = request.params.get('artist')
        myalbum = request.params.get('album')
        myfriend = request.params.get('fid')
        tuples = Session.query(Albums).add_entity(Songs).join('songs').filter_by(artist="Radiohead").all()
        # row[0] is for album data, row[1] is for song data 
        json = { "type":"albums", 
                 "data" : [
                        {
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
        
    @jsonify    
    def get_songs(self):     
        myartist = request.params.get('artist')
        myalbum = request.params.get('album')
        myfriend = request.params.get('fid')
        tuples = Session.query(Albums).add_entity(Songs).join('songs').all()
        print len(tuples)
        # row[0] is for album data, row[1] is for song data 
        json = { "type":"songs", 
                 "data" : [
                        {
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

    def home(self):
        pass
