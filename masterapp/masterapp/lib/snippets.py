from masterapp.lib.base import request
from masterapp.model import Session, User
from pylons import session
from decimal import Decimal

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
    
def get_user():
    friendid = request.params.get('friend')
    if not friendid:
        user = Session.query(User).get(session['userid'])
    else:
        # TODO: Make sure they're friends
        user = Session.query(User).get(friendid)
    return user

def is_ie6(user_agent):
	if user_agent.find('MSIE 6.0') >= 0:
		for not_6 in ('MSIE 7.0', 'Opera', 'Netscape'):
			if user_agent.find(not_6) >= 0:
				return False
		return True
	else:
		return False
