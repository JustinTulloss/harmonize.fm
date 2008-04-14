import pylons
from facebook import FacebookError
from facebook.wsgi import facebook
from masterapp.model import User, Session
from masterapp.lib.base import *
from sqlalchemy import or_

def ensure_fb_session():
    c.facebook = facebook

    if 'paste.testing_variables' in request.environ:
        #We're testing. Setup a permanent facebook session
        facebook.session_key = '08bd66d3ebc459d32391d0d2-1909354'
        facebook.uid = 1909354
        session['fbsession']= facebook.session_key
        session['fbuid']= facebook.uid
        session['user'] = Session.query(User).filter(
            User.fbid==facebook.uid).first()
        session['fbfriends']=facebook.friends.getAppUsers()
        # XXX: This conditional works around a bug where the getAppUsers call
        #   returns a {} instead of [] when there are no friends. Should fix
        #   in the library
        if len(session['fbfriends']) > 0:
            session['fbfriends'].append(facebook.uid)
        else:
            session['fbfriends'] = [facebook.uid]
        session.save()
        return True

    if not session.has_key('fbsession'):
        if facebook.check_session(request):
            session['fbsession']=facebook.session_key
            session['fbuid']=facebook.uid
            session['user'] = Session.query(User).filter(
                User.fbid==facebook.uid).first()
            session['fbfriends']=facebook.friends.getAppUsers()
            session.save()
            return True
        else:
            next = '%s' % (request.environ['PATH_INFO'])
            url = facebook.get_login_url(next=next, canvas=False)
            facebook.redirect_to(url)
    else: 
        facebook.session_key = session['fbsession']
        facebook.uid = session['fbuid']
        return True

def filter_friends(qry):
    """
    This function ensures that songs belong to you by default. If you are
    browsing a friend's music store, ensure that the songs belong to them.
    """
    friend = request.params.get('friend')
    if friend:
        friend = int(friend)

    if friend in session['fbfriends']:
        qry = qry.filter(User.fbid == friend)
    else:
        qry = qry.filter(User.id == session['user'].id)
    return qry

def get_user_info():
    return facebook.users.getInfo(session['fbuid'])[0]
