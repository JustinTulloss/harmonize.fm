"""The application's Globals object"""
from pylons import config

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application
    """

    def __init__(self):
        """One instance of Globals is created during application
        initialization and is available during requests via the 'g'
        variable
        """
        # This is a dictionary of all the file ids currently being played
        # in the system right now. It's keyed by the file.id and the owners
        # collection is the value
        self.usedfiles = dict()