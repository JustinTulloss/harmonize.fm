import logging
import os 

from masterapp.lib.base import *

log = logging.getLogger(__name__)

class UploadsController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('upload', 'uploads')

    def upload_new(self, id):
        """POST /uploads/id: This one uploads new songs for realsies"""
        dest_dir = config['app_conf']['upload_dir']
        dest_path = os.path.join(dest_dir, id)
        #need to actually make this file
        if not os.path.exists(dest_path):
            dest_file = file(dest_path, 'w')
            chunk_size = 1024
            file_size = int(request.environ["CONTENT_LENGTH"])
            for i in range(0, file_size, chunk_size):
              dest_file.write(request.body.read(chunk_size))

            dest_file.write(request.body.read(file_size%chunk_size))

        return "1"
        
    def file_exists(self, id):
        """GET /uploads/id : This is to check whether a file has already been
        uploaded or not. Returns a 1 if it has and a 0 otherwise"""
        return '0'
