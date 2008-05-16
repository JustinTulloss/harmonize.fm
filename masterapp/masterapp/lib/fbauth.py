import pylons
from facebook import FacebookError
from facebook.wsgi import facebook
from masterapp.model import User, Session
from masterapp.lib.base import *
from sqlalchemy import or_

def ensure_fb_session():
    c.facebook = facebook

    def setup_user():
        session['fbsession']= facebook.session_key
        session['fbuid']= facebook.uid
        user = Session.query(User).filter(
            User.fbid==facebook.uid).first()
        if not user:
            # First time visitor, set up an account for them
            user = User(fbid = facebook.uid)
            Session.save(user)
            Session.commit()
        session['user'] = user

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

    if 'paste.testing_variables' in request.environ:
        #We're testing. Setup a permanent facebook session
        facebook.session_key = '08bd66d3ebc459d32391d0d2-1909354'
        facebook.uid = 1909354
        return setup_user()

    if not session.has_key('fbsession'):
        if facebook.check_session(request):
            return setup_user()
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

    friend_fbid = Session.query(User).get(friend).fbid
    if friend_fbid in session['fbfriends']:
        qry = qry.filter(User.id == friend)
    else:
        qry = qry.filter(User.id == session['user'].id)
    return qry

def filter_any_friend(qry):
    """
    This function creates a giant SQL OR statement that restricts
    the files you can select from to files owned by any of your friends.
    It assumes you are joined to the Users table.
    """
    fbclause = or_()
    for friend in session['fbfriends']:
        fbclause.append(User.fbid==friend)
    fbclause.append(User.id == session['user'].id)
    qry = qry.filter(fbclause)
    return qry

def get_user_info():
    return facebook.users.getInfo(session['fbuid'])[0]
