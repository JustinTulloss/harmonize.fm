from facebook.wsgi import facebook
from pylons import session, request
import re
def login():
    session['fbsession'] = None
    session.save()
    qry_string = request.environ['QUERY_STRING']
    auth_match = re.search('&auth_token=[A-Za-z0-9]+', qry_string)
    if auth_match:
        qry_string = qry_string.replace(auth_match.group(), '')
        
    next = '%s?%s' % \
        (request.environ['PATH_INFO'], qry_string)
    url = facebook.get_login_url(next=next, canvas=False)
    facebook.redirect_to(url)

