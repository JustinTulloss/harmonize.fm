from paste.deploy import CONFIG
from masterapp.lib.base import *
import os,sys,shutil

import guid
from fprocessor.fprocessor import file_queue

SUCCESS = "Great work kiddos!"

class PostfileController(BaseController):
    def index(self):
        dir = CONFIG['app_conf']['upload_dir']
        fname = os.path.join(dir, guid.generate())
        f = open(fname,'wb')
        shutil.copyfileobj(request.POST['file'].file, f)
        f.close()
        f = open(fname, 'rb')
        file_queue.put(f)
        # Return a rendered template
        #   return render_response('/some/template.html')
        # or, Return a response object
        return Response(SUCCESS)
