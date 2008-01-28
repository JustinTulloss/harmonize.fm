import logging
from baseaction import BaseAction

log = logging.getLogger(__name__)

class Facebook(BaseAction):
    """
    This action fetches any data we might need on a user from facebook
    """
    def process(self, file):
        if facebook == None:
            from facebook.wsgi import facebook
        facebook.session_key = file['fbsession']
        userinfo = facebook.users.getLoggedInUser()

        #TODO: Error handling. What do we do if the user isn't logged in?

        file['fbid']=userinfo['uid']

        return file
