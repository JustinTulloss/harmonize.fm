from masterapp.lib.base import *
from masterapp.lib.profile import Profile
from masterapp.model import Music, Session
import pylons

class PlayerController(BaseController):
    def index(self):
        # Return a rendered template
        #   return render_response('/some/template.html')
        # or, Return a response object
        c.noun = "ass"
        record = Session.query(Music).all()
        if record == None:
            return "Bad"
        c.data = record
        c.cols = ["title", "artist", "album"]
        c.profile = Profile()
        return render('/player.mako')
    
    def enqueue(self):
        return request.POST["id"]
    
    def settings(self):
        return "This is the change settings form!"
    
    @jsonify
    def artist(self, id):
        query = Session.query(Music).filter_by(artist=id)
        #shouldn't there be a better way to do this?
        data = {}
        i=0
        for song in query.all():
            data['song'+str(i)]=song.c
            i = i + 1
        
        return data
    def home(self):
        pass
