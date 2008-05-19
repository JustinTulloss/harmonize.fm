import logging
import os
import fileprocess
from baseaction import BaseAction
from sqlalchemy import and_

log = logging.getLogger(__name__)

class DBChecker(BaseAction):
    """
    This class checks to see if the user is established, whether or not this
    file has been uploaded by this user, and whether or not this file
    has been uploaded by any user. Pretty much just tries to see whether
    we need to continue with the less pleasant pieces of processing this file
    """

    def process(self, file):
        assert file and len(file)>0 and \
            file.has_key('fbid') and file.has_key('sha')

        from masterapp import model

        # Get this user, create him if he doesn't exist
        qry = model.Session.query(model.User).filter(
            model.User.fbid == file['fbid']
        )
        user = qry.first()
        if user == None:
            user = model.User()
            user.fbid = file['fbid']
            model.Session.save(user)
            model.Session.commit()

        file['dbuser'] = user

        # Check to see if this file has already been uploaded by this person.
        qry = model.Session.query(model.Owner).join('file').filter(
            and_(model.File.sha == file['sha'], model.Owner.id==user.id)
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

        qry = model.Session.query(model.File).filter(
            model.File.sha==file['sha']
        )
        dbfile = qry.first()
        if dbfile is not None: #this file exists, create a owner and get out
            owner = model.Owner()
            owner.file = dbfile
            owner.user = user
            log.debug("Adding %s to %s's music", file.get('title'), file['fbid'])
            model.Session.save(owner)
            model.Session.commit()
            log.debug('%s already uploaded, removing', file.get('fname'))
            self.cleanup(file)
            return False

        model.Session.remove()
        return file
