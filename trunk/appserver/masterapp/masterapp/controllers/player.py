from masterapp.lib.base import *

class PlayerController(BaseController):
    def index(self):
        # Return a rendered template
        #   return render_response('/some/template.html')
        # or, Return a response object
        c.noun = "puppies"
        return render('/player.mako')
		
