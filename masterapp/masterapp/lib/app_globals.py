"""The application's Globals object"""
from pylons import session
from masterapp.model import Session, User

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application
    """

    def __init__(self):
        """One instance of Globals is created during application
        initialization and is available during requests via the 'g'
        variable
        """

    def get_session_user(self):
        return Session.query(User).get(session['userid'])
    session_user = property(user)
