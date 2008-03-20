import logging
import os
from baseaction import BaseAction
import fileprocess
from pylons import config
from facebook import Facebook, FacebookError

log = logging.getLogger(__name__)

class FacebookAction(BaseAction):
    """
    This action fetches any data we might need on a user from facebook
    """
    def __init__(self, *args):
        super(FacebookAction, self).__init__(args)
        self.apikey = config['pyfacebook.apikey']
        self.secret = config['pyfacebook.secret']
    def process(self, file):
        facebook = Facebook(self.apikey, self.secret)
        facebook.session_key = file['fbsession']
        try:
            userinfo = facebook.users.getLoggedInUser()
        except FacebookError, e:
            #TODO: Error handling. What do we do if the user isn't logged in?
            if e.code == 102: #session key has expired
                log.info('%s is not a valid session, removing upload', 
                    file['fbsession'])
                file['msg'] = "Facebook session not valid"
                file['na'] = fileprocess.na.AUTHENTICATE
                self.cleanup(file)
                return False


        file['fbid']=userinfo
        log.debug('Found user %s', userinfo)

        return file
