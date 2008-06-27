# vim:expandtab:smarttab
import logging
import S3
import socket
import cPickle as pickle
from masterapp.lib.base import *
from masterapp.lib.fbauth import ensure_fb_session
from masterapp.model import Session, File, Song, Album, BlogEntry, User, Whitelist
from mako.template import Template
from pylons import config

log = logging.getLogger(__name__)

DEFAULT_EXPIRATION = 30 #minutes to expire a song access URL

class AdminController(BaseController):

    admin = [1908861,1909354, 1932106]

    def __before__(self):
        ensure_fb_session()
        user = Session.query(User).get(session['userid'])
        if not user.fbid in self.admin:
            redirect_to('/')

    def index(self):
        return render('/admin.mako')

    def rmentities(self):
        c.albums = Session.query(Album).all()
        c.songs = []
        return render('/admin/rmentities.mako')

    def rmsongs(self):
        self._rmentity(Song)

    def rmalbums(self):
        self._rmentity(Album)

    def _rmentity(self, rmclass):
        for id in request.params.iterkeys():
            entity = Session.query(rmclass).get(id)
            if entity:
                Session.delete(entity)
        Session.commit()
        redirect_to(action='rmentities')
        
    def s3cleanup(self):
        a = S3.AWSAuthConnection(config['S3.accesskey'], config['S3.secret'])
        files = a.list_bucket(config['S3.music_bucket']).entries
        for file in files:
            db=Session.query(File).filter(File.sha==file.key).first()
            if db:
                files.remove(file)
        removed =[]
        for file in files:
            removed.append(file.key)
            if request.params.get('doit'):
                a.delete(config['S3.music_bucket'], file.key)

        return removed

    def monitor(self):
        try:
            fplog = open('/var/log/rubicon/filepipe' , 'r')
            c.fplog = fplog.read()
            c.fplog = c.fplog.replace('\n', '<br>')
            fplog.close()

            accesslog = open('/var/log/rubicon/access.log' , 'r')
            c.accesslog = accesslog.read()
            c.accesslog = c.accesslog.replace('\n', '<br>')
            accesslog.close()
        except:
            pass

        return render('/admin/monitor.mako')

    def blog(self):
        return render('/admin/blogentry.mako')

    def postblog(self):
        title = request.params.get('title')
        author = request.params.get('author')
        entry = request.params.get('entry')
        b = BlogEntry(title=title, author=author, entry=entry)
        Session.save(b)
        Session.commit()
        return 'Success!'

    def monitor_pipeline(self):
        try:
            msock = socket.socket()
            port = int(config['pipeline_port'])+1
            msock.connect(('localhost', port))
        except socket.error:
            return "Could not connect to file pipeline"

        msock.send('1') #Wakes up the monitor thread
        received = None
        msg = ''
        while received != '':
            received = msock.recv(512)
            msg = msg+received

        c.status = pickle.loads(msg)
        return render('/admin/monitor_pipeline.mako')

    def manage_whitelist(self):
        c.whitelists = Session.query(Whitelist).all()
        return render('/admin/manage_whitelist.mako')

    def remove_from_whitelist(self):
        for id in request.params.iterkeys():
            entry = Session.query(Whitelist).get(id)
            if entry:
                Session.delete(entry)
            Session.commit()
            redirect_to(action='manage_whitelist')

    def add_to_whitelist(self):
        fbid = request.params.get('fbid')
        w = Whitelist(fbid=fbid, registered=False)
        Session.save(w)
        Session.commit()
        redirect_to(action='manage_whitelist')
