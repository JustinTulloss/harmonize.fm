# Profile controller for viewing a friend's profile

from masterapp.lib.base import *
from masterapp.lib.profile import Profile
from masterapp.lib.fbauth import ensure_fb_session
from masterapp.model import User, Session, Spotlight, SpotlightComment
import sqlalchemy.sql as sql

from facebook import FacebookError
from facebook.wsgi import facebook

from pylons import config
import pylons

class PeopleController(BaseController):
    def __before__(self):
        ensure_fb_session()

    def _get_active_spotlights(self, uid):
        return Session.query(Spotlight).filter(Spotlight.uid==uid).\
                order_by(sql.desc(Spotlight.timestamp))[:3]

    def profile(self, id):
        """
        Display the main profile for a user identified by id
        """
        # Make sure this user is allowed to access this profile
        #ensure_friends(id)
        
        c.user = Session.query(User).get(id)
        c.current_url = '#/people/profile/'+id
        c.profile = Profile()
        return render('/profile/index.mako')

    def add_spotcomment(self, id):
        comment = request.params.get('comment')
        if comment:
            spotcomment = SpotlightComment(session['userid'], id, comment)
            Session.save(spotcomment)
            Session.commit()

            return '1'
        else:
            return '0'
