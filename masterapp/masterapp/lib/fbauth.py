import time
import pylons
from pylons import cache, config
from facebook import FacebookError
from facebook.wsgi import facebook
from masterapp.model import User, Session, Whitelist
from masterapp.lib.base import *
from sqlalchemy import or_
from fblogin import login


from datetime import datetime

def ensure_fb_session():
    c.facebook = facebook

    def setup_user():
        session['fbsession']= facebook.session_key
        session['fbuid']= facebook.uid

        if not qualified_for_login(facebook.uid, 1):
            return False

        user = Session.query(User).filter(
            User.fbid==facebook.uid).first()        
        if not user:
            #return False #XXX: Remove this line to open up harmonize!
            # First time visitor, set up an account for them
            user = User(fbid = facebook.uid, premium = False)
            user.update_friends_caches()
            Session.add(user)
            
        user.lastseen = datetime.now()
        user.fbsession = facebook.session_key
        user.present_mode = True if request.params.get('present') == 'true' else False
        Session.add(user)
        Session.commit()
        session['userid'] = user.id
        session.save()
        return True

    if not session.get('fbsession'):
        if facebook.check_session(request):            
            return setup_user()
        else:
            login()
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
    friend_fbid = None
    if friend:
        friend_fbid = Session.query(User).get(friend).fbid
        friend = int(friend)

    if friend_fbid in session['fbfriends']:
        qry = qry.filter(User.id == friend)
    else:
        qry = qry.filter(User.id == session['userid'])
    return qry

def filter_any_friend(qry):
    """
    This function creates a giant SQL OR statement that restricts
    the files you can select from to files owned by any of your friends.
    It assumes you are joined to the Users table.
    """
    raise DeprecationWarning()
    fbclause = or_()
    for friend in session['fbfriends']:
        fbclause.append(User.fbid==friend)
    fbclause.append(User.id == session['userid'])
    qry = qry.filter(fbclause)
    return qry

def get_user_info():
    raise DeprecationWarning()
    info = None
    while not info:
        try:
            info = facebook.users.getInfo(session['fbuid'])[0]
        except:
            time.sleep(.1)
    return info

def qualified_for_login(fbuser, breadth):
    # right now the base users are dave paola, justin tulloss, and brian smith.
    # TODO: pull these base_users from a database table?
    base_users = ['1932106','1909354','1908861']
    if base_users.count(fbuser) != 0:
        return True
    orit = or_()
    for u in base_users:
        orit.append(User.fbid == u)

    base_users = Session.query(User).filter(orit).all()
    for b in base_users:
        if b.is_fbfriends_with(fbuser):
            return True
    # next see if this user is on the whitelist
    qry = Session.query(Whitelist).filter(Whitelist.fbid == user)
    if qry.count() != 0:
        return True

    return False
