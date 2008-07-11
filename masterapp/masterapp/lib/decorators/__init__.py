# vim:expandtab:smarttab
"""
A place for various useful decorators, created to move to cjson
"""

import logging
import cjson
import pylons
from decorator import decorator
from pylons.decorators import jsonify, validate
log = logging.getLogger(__name__)
from masterapp.lib.snippets import get_user, build_json

@decorator
def cjsonify(func, *args, **kwargs):
    """Action decorator that formats output for JSON

    Given a function that will return content, this decorator will
    turn the result into JSON, with a content-type of 'text/javascript'
    and output it.
    """
    pylons.response.headers['Content-Type'] = 'application/json'
    data = func(*args, **kwargs)
    if isinstance(data, list):
        msg = "JSON responses with Array envelopes are susceptible to " \
              "cross-site data leak attacks, see " \
              "http://pylonshq.com/warnings/JSONArray"
        warnings.warn(msg, Warning, 2)
        log.warning(msg)
    return cjson.encode(data)

def d_build_json(func):
    def json_wrapper(*args, **kwargs):
        return build_json(func(*args, **kwargs))
    return json_wrapper

def pass_user(func):
    def pu_wrapper(self, *args, **kwargs):
        user = get_user()
        return func(self, user, *args, **kwargs)
    return pu_wrapper

