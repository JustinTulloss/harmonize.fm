# Profile controller for viewing a friend's profile

from masterapp.lib.base import *
from masterapp.lib.profile import Profile
from masterapp.lib.fbauth import ensure_fb_session
from masterapp.model import User, Session

from facebook import FacebookError
from facebook.wsgi import facebook

from pylons import config
import pylons

class PeopleController(BaseController):
    def __before__(self):
        ensure_fb_session()

    def profile_body(self, id):
        """
        Display the main profile for a user identified by id
        """
        # Make sure this user is allowed to access this profile
        #ensure_friends(id)
        
        c.user = Session.query(User).get(id)
        c.profile = Profile()
        return render('/profile/index.mako')

    def profile_right(self, id):
        """
        Display the right column of a user identified by id. I currently do 2
        requests cause I can't figure out how to do it with Ext layouts in 1. I
        want to use ext layouts cause I can't get scrolling to work properly on
        my own.
        """
        c.user = Session.query(User).get(id)
        c.profile = Profile()
        return render('/profile/rightcol.mako')
