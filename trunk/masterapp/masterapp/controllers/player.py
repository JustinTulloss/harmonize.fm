# vim:expandtab:smarttab
import logging
import time

import S3
from masterapp.lib.base import *
from masterapp.lib.fbauth import ensure_fb_session, filter_friends
from masterapp.lib.profile import Profile
from masterapp.model import Session, User, File
from facebook import FacebookError
from facebook.wsgi import facebook
from pylons import config
import pylons

log = logging.getLogger(__name__)

DEFAULT_EXPIRATION = 5 #minutes to expire a song access URL

class PlayerController(BaseController):
    def __before__(self):
        ensure_fb_session()

    def index(self):
        c.profile = Profile()
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

        files= Session.query(File).\
            join(['owners', 'user']).filter(File.songid==int(id))
        files = filter_friends(files)
        files = files.all()
        # TODO: Think of a more efficient way of doing this. Perhaps the inuse
        # flag should be in the database?
        for file in files:
            for owner in file.owners:
                if not g.usedfiles.has_key((file.id, owner.id)):
                    qsgen = S3.QueryStringAuthGenerator(
                        config['S3_accesskey'], config['S3_secret']
                    )
                    qsgen.set_expires_in(DEFAULT_EXPIRATION*60)
                    
                    #Mark the file as in use, with the time it can come back
                    g.usedfiles[(file.id, owner.id)] = \
                        time.time()+DEFAULT_EXPIRATION*60
                    session['playing'] = (file.id, owner.id)
                    session.save()
                    return qsgen.get(config['S3_music_bucket'], file.sha)
        #if we get here, all files are in use! Damn it!
        session['playing'] = None
        session.save()
        return 'false'

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
	
    def add_rec(self):
        type = request.params.get('type')
        myid = request.params.get('id')
        if type == 'album': #recommending entire album
            myalbum = Session.query(Songs).filter_by(album_id=myid).all()
            for mysong in myalbum:
                mysong.recommendations = mysong.recommendations + 1
        elif type == 'song': #individual song
            mysong = Session.query(Songs).filter_by(id=myid).one()
            mysong.recommendations = mysong.recommendations + 1
        elif type == 'artist':
            myalbum = Session.query(Songs).filter_by(artist=myid).all()
            for mysong in myalbum:
                mysong.recommendations = mysong.recommendations + 1
        else:
            return "Failure"
        #Session.save(mysong)  - this should work and use less resources...
        Session.commit()
        return "Success"    
