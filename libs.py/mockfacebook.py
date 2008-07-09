# Justin Tulloss
#
# A very simple mock facebook for testing

from mock import Mock, sentinel

#My uuid generator rocks
uuid = 0
def get_uuid():
    global uuid
    uuid += 1
    return uuid

class MockFacebook(object):
    
    _session_key = None
    _uid = None

    # Preset return values
    configured_friends = None
    configured_info = None
    configured_user_info = None

    # Namespaces
    auth = Mock()
    fbml = Mock()
    feed = Mock()
    fql = Mock()
    friends = Mock()
    notifications = Mock()
    profile = Mock()
    users = Mock()
    pages = Mock()
    events = Mock()
    groups = Mock()
    photos = Mock()
    marketplace = Mock()
    get_login_url = Mock()

    # Base methods
    get_login_url = Mock()
    get_login_url.return_value = 'loggin now for cheap hookers and light beer!!'
    check_session = Mock()
    check_session.return_value = True
    def __init__(self, apikey, secret):
        pass

    def _get_session_key(self):
        if self._session_key:
            return self._session_key
        else:
            self._session_key=get_uuid()
            return self._session_key
    def _set_session_key(self, key):
        self._session_key = key

    session_key = property(_get_session_key, _set_session_key)

    def _get_uid(self):
        if self._uid:
            return self._uid
        else:
            self._uid = get_uuid()
            return self._uid
    def _set_uid(self, id):
        self._uid = id

    uid = property(_get_uid, _set_uid)

    def configure_friends(friends):
        self._friends = friends

    # Namespace mocked methods
    friends.get = Mock()
    friends.get.return_value = configured_friends

    friends.getAppUsers = Mock()
    friends.getAppUsers.return_value = configured_friends

    def getuserinfo(self, fbid, fields):
        if fields:
            return configured_user_info
        else:
            return configured_info
    users.getInfo = getuserinfo



