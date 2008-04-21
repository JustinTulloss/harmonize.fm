# vim:expandtab:smarttab
import logging
from pylons import g, Response
import os
import os.path as path
#from facebook.wsgi import facebook
import facebook
from facebook import FacebookError

from masterapp.lib.base import *
from fileprocess.fileprocess import file_queue, na, msgs

from masterapp import model

log = logging.getLogger(__name__)

class UploadsController(BaseController):
    def __init__(self, *args):
        super(BaseController, self).__init__(args)
        self.apikey = config['pyfacebook.apikey']
        self.secret = config['pyfacebook.secret']

    def file_already_uploaded(self, f_sha, fbid):
        """Checks to see if a song has already been uploaded and marks that user
            as having uploaded it if true"""
        song = model.Session.query(model.File).filter_by(sha=f_sha).first()
        if song == None:
            return False

        #We already have the song, mark the user as having it
        user = model.Session.query(model.User).filter_by(fbid=fbid).first()
        if user == None:
            user = model.User()
            user.fbid = fbid
            model.Session.save(user)
        
        new_owner = model.Owner()
        new_owner.file = song
        new_owner.user = user
        model.Session.save(new_owner)

        model.Session.commit()
        return True

    def get_fb(self):
        return facebook.Facebook(self.apikey, self.secret)

    def get_fbid(self, request):
        session_key = request.params.get('session_key')
        if session_key == None:
            return None
        
        fb = self.get_fb()
        try:
            fb.session_key = session_key
            fbid = fb.users.getLoggedInUser()
        except FacebookError:
            return None

        return fbid

    def upload_new(self, id):
        """POST /uploads/id: This one uploads new songs for realsies"""
        #first get session key
        fbid = self.get_fbid(request)
        if fbid == None:
            request.environ['wsgi.input'].read(request.environ['CONTENT_LENGTH'])
            return 'reauthenticate'

        dest_dir = path.join(config['app_conf']['upload_dir'], fbid)
        if not path.exists(dest_dir):
            os.mkdir(dest_dir)
        dest_path = os.path.join(dest_dir, id)

        if not os.path.exists(dest_path):
            dest_file = file(dest_path, 'w')
            chunk_size = 1024
            file_size = int(request.environ["CONTENT_LENGTH"])
            body = request.environ['wsgi.input']

            for i in range(0, file_size/chunk_size):
                dest_file.write(body.read(chunk_size))
 
            dest_file.write(body.read(file_size%chunk_size))

            #finally, put the file in file_queue for processing
            fdict = {
                'fname': dest_path, 
                'fbid': fbid,
                'usersha': id
            }
            file_queue.put(fdict)
            dest_file.close()

        return 'file_uploaded'
        
    def file_exists(self, id):
        """GET /uploads/id : This is to check whether a file has already been
        uploaded or not. Returns a 1 if it has and a 0 otherwise"""
        fbid = self.get_fbid(request)

        if fbid == None:
            return 'reauthenticate'

        if self.file_already_uploaded(id, fbid):
            return 'file_uploaded'
        else:
            return 'upload_file'
    
    def desktop_redirect(self):
        fb = self.get_fb()
        if fb.check_session(request):
            url = 'http://localhost:8080/complete_login?session_key='+ \
                fb.session_key
        else:
            url = 'http://localhost:8080/login_error.html'
        #session_key returns unicode, have to convert back to string
        redirect_to(str(url)) 

    def desktop_login(self):
        url = self.get_fb().get_login_url(canvas=False,next='/desktop_redirect')
        redirect_to(str(url))
