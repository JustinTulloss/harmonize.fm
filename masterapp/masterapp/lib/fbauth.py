import time
import pylons
from facebook import FacebookError
from facebook.wsgi import facebook
from masterapp.model import User, Session, users_table, Whitelist
from masterapp.lib.base import *
from sqlalchemy import or_

import re

from datetime import datetime

def ensure_fb_session():
    c.facebook = facebook

    def setup_user():
        
        session['fbsession']= facebook.session_key
        session['fbuid']= facebook.uid
        user = Session.query(User).filter(
            User.fbid==facebook.uid).first()        
        #raise RuntimeError()
        if not qualified_for_login(facebook.uid, 1):
            return False
        if not user:
            # First time visitor, set up an account for them
            user = User(fbid = facebook.uid)
            Session.add(user)
            Session.commit()
            
        user.lastseen = datetime.now()
        user.fbsession = facebook.session_key
        session['userid'] = user.id
        Session.add(user)
        Session.commit()

        session['fbfriends']=facebook.friends.getAppUsers()
        # XXX: This conditional works around a bug where the getAppUsers call
        #   returns a {} instead of [] when there are no friends. Should fix
        #   in the library
        if len(session['fbfriends']) == 0:
            session['fbfriends'] = []
        if request.params.get('present') == 'true':
            session['fbfriends'].extend([1909354, 1908861])
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
            qry_string = request.environ['QUERY_STRING']
            auth_match = re.search('&auth_token=[A-Za-z0-9]+', qry_string)
            if auth_match:
                qry_string = qry_string.replace(auth_match.group(), '')
                
            next = '%s?%s' % \
                (request.environ['PATH_INFO'], qry_string)
            url = facebook.get_login_url(next=next, canvas=False)
            facebook.redirect_to(url)
    else: 
        facebook.session_key = session['fbsession']
        facebook.uid = session['fbuid']
        return True

friendcache = cache.get_cache('fbfriends')
def get_friend_ids():
    return friendcache.get_value    
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

def filter_sql_friends(qry):
    friend = request.params.get('friend')
    friend_fbid = None
    if friend:
        friend_fbid = Session.query(User).get(friend).fbid
        friend = int(friend)
    
    if friend_fbid in session['fbfriends']:
        qry = qry.where(users_table.c.id == friend)
    else:
        qry = qry.where(users_table.c.id == session['userid'])

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
    fbclause.append(User.id == session['userid'])
    qry = qry.filter(fbclause)
    return qry

def get_user_info():
    info = None
    while not info:
        try:
            info = facebook.users.getInfo(session['fbuid'])[0]
        except:
            time.sleep(.1)
    return info

def qualified_for_login(user, breadth):
        # right now the base users are dave paola, justin tulloss, and brian smith.
        # TODO: pull these base_users from a database table?
        base_users = ['1932106','1909354','1908861']
        if base_users.count(user) != 0:
                return True
	for b in base_users:
                r = facebook.friends.areFriends([user],[b])
                
                if r[0]['are_friends']:
                        return True
        # next see if this user is on the whitelist
        qry = Session.query(Whitelist).filter(Whitelist.fbid == user)
        if qry.count() != 0:
                return True

        return False

# this is my test function, run through the pylons debugger, not for production!
def test():
        return qualified_for_login(facebook.uid,1)
