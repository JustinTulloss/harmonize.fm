# vim:expandtab:smarttab
import logging
from pylons import g, Response
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

from sqlalchemy.sql import or_

from masterapp.lib.base import *
import cPickle as pickle

from masterapp import model

log = logging.getLogger(__name__)

class Response(object):
    upload = 'upload'
    reauthenticate = 'reauthenticate'
    done = 'done'
    upload = 'upload'
    wait = 'wait'
    retry = 'retry'

upload_response = Response()

class UploadController(BaseController):
    def __init__(self, *args):
        super(BaseController, self).__init__(args)
        self.apikey = config['pyfacebook.apikey']
        self.secret = config['pyfacebook.secret']

    def _file_already_uploaded(self, f_sha, fbid):
        """Checks to see if a song has already been uploaded and marks that user
            as having uploaded it if true"""
        user = model.Session.query(model.User).filter_by(fbid=fbid).first()
        if user == None:
            user = model.User(fbid)
            model.Session.save(user)
        
        # Check so see if the user has already uploaded the file
        song = model.Session.query(model.File).join(model.SongOwner)
        song = song.filter(model.File.sha == f_sha)
        song = song.filter(model.SongOwner.user == user)
        song = song.first()
        if song != None:
            return True

        # Check to see if anybody else already has the song
        song = model.Session.query(model.File).filter_by(sha=f_sha).first()
        if song == None:
            return False

        #We already have the song, mark the user as having it
        new_owner = model.SongOwner(song=song, user=user)
        model.Session.save(new_owner)

        model.Session.commit()
        return True

    def _get_fb(self):
        return facebook.Facebook(self.apikey, self.secret)

    def _get_fbid(self, request):
        session_key = request.params.get('session_key')
        if session_key == None:
            return None
        
        fb = self._get_fb()
        retries = 2
        while retries > 0:
            try:
                fb.session_key = session_key
                fbid = fb.users.getLoggedInUser()
                retries = 0 
            except FacebookError:
                return None
            except URLError:
                print 'getLoggedInUser error, retrying'
                retries -= 1
                if retries == 0: 
                    print 'getLoggedInUser failed'
                    return None

        return fbid

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
        fbid = self._get_fbid(request)
        if fbid == None:
            try:
                self.read_postdata()
            except self.PostException:
                pass
            return upload_response.reauthenticate

        if config['app_conf']['check_df'] == 'true' and \
                df.check(config['app_conf']['upload_dir']) > 85:
            try:
                self.read_postdata()
            except self.PostException:
                pass
            return upload_response.wait
            

        dest_dir = path.join(config['app_conf']['upload_dir'], fbid)
        if not path.exists(dest_dir):
            os.mkdir(dest_dir)
        dest_path = os.path.join(dest_dir, id)

        if not os.path.exists(dest_path):
            dest_file = file(dest_path, 'wb')

            try:
                self.read_postdata(dest_file)
            except self.PostException:
                os.remove(dest_path)
                return upload_response.retry

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

        return upload_response.done
        
    def tags(self):
        fbid = self._get_fbid(request)
        if not fbid:
            return upload_response.reauthenticate

        # Check for api version
        version = request.params.get('version')
        if not version=='1.0':
            abort(400, 'Version must be 1.0')

        # Check our database for PUID
        userpuid = request.params.get('puid')
        if not userpuid:
            log.debug("Puid was blank, upload the file")
            return upload_response.upload

        def build_fdict():
            return dict(
                puid = request.params.get('puid'),
                artist = request.params.get('artist'),
                album = request.params.get('album'),
                title = request.params.get('title'),
                duration = request.params.get('duration'),
                bitrate = request.params.get('bitrate'),
                date = request.params.get('date'),
                tracknumber = request.params.get('tracknumber'),
                genre = request.params.get('genre'),
                fbid = fbid
            )

        dbpuids = model.Session.query(model.Puid).filter(
            model.Puid.puid == userpuid
        ).all()
        if len(dbpuids) > 0:
            self._process(build_fdict())
            log.debug("We have the puid for %s in our db, don't need the song",
                request.params.get('title'))
            return upload_response.done

        # We haven't seen the song, let's get the whole file
        return upload_response.upload
            
    def desktop_redirect(self):
        fb = self._get_fb()
        if fb.check_session(request):
            url = 'http://localhost:26504/complete_login?session_key='+ \
                fb.session_key
        else:
            url = 'http://localhost:26504/login_error.html'
        #session_key returns unicode, have to convert back to string
        redirect_to(str(url)) 

    def desktop_login(self):
        url = self._get_fb().get_login_url(canvas=False,next='/desktop_redirect')
        redirect_to(str(url))

    def upload_ping(self):
        return ''
