"""
A place for various useful decorators, created to move to cjson
"""

import logging
import cjson
import pylons
from decorator import decorator
from pylons.decorators import jsonify, validate
log = logging.getLogger(__name__)
from decimal import Decimal
from masterapp.lib.base import request

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

def build_json(results):
	json = { "data": []}
	for row in results:
		lrow = {}
		for key in row.keys():
			value = getattr(row, key)
			if isinstance(value, Decimal):
				value = int(value)
			lrow[key] = value
		json['data'].append(lrow)
		json['data'][len(json['data'])-1]['type'] = request.params.get('type')
	json['success']=True
	return json
	

def d_build_json(func):
	def wrapper(self, *args):
		return build_json(func(self, *args))
	return wrapper
