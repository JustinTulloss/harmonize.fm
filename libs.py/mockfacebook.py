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

    class MockUsers(object):
        """
        A mock for the users namespace since its a bit more complicated
        """
        configured_info = None
        configured_user_info = None

        def __init__(self, 
                configured_info, configured_user_info,
                configured_friend_info, uid):
            MockFacebook._uid = uid
            self.configured_info = configured_info
            self.configured_user_info = configured_user_info
            self.configured_friend_info = configured_friend_info

        def getInfo(self, id, fields=None):
            if fields:
                if id == MockFacebook._uid:
                    return self.configured_user_info
                else:
                    return self.configured_friend_info
            else:
                return self.configured_info

        def getLoggedInUser(self):
            return MockFacebook._uid

    # Namespaces
    auth = Mock()
    fbml = Mock()
    feed = Mock()
    fql = Mock()
    friends = Mock()
    notifications = Mock()
    profile = Mock()
    pages = Mock()
    events = Mock()
    groups = Mock()
    photos = Mock()
    marketplace = Mock()
    get_login_url = Mock()

    # Base methods
    get_login_url = Mock()
    get_login_url.return_value = 'login now for cheap hookers and light beer!!'
    check_session = Mock()
    check_session.return_value = True
    def __init__(self, apikey, secret):
        self.users = self.MockUsers(
            self.configured_info, self.configured_user_info,
            self.configured_friend_info, self.uid)

        # Namespace mocked methods
        self.friends.get = Mock()
        self.friends.get.return_value = self.configured_friends

        def getfriends():
            return self.configured_friends[int(self.uid)]
        self.friends.getAppUsers = getfriends


    def _get_session_key(self):
        if not self._session_key:
            self._session_key=get_uuid()
        return self._session_key
    def _set_session_key(self, key):
        self._session_key = key

    session_key = property(_get_session_key, _set_session_key)

    def _get_uid(self):
        if MockFacebook._uid:
            return MockFacebook._uid
        else:
            MockFacebook._uid = get_uuid()
            return MockFacebook._uid
    def _set_uid(self, id):
        MockFacebook._uid = id

    uid = property(_get_uid, _set_uid)

    def configure_friends(friends):
        self._friends = friends


    # Make this more legit in the future so we can test people who are not
    # necessarily friends
    friends.areFriends = Mock()
    friends.areFriends.return_value = [{'are_friends':True}]

