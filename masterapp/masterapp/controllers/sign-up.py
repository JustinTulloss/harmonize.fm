# vim:expandtab:smarttab
import logging
import time



from masterapp.lib.base import *
from masterapp.config import schema
from masterapp.model import (
    Session, 
    Notification)
import pylons
from sqlalchemy.orm import aliased
from sqlalchemy.sql import or_, and_
import sqlalchemy.sql as sql

import re
import thread

import masterapp.lib.snippets as snippets

log = logging.getLogger(__name__)

class SignUpController(BaseController):
    def __init__(self):
        BaseController.__init__(self)
        self.email_regex = re.compile("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+\.[a-zA-Z]{2,6}$")


    def index(self):
        if request.params.has_key('email'):
            # we've submitted the form
            email = request.params.get('email')
            qry = Session.query(Notification).filter(Notification.email == email)
            if qry.count() == 0: # this user hasn't already asked to be notified
                n = Notification(email)
                Session.save(n)
                Session.commit()
            return render('/pages/thankyou.mako.html')
        else:
            # we haven't submitted yet
            return render('/pages/sign-up.mako.html')

