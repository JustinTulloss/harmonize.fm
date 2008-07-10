from facebook.wsgi import facebook
from facebook import FacebookError
from decorator import decorator
from pylons.controllers.util import abort

from masterapp.lib import fblogin

@decorator
def fbaccess(func, self, *args, **kwargs):
    tries = 0
    while tries < 4:
        try:
            return func(self, *args, **kwargs)
        except FacebookError, e:
            if e.code == 102:
                method = request.environ.get('HTTP_X_REQUESTED_WITH')
                if method == 'XMLHttpRequest':
                    abort(401, 'Please re-login to facebook')
                else: 
                    fblogin.login()
            else:
                tries = tries + 1
                time.sleep(.1)
