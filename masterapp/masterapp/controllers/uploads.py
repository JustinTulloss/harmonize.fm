# vim:expandtab:smarttab
from __future__ import with_statement
import logging
from pylons import g
import os
from facebook.wsgi import facebook

from masterapp.lib.base import *
from fileprocess.fileprocess import file_queue, na, msglock, msgs

log = logging.getLogger(__name__)

class UploadsController(BaseController):
    def upload_new(self, id):
        """POST /uploads/id: This one uploads new songs for realsies"""
        #first get session key
        session_key = request.params.get('session_key')
        if session_key == None:
            return '0'

        dest_dir = config['app_conf']['upload_dir']
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
            if msgs.get(session_key) == None:
                with msglock:
                    msgs[session_key] = []

            fdict = dict(fname=dest_path, fbsession=session_key) 
            file_queue.put(fdict)
            dest_file.close()

        return '1'
        
    def file_exists(self, id):
        """GET /uploads/id : This is to check whether a file has already been
        uploaded or not. Returns a 1 if it has and a 0 otherwise"""
        #This is temporary
        dest_dir = config['app_conf']['upload_dir']
        dest_path = os.path.join(dest_dir, id)
        if os.path.exists(dest_path):
            return '1'
        else:
            return '0'
    
    def desktop_redirect(self):
        if facebook.check_session(request):
            url = 'http://localhost:8080/complete_login?session_key='+ \
                facebook.session_key
        else:
            url = 'http://localhost:8080/login_error.html'
        #session_key returns unicode, have to convert back to string
        redirect_to(str(url)) 

    def desktop_login(self):
        url = facebook.get_login_url(canvas=False, next='/desktop_redirect')
        redirect_to(str(url))
