import time
import pylons
from pylons import cache, config
from facebook import FacebookError
from facebook.wsgi import facebook
from masterapp.model import User, Session, Whitelist
from masterapp.lib.base import *
from sqlalchemy import or_
from fblogin import login
from masterapp.lib.fbaccess import fbaccess


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
            user = create_user(facebook.uid)

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

def create_user(fbid):
    user = User(fbid = fbid, premium = False)
    user.add_me_to_friends()
    Session.add(user)
    return user

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

@fbaccess
def qualified_for_login(fbuser, breadth):
    # right now the base users are dave paola, justin tulloss, and brian smith.
    # TODO: pull these base_users from a database table?
    base_users = ['1932106','1909354','1908861']
    if fbuser in base_users:
        return True

    test_user = [fbuser for i in range(3)]
    results = facebook.friends.areFriends(base_users, test_user)
    for res in results:
        if res['are_friends']:
            return True

    # next see if this user is on the whitelist
    qry = Session.query(Whitelist).filter(Whitelist.fbid == fbuser)
    if qry.count() != 0:
        return True

    return False
