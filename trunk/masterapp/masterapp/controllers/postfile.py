from pylons import config
from masterapp.lib.base import *
import os,sys,shutil

import guid
from fileprocess.fileprocess import file_queue

SUCCESS = "Great work kiddos!"

class PostfileController(BaseController):
    def index(self):
        dir = config['app_conf']['upload_dir']
        fname = os.path.join(dir, guid.generate())
        f = open(fname,'wb')
        shutil.copyfileobj(request.POST['file'].file, f)
        f.close()
        fdict = dict(fname=fname, fbsession=request.POST['fbsession'])
        file_queue.put(fdict)
        return SUCCESS
