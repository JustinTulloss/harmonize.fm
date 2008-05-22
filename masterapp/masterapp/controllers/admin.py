# vim:expandtab:smarttab
import logging
import S3
import socket
import cPickle as pickle
from masterapp.lib.base import *
from masterapp.lib.fbauth import ensure_fb_session
from masterapp.model import Session, File, Song, Album, BlogEntry
from mako.template import Template
from pylons import config

log = logging.getLogger(__name__)

DEFAULT_EXPIRATION = 30 #minutes to expire a song access URL

class AdminController(BaseController):

    admin = [1908861,1909354]

    def __before__(self):
        ensure_fb_session()
        if not session['user'].fbid in self.admin:
            redirect_to('/')

    def index(self):
        return render('/admin.mako')

    def rmentities(self):
        c.albums = Session.query(Album).all()
        c.songs = Session.query(Song).all()
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
        queue_list = []
        for handler in config['filepipeline'].handlers:
            queue_list.append((handler.queue.qsize(), handler.queue.queue))

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
        msock = socket.socket()
        msock.connect(('localhost', 48261))
        msock.send('1') #Wakes up the monitor thread
        received = None
        msg = ''
        while received != '':
            received = msock.recv(512)
            msg = msg+received

        c.status = pickle.loads(msg)
        return render('/admin/monitor_pipeline.mako')
