# vim:expandtab:smarttab
import logging
import time
import os

import S3
import urllib
import cjson
from masterapp.config.include_files import player_files, compressed_player_files
from masterapp.lib.base import *
from masterapp.lib.decorators import pass_user
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
    Song,
    SongStat
    )
from facebook import FacebookError
from facebook.wsgi import facebook
from pylons import config
import pylons
from sqlalchemy.sql import or_, and_
import sqlalchemy.sql as sql

from mailer import mail
import re
import thread

import masterapp.lib.snippets as snippets

feedback_template = """
%s

Browser:
%s

Screen:
%s

File this (harmonize.fm employees only):
http://trac.harmonize.fm/trac/newticket
"""

log = logging.getLogger(__name__)

DEFAULT_EXPIRATION = 30 #minutes to expire a song access URL

class PlayerController(BaseController):
    def __init__(self):
        BaseController.__init__(self)
        self.email_regex = re.compile("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+\.[a-zA-Z]{2,6}$")

    def __before__(self):
        if not ensure_fb_session():
            redirect_to("/request/invitation")

    def index(self):
        assert request.environ.get('HTTP_USER_AGENT'),\
            "Cannot serve to unidentified clients"

        c.profile = Profile()
        c.user = Session.query(User).get(session['userid'])
        c.fields = schema.fields
        c.fblogin_url = facebook.get_login_url(canvas=False)

        if snippets.is_ie6(request.environ['HTTP_USER_AGENT']):
            redirect_to('/ie6')

        if config.get('compressed') == 'true':
            c.include_files = compressed_player_files
        else:
            c.include_files = player_files
	
        return render('/player.mako')

    @pass_user
    def songurl(self, friend, **kwargs):
        """
        Fetches the S3 authenticated url of a song.
        Right now, this provides no security at all since anybody with a 
        facebook login can request a url. However, now it's possible to track
        who's doing what, and if we can come up with conclusive proof that
        somebody is stealing music through our logs, we can ban them.
        """
        user = Session.query(User).get(session['userid'])
        if not user.is_friends_with(friend):
            abort(401)

        song = Session.query(Song).\
            join(Song.owners).filter(Song.id==int(kwargs['id']))
        song = song.first()
        if not song:
            abort(404)

        qsgen = S3.QueryStringAuthGenerator(
        config['S3.accesskey'], config['S3.secret'],
            is_secure = False
        )
        qsgen.set_expires_in(DEFAULT_EXPIRATION*60)

        return qsgen.get(config['S3.music_bucket'], song.sha)
        
    @pass_user
    def set_now_playing(self, user, **kwargs):
        if not request.params.has_key('id'):
            return 'false'
        
        song = Session.query(Song).get(request.params.get('id'))
        user = Session.query(User).get(session['userid'])
        # we need to now add the database entries for this song being played.
        # this includes setting the now playing and updating the song statistic song and source
        if request.params.has_key('source'):
            src = int(request.params.get('source'))
            if src in SongStat.sources:
                session['src'] = src
        
        user.nowplaying = song
        Session.add(user)
        Session.commit()
        user.update_profile()
        return 'true'

    @pass_user
    def album_details(self, user, **kwargs):
        c.songs = user.song_query.filter(
            Song.albumid == request.params.get('album')
        ).order_by(Song.tracknumber).all()
        if len(c.songs) == 0:
            abort(404)
        c.album = user.album_query.filter(
            Album.id == request.params.get('album')
        ).one()
        return render('/album_details.mako')

    @pass_user
    def username(self, user, **kwargs):
        return user.name

    def feedback(self):
        if not request.params.has_key('email') or\
                not request.params.get('feedback'):
            return '0';
        user_email = request.params['email']
        user_feedback = request.params['feedback']
        user_browser = request.params.get('browser')

        browser = screen = user = ''
        user = Session.query(User).get(session['userid'])

        if user_browser:
            bdata = cjson.decode(urllib.unquote(user_browser))
            for key, value in bdata['browser'].items():
                browser = browser + "%s = %s\n" % (key, value)

            for key, value in bdata['screen'].items():
                screen = screen + "%s = %s\n" % (key, value)
        message = feedback_template % \
                (user_feedback, browser, screen)

        if (self.email_regex.match(user_email) != None):
            if user.email != user_email:
                user.email = user_email
                Session.add(user)
                Session.commit()
        else:
            user_email = None

        subject = 'harmonize.fm feedback from %s' % user.name
        
        def sendmail():
            cc = user_email
            if config['use_gmail'] == 'yes' or not user_email:
                frm = config['feedback_email']
                pword = config['feedback_password']
            else:
                frm = user_email
                pword = None
            mail(config['smtp_server'], config['smtp_port'],
                frm, pword,
                'founders@harmonize.fm', subject, message, cc=cc)

        if not 'paste.testing_variables' in request.environ:
            thread.start_new_thread(sendmail, ())
        return '1'

    def blog(self, id):
        c.entries = Session.query(BlogEntry).order_by(sql.desc(BlogEntry.timestamp))
        c.main = True
        return render('/blog.mako')

    def home(self):
        user = Session.query(User).get(session['userid'])
        c.entries = user.feed_entries
        c.main = True
        c.user = user
        c.num_songs = c.user.song_count

        c.fbapp_href = "http://www.facebook.com/apps/application.php?id=%s" % \
            config['pyfacebook.appid']
        c.appid = config['pyfacebook.appid']
        if 'Windows' in request.headers['User-Agent']:
            c.platform = 'windows'
        elif 'Macintosh' in request.headers['User-Agent']:
            c.platform = 'mac'
        return render('/home.mako')
        
    def set_volume(self, id):
        user = Session.query(User).get(session['userid'])
        user.lastvolume = id
        Session.add(user)
        Session.commit()
        return '1'

