import time
from facebook.wsgi import facebook
from facebook import FacebookError
from decorator import decorator
from pylons.controllers.util import abort
from pylons import request

from masterapp.lib import fblogin
import time

@decorator
def fbaccess(func, *args, **kwargs):
    tries = 0
    while tries < 4:
        try:
            return func(*args, **kwargs)
        except Exception, e:
            if isinstance(e, FacebookError) and e.code == 102:
                method = request.environ.get('HTTP_X_REQUESTED_WITH')
                if method == 'XMLHttpRequest':
                    abort(401, 'Please re-login to facebook')
                else: 
                    fblogin.login()
            else:
                tries = tries + 1
                time.sleep(.1)
