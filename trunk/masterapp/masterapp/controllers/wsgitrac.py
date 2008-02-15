#Trac WSGI interface

from masterapp.lib.base import *
from trac.web.main import dispatch_request
from facebook.wsgi import *
import StringIO, urllib

#from authkit.permissions import NotAuthenticatedError
import os

template = """\
            <html>
            <head><title>Please Login!</title></head>
            <body>
            <h1>Please Login</h1>
            <form action="" method="post">
            <dl>
            <dt>Username:</dt>
            <dd><input type="text" name="username"></dd>
            <dt>Password:</dt>
            <dd><input type="password" name="password"></dd>
            </dl>
            <input type="hidden" name="r" value="%s" />
            <input type="submit" name="authform" />
            <hr />
            </form>
            </body>
            </html>
            """

class WsgitracController(BaseController):

    def tracpage(self, *args, **kwargs):
        # Thanks to ianbicking for a workaround of an empty wsgi.input value
        if request.environ.get('paste.parsed_formvars', False):
            wsgi_input = urllib.urlencode(
                request.environ['paste.parsed_formvars'][0], True)
            request.environ['wsgi.input'] = StringIO.StringIO(wsgi_input)
            request.environ['CONTENT_LENGTH'] = len(wsgi_input)

        os.environ['TRAC_ENV'] = "/home/jmtulloss/trac11"

        if request.environ['PATH_INFO'] == '/logout':
            del(session['user'])
            session.save()
            h.redirect_to('/')

        next = request.environ['SCRIPT_NAME']+request.environ['PATH_INFO']
        if session.get('user') == None:
            fbresult = facebook.check_session(request, next=next)
            if fbresult:
                return fbresult
            info = facebook.users.getInfo([facebook.uid],['name'])[0]
            session['user']=info['name']+':'+facebook.uid
            session.save()

        request.environ['REMOTE_USER'] = session.get('user')

        a = dispatch_request(request.environ, self.start_response)
        if len(a) == 0:
            return ['']
        return a
