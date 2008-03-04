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
        session['fbfriends'].append(facebook.uid)
        session.save()
        return

    if not session.has_key('fbsession'):
        if facebook.check_session(request):
            session['fbsession']=facebook.session_key
            session['fbuid']=facebook.uid
            session['user'] = Session.query(User).filter(
                User.fbid==facebook.uid).first()
            session['fbfriends']=facebook.friends.getAppUsers()
            session['fbfriends'].append(facebook.uid)
            session.save()
        else:
            next = '%s' % (request.environ['PATH_INFO'])
            url = facebook.get_login_url(next=next, canvas=False)
            facebook.redirect_to(url)
    else: 
        facebook.session_key = session['fbsession']
        facebook.uid = session['fbuid']

def filter_friends(qry):
    """
    This function creates a giant SQL OR statement that restricts
    the files you can select from to files owned by any of your friends.
    It assumes you are joined to the Users table.
    """
    #fbclause = sql.expression.or_()
    fbclause = or_()
    for friend in session['fbfriends']:
        fbclause.append(User.fbid==friend)
    qry = qry.filter(fbclause)
    return qry
