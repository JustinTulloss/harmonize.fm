from masterapp.lib.base import *
from masterapp.model import Music, Session

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
        return render('/player.mako')
    
    def enqueue(self):
        return request.POST["id"]
    
    def settings(self):
        return "This is the change settings form!"
