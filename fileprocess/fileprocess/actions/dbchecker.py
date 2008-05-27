import logging
import os
import fileprocess
from baseaction import BaseAction
from sqlalchemy import and_, engine_from_config
from pylons import config as pconfig
from mock import Mock
from fileprocess.configuration import config

log = logging.getLogger(__name__)

class DBChecker(BaseAction):
    """
    This class checks to see if the user is established, whether or not this
    file has been uploaded by this user, and whether or not this file
    has been uploaded by any user. Pretty much just tries to see whether
    we need to continue with the less pleasant pieces of processing this file
    """

    def __init__(self, *args, **kwargs):
        super(DBChecker, self).__init__(*args, **kwargs)
        pconfig['pylons.g'] = Mock()
        pconfig['pylons.g'].sa_engine = engine_from_config(config,
            prefix = 'sqlalchemy.default.'
        )
        from masterapp import model
        self.model = model

    def process(self, file):
        assert file and len(file)>0 and \
            file.has_key('fbid') and file.has_key('sha')

        # Get this user, create him if he doesn't exist
        qry = self.model.Session.query(self.model.User).filter(
            self.model.User.fbid == file['fbid']
        )
        user = qry.first()
        if user == None:
            user = self.model.User()
            user.fbid = file['fbid']
            self.model.Session.save(user)
            self.model.Session.commit()

        file['dbuser'] = user

        # Check to see if this file has already been uploaded by this person.
        qry = self.model.Session.query(self.model.Owner).join('file').filter(
            and_(self.model.File.sha == file['sha'], self.model.Owner.id==user.id)
        )
        ownerfile = qry.first()
        if ownerfile != None:
            #Just bail now, this file's already been uploaded
            log.debug('%s has already been uploaded by %s', 
                file.get('fname'), file['fbid'])
            file['msg'] = "File has already been uploaded by user"
            file['na'] = fileprocess.na.NOTHING
            self.cleanup(file)
            return False

        qry = self.model.Session.query(self.model.File).filter(
            self.model.File.sha==file['sha']
        )
        dbfile = qry.first()
        if dbfile is not None: #this file exists, create a owner and get out
            owner = self.model.Owner()
            owner.file = dbfile
            owner.user = user
            log.debug("Adding %s to %s's music", file.get('title'), file['fbid'])
            self.model.Session.save(owner)
            self.model.Session.commit()
            log.debug('%s already uploaded, removing', file.get('fname'))
            self.cleanup(file)
            return False

        self.model.Session.remove()
        return file
