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

from masterapp.lib.base import *
import cPickle
pickle = cPickle

from masterapp import model

log = logging.getLogger(__name__)

class UploadsController(BaseController):
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
        song = model.Session.query(model.File).join(model.Owner)
        song = song.filter(model.File.sha == f_sha)
        song = song.filter(model.Owner.user == user)
        song = song.first()
        if song != None:
            return True

        # Check to see if anybody else already has the song
        song = model.Session.query(model.File).filter_by(sha=f_sha).first()
        if song == None:
            return False

        #We already have the song, mark the user as having it
        new_owner = model.Owner()
        new_owner.file = song
        new_owner.user = user
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


    def fingerprint(self):
        # check session
        fbid = self._get_fbid(request)
        if fbid == None:
            return 'reauthenticate'

        # Check to make sure we got the right parameters
        version = request.params.get('version')
        if not version:
            abort(400, "A version number must be specified")

        file = dict(
            artist = request.params.get('artist'),
            album = request.params.get('album'),
            title = request.params.get('title'),
            date = request.params.get('date'),
            genre = request.params.get('genre'),
            tracknumber = request.params.get('tracknumber'),
            bitrate = request.params.get('bitrate'),
            duration = request.params.get('duration')
        )
        fingerprint = request.params.get('fingerprint')

        if fingerprint:
            # Look up the puid
            puid = lookup_fingerprint(fingerprint, **file)
        return puid

    def upload_new(self, id):
        """POST /uploads/id: This one uploads new songs for realsies"""
        # first get session key
        fbid = self._get_fbid(request)
        if fbid == None:
            try:
                self.read_postdata()
            except self.PostException:
                pass
            return 'reauthenticate'

        if config['app_conf']['check_df'] and \
                df.check(config['app_conf']['upload_dir']) > 80:
            try:
                self.read_postdata()
            except self.PostException:
                pass
            return 'wait'
            

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
                return 'retry'

            #finally, put the file in file_queue for processing
            fdict = {
                'fname': dest_path, 
                'fbid': fbid,
                'usersha': id
            }
            dest_file.close()
            pfile = pickle.dumps(fdict)
            fsock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            )
            port = int(config['pipeline_port'])
            fsock.connect(('localhost', port))
            fsock.send(pfile)
            fsock.shutdown(socket.SHUT_RDWR)
            fsock.close()
        else:
            try:
                self.read_postdata()
            except self.PostException:
                pass

        return 'file_uploaded'
        
    def file_exists(self, id):
        """GET /uploads/id : This is to check whether a file has already been
        uploaded or not. Returns a 1 if it has and a 0 otherwise"""
        fbid = self._get_fbid(request)

        if fbid == None:
            return 'reauthenticate'


        if config['app_conf']['check_df'] == 'true' and \
                df.check(config['app_conf']['upload_dir']) > 70:
            return 'wait'

        if self._file_already_uploaded(id, fbid):
            return 'file_uploaded'
        else:
            return 'upload_file'
    
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
