# Profile controller for viewing a friend's profile

from masterapp.lib.base import *
from masterapp.lib.amazon import *
from masterapp.lib.profile import Profile
from masterapp.lib.fbauth import ensure_fb_session
from masterapp.model import User, Session, Spotlight, SpotlightComment
import sqlalchemy.sql as sql

from facebook import FacebookError
from facebook.wsgi import facebook

from pylons import config
import pylons
import time

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
        c.current_user = Session.query(User).get(session['userid'])
        c.profile = Profile()
        def l_get_asin(id,type):
            return get_asin(id, type)
        c.l_get_asin = l_get_asin
        return render('/profile/index.mako')

    def add_spotcomment(self, id):
        comment = request.params.get('comment')
        if comment:
            comment = h.util.html_escape(comment)
            spotcomment = SpotlightComment(session['userid'], id, comment)
            Session.save(spotcomment)
            Session.commit()

            # send facebook notification to the person who owns this spotlight
            spot = Session.query(Spotlight).get(spotcomment.spotlightid)
            owner = Session.query(User).get(spot.uid)
            fbml = " commented on <a href='http://harmonize.fm/player#/people/profile/" + str(owner.id) + "/spcomments/" + str(spot.id) + "' target='_blank'>" + spot.title + "</a>"
            response = facebook.notifications.send(owner.fbid, fbml)

            return response
        else:
            return '0'

    def invite(self,**kwargs):
        fbml = '<fb:notif-page> invited you as a private beta user to <a href="http://harmonize.fm/player">Harmonize.fm</a></fb:notif-page>'
        # TODO: right now, we only have one id coming in.  when we change this, we need to
        # split them up into an array and pass that to the send() function below.
        response = facebook.notifications.send(kwargs['id'],fbml)
        # CANNOT find a way to get any sort of response from this call, for now just assume it worked
        # :-/
        return '1'
