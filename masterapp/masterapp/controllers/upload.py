# vim:expandtab:smarttab
import logging
from pylons import g, Response, config, cache
import os
import socket
import os.path as path
import facebook
from facebook import FacebookError
from urllib2 import URLError
import df
from puid import lookup_fingerprint
from musicbrainz2.webservice import (
    Query,
    TrackFilter,
    WebServiceError
)

from facebook.wsgi import facebook
from sqlalchemy.sql import or_

from masterapp.lib.base import *
import cPickle as pickle
import simplejson

from masterapp import model
from sqlalchemy.sql import and_
import thread
from mailer import mail
from masterapp.lib.fbaccess import fbaccess_noredirect

log = logging.getLogger(__name__)

class Response(object):
    upload = 'upload'
    reauthenticate = 'reauthenticate'
    done = 'done'
    upload = 'upload'
    wait = 'wait'
    retry = 'retry'

class UploadController(BaseController):
    def __init__(self, *args):
        super(BaseController, self).__init__(args)
        self.apikey = config['pyfacebook.apikey']
        self.secret = config['pyfacebook.secret']

    def _check_tags(self, user, fdict):
        song = None
        if fdict.has_key('title') and fdict.has_key('album') and \
                fdict.has_key('artist'):
            qry = model.Session.query(model.Song).join(
                model.Song.artist, model.Song.album).filter(
                model.Artist.name == fdict['artist']).filter(
                model.Album.title == fdict['album']).filter(
                model.Song.title == fdict['title'])
            song = qry.first()

        if not song:
            return False

        # Check to see if this user owns this songs
        owner = model.Session.query(model.SongOwner).filter(
            and_(model.SongOwner.songid==song.id, 
                model.SongOwner.uid == user.id)
        ).first()
        if owner:
            # This request.params has already been uploaded by this fella
            log.debug('%s has already been uploaded by %s', 
                fdict.get('title'), user.id)
            return True

        # Make a new owner
        user.add_song(song)
        log.debug('%s added to %s\'s files', fdict.get('title'), user.id)
        return True


    def _build_fdict(self, user, src=None):
        if not src:
            src = request.params
        return dict(
            puid = src.get('puid'),
            artist = src.get('artist'),
            album = src.get('album'),
            title = src.get('title'),
            duration = src.get('duration'),
            bitrate = src.get('bitrate'),
            date = src.get('date'),
            tracknumber = src.get('tracknumber'),
            genre = src.get('genre'),
            fbid = user.fbid
        )

    def _check_puid(self, user):
        userpuid = request.params.get('puid')
        if not userpuid:
            log.debug("Puid was blank, upload the file")
            return False

        dbpuids = model.Session.query(model.Puid).filter(
            model.Puid.puid == userpuid
        ).all()
        if len(dbpuids) > 0:
            self._process(self._build_fdict(user))
            log.debug("We have the puid for %s in our db, don't need the song",
                request.params.get('title'))
            return True
        return False

    def _get_user(self, fbid):
        return model.Session.query(model.User).filter_by(fbid = fbid).one()

    def _get_fbid(self, request):
        session_key = request.params.get('session_key')
        if session_key == None:
            return None
        
        @fbaccess_noredirect
        def get_fbid():
            facebook.session_key = session_key
            fbid = facebook.users.getLoggedInUser()
            if type(fbid) == int:
                return str(fbid)
            return fbid

        sessionc = cache.get_cache('upload.sessions')
        return sessionc.get(session_key,
            expiretime = 120,
            createfunc = get_fbid
        )
        
    class PostException(Exception):
        """An exception that means the content-length did not match the actual
           amount of data read"""
        pass

    def read_postdata(self, dest_file=None):
        """Reads the postdata into the file object or throws it away 
           otherwise"""
        chunk_size = 1024
        file_size = int(request.environ["CONTENT_LENGTH"])
        body = request.environ['wsgi.input']

        for i in range(0, file_size/chunk_size):
            data = body.read(chunk_size)
            if len(data) != chunk_size:
                raise self.PostException
            if dest_file != None:
                dest_file.write(data)

        data = body.read(file_size%chunk_size)
        if len(data) != file_size%chunk_size:
            raise self.PostException
        if dest_file != None:
            dest_file.write(data)

    def _process(self, file):
        pfile = pickle.dumps(file)
        fsock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        port = int(config['pipeline_port'])
        fsock.connect(('localhost', port))
        fsock.send(pfile)
        fsock.shutdown(socket.SHUT_RDWR)
        fsock.close()
        
    def file(self, id):
        """POST /upload/file/id: This one uploads new songs for realsies"""
        # first get session key
        try:
            fbid = self._get_fbid(request)
            if fbid == None:
                return Response.reauthenticate
        except Exception, e:
            try:
                self.read_postdata()
            except self.PostException:
                pass

            if hasattr(e, 'code') and e.code == 102:
                return Response.reauthenticate
            else:
                return Response.retry

        if config['app_conf']['check_df'] == 'true' and \
                df.check(config['app_conf']['upload_dir']) > 85:
            try:
                self.read_postdata()
            except self.PostException:
                pass
            return Response.wait

        dest_dir = path.join(config['app_conf']['upload_dir'], fbid)
        if not path.exists(dest_dir):
            os.mkdir(dest_dir)
        dest_path = os.path.join(dest_dir, id)

        if not os.path.exists(dest_path):
            dest_file = file(dest_path, 'wb')

            try:
                self.read_postdata(dest_file)
            except self.PostException, e:
                dest_file.close()
                os.remove(dest_path)
                return Response.retry

            dest_file.close()

            #finally, put the file in file_queue for processing
            fdict = {
                'fname': dest_path, 
                'fbid': fbid,
                'usersha': id,
                'puid': request.params.get('puid')
            }
            self._process(fdict)
        else:
            try:
                self.read_postdata()
            except self.PostException, e:
                log.warn("A problem occurred with the post: %s", e)

        return Response.done
        
    def tags(self):
        try:
            fbid = self._get_fbid(request)
            if fbid == None:
                return Response.reauthenticate
        except Exception, e:
            if hasattr(e, 'code') and e.code == 102:
                return Response.reauthenticate
            else:
                return Response.retry
        user = self._get_user(fbid)

        # Check for api version
        version = request.params.get('version')
        if not version=='1.0':
            abort(400, 'Version must be 1.0')

        if request.params.get('tags'):
            return self._mass_tags(user, request.params['tags'])

        # Check our database for tag match
        if self._check_tags(user, self._build_fdict(user)):
            return Response.done

        # Check our database for PUID
        if self._check_puid(user):
            return Response.done

        # We haven't seen the song, let's get the whole file
        return Response.upload

    def _mass_tags(self, user, str_tags):
        tag_list = simplejson.loads(str_tags)
        if type(tag_list) != list:
            abort(400, 'Invalid tags sent')

        response_list = []
        for tags in tag_list:
            if self._check_tags(user, self._build_fdict(user, tags)):
                response_list.append(Response.done)
            else:
                response_list.append(Response.upload)

        return simplejson.dumps(response_list)
            
    @fbaccess_noredirect
    def desktop_redirect(self):
        if facebook.check_session(request):
            url = 'http://localhost:26504/complete_login?session_key='+ \
                facebook.session_key
        else:
            abort(404)
        #session_key returns unicode, have to convert back to string
        redirect_to(str(url)) 

    def desktop_login(self):
        url = facebook.get_login_url(canvas=False,next='/desktop_redirect')
        redirect_to(str(url))

    def upload_ping(self):
        return ''

    def error(self):
        client_size = int(request.environ["CONTENT_LENGTH"])
        read_size = min(client_size, 4096)
        stack_trace = request.environ['wsgi.input'].read(read_size)
        if stack_trace == '':
            return '0'
        def sendmail():
            if config['use_gmail'] == 'yes':
                password = config['feedback_password']
            else:
                password = None

            mail(config['smtp_server'], config['smtp_port'],
                config['feedback_email'], password,
                'brian@harmonize.fm', 'Uploader exception', stack_trace)
        thread.start_new_thread(sendmail, ())
        return '1'
