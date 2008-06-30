# vim:expandtab:smarttab
import logging
import time

import S3
import masterapp.controllers.metadata
from masterapp.config.include_files import player_files, compressed_player_files
from masterapp.lib.base import *
from masterapp.lib.fbauth import ensure_fb_session, filter_friends,\
    get_user_info
from masterapp.lib.profile import Profile
from masterapp.config import schema
from masterapp.model import (
    Session, 
    User, 
    File, 
    Album, 
    BlogEntry, 
    Spotlight,
    SpotlightComment,
    Song)
from facebook import FacebookError
from facebook.wsgi import facebook
from pylons import config
import pylons
from sqlalchemy.orm import aliased
from sqlalchemy.sql import or_, and_
import sqlalchemy.sql as sql

from mailer import mail
import re
import thread

import masterapp.lib.snippets as snippets

log = logging.getLogger(__name__)

DEFAULT_EXPIRATION = 30 #minutes to expire a song access URL

class PlayerController(BaseController):
    def __init__(self):
        BaseController.__init__(self)
        self.email_regex = re.compile("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+\.[a-zA-Z]{2,6}$")

    def __before__(self):
        if not ensure_fb_session():
                redirect_to("/sign-up")

    def _get_feed_entries(self, uid, max_count=20):
        entries = Session.query(BlogEntry)[:max_count]
        myor = or_()
        for friend in session['fbfriends']:
            myor.append(User.fbid == friend)

        entries.extend(Session.query(Spotlight).join(User).filter(and_(
                myor, Spotlight.active==True))\
                [:max_count])

        CommentUser = aliased(User)
        SpotlightUser = aliased(User)
        commentor = or_()
        spotlightor = or_()
        for friend in session['fbfriends']:
            commentor.append(CommentUser.fbid == friend)
            spotlightor.append(SpotlightUser.fbid == friend)
            

        entries.extend(Session.query(SpotlightComment).\
                join(CommentUser,
                    (Spotlight, SpotlightComment.spotlight), 
                    (SpotlightUser, Spotlight.user)).\
                filter(and_(
                    SpotlightComment.uid!=session['userid'],
                    or_(Spotlight.uid==session['userid'],
                        and_(commentor, spotlightor)),
                    Spotlight.active == True))[:max_count])

        def sort_by_timestamp(x, y):
            if x.timestamp == None:
                if y.timestamp == None:
                    return 0
                return 1
            elif y.timestamp == None:
                return -1
            elif x.timestamp > y.timestamp:
                return -1
            elif x.timestamp == y.timestamp:
                return 0
            else:
                return 1

        entries.sort(sort_by_timestamp)
        return entries[:max_count]

    def index(self):
        c.profile = Profile()
        c.user = Session.query(User).get(session['userid'])
        c.fields = schema.fields

        if snippets.is_ie6(request.environ['HTTP_USER_AGENT']):
            redirect_to('/ie6')

        if config.get('compressed') == 'true':
            c.include_files = compressed_player_files
        else:
            c.include_files = player_files
	
        return render('/player.mako')
    
    def songurl(self, id):
        """
        Fetches the S3 authenticated url of a song.
        Right now, this provides no security at all since anybody with a 
        facebook login can request a url. However, now it's possible to track
        who's doing what, and if we can come up with conclusive proof that
        somebody is stealing music through our logs, we can ban them.
        """
        if session.get('playing') != None:
            if g.usedfiles.has_key(session['playing']):
                g.usedfiles.pop(session['playing'])

        song= Session.query(Song).\
            join([Song.owners]).filter(Song.id==int(id))
        song= song.first()
        # Update now playing
        user = Session.query(User).get(session['userid'])
        user.nowplaying = song
        Session.add(user)
        Session.commit()
        # XXX: Remove this to enable locking implemented below
        qsgen = S3.QueryStringAuthGenerator(
        config['S3.accesskey'], config['S3.secret'],
            is_secure = False
        )
        qsgen.set_expires_in(DEFAULT_EXPIRATION*60)
        return qsgen.get(config['S3.music_bucket'], song.sha)
        
        # TODO: Think of a more efficient way of doing this. Perhaps the inuse
        # flag should be in the database?
        for file in files:
            for owner in file.owners:
                if not g.usedfiles.has_key((file.id, owner.id)):
                    qsgen = S3.QueryStringAuthGenerator(
                        config['S3.accesskey'], config['S3.secret'],
                        is_secure = False
                    )
                    qsgen.set_expires_in(DEFAULT_EXPIRATION*60)
                    
                    #Mark the file as in use, with the time it can come back
                    g.usedfiles[(file.id, owner.id)] = \
                        time.time()+DEFAULT_EXPIRATION*60
                    session['playing'] = (file.id, owner.id)
                    session.save()
                    return qsgen.get(config['S3.music_bucket'], file.sha)
        #if we get here, all files are in use! Damn it!
        session['playing'] = None
        session.save()
        return 'false'

    def album_details(self):
        c.album = Session.query(Album).get(request.params.get('album'))
        return render('/album_details.mako')

    def recommend_to_fbfriend(self, id):
        """
        Recommends music to a friend based on their facebook id
        """
        # Set up the correct informatio to pass to the notification template
        c.recommender = session['user'].fbid
        c.recommendee = id
        c.recommended = request.params.get('recommended')
        c.playlink = request.params.get('playlink')
        notification = render('/fbprofile/recnotif.mako')
        facebook.notifications.send([id], notification)

    def username(self):
        return get_user_info()['name']

    @jsonify
    def get_checked_friends(self):
        userStore = facebook.friends.getAppUsers()
        userList = facebook.users.getInfo(userStore)
        for user in userList:
            user["checked"]=self.get_active(user["uid"])
        
        userDict = dict(data = userList) 
        return userDict
    
    def get_active(self, uid):
        if uid == 1908861:
            return True 
        else:
            return False

    def feedback(self):
        if not request.params.has_key('email') or\
                not request.params.has_key('feedback'):
            return '0';
        user_email = request.params['email']
        user_feedback = request.params['feedback']

        if (self.email_regex.match(user_email) != None):
            subject = 'Site feedback from %s' % user_email
        else:
            subject = 'Site feedback'
        
        def sendmail():
            mail(config['smtp_server'], config['smtp_port'],
                config['feedback_email'], config['feedback_password'],
                'founders@harmonize.fm', subject, user_feedback)

        thread.start_new_thread(sendmail, ())
        return '1'

    def spotlight_album(self, id):
        if not request.params.has_key('comment'):
            return '0'

        albumid = id
        comment = request.params['comment']
        uid = session['userid']

        spotlight = Spotlight(uid, albumid, comment)
        Session.save(spotlight)
        Session.commit()
        
        return '1'

    def blog(self, id):
        c.entries = Session.query(BlogEntry).order_by(sql.desc(BlogEntry.timestamp))
        c.main = True
        return render('/blog.mako')

    def home(self):
        c.entries = self._get_feed_entries(session['userid'])
        c.main = True
        c.user = Session.query(User).get(session['userid'])
        c.num_songs = c.user.song_count
        c.appid = config['pyfacebook.appid']
        if 'Windows' in request.headers['User-Agent']:
            c.platform = 'windows'
        elif 'Macintosh' in request.headers['User-Agent']:
            c.platform = 'mac'
        return render('/home.mako')
        
    def spotlight_edit(self):
        if not request.params.has_key('comment'):
            return "False"
        elif not request.params.has_key('spot_id'):
            return "False"
        id = request.params.get('spot_id')
        comment = request.params.get('comment')
        spotlight = Session.query(Spotlight).filter(Spotlight.id == id)[0]
        spotlight.comment = comment
        Session.commit()
        
        return "True"

    def delete_spotlight(self,id):
        spot = Session.query(Spotlight).get(id)
        if (spot):
            Session.delete(spot)
            Session.commit()
            return "True"
        else:
            return "False"
        
        
    def spotlight_playlist(self, id):
        if not request.params.has_key('comment'):
            return '0'

        playlistid = id
        comment = request.params['comment']
        uid = session['userid']

        spotlight = Spotlight(uid, None, comment, True, playlistid)
        Session.save(spotlight)
        Session.commit()
        
        return '1'
