import logging
import os
from baseaction import BaseAction
from sqlalchemy import and_

log = logging.getLogger(__name__)

class DBRecorder(BaseAction):
    """
    This action takes a dictionary of music data and inserts it into the database
    """
    def process(self, file):
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

        # Check to see if this file has already been uploaded by this person.
        qry = model.Session.query(model.Owner).join('file').filter(
            and_(model.File.sha == file['sha'], model.Owner.id==user.id)
        )
        ownerfile = qry.first()
        if ownerfile != None:
            #Just bail now, this file's already been uploaded
            os.remove(file['fname'])
            log.debug('%s has already been uploaded by %s', 
                file['fname'], file['fbid'])
            return False

        # Check to see if this file has been uploaded, 
        # just add it to this user if it has
        owner = model.Owner()
        owner.user = user
        owner.recommendations = 0
        owner.playcount = 0
        log.debug("Adding %s to %s's music", file['title'], file['fbid'])
        model.Session.save(owner)

        qry = model.Session.query(model.File).filter(
            model.File.sha==file['sha']
        )
        dbfile = qry.first()
        if dbfile == None:
            dbfile = model.File()
            dbfile.sha = file['sha']
            log.debug("New file %s added to files", file['sha'])
            model.Session.save(dbfile)
        else:
            owner.file = dbfile
            model.Session.update(owner)
            model.Session.commit()
            log.debug('%s already uploaded, removing', file['fname'])
            os.remove(file['fname'])
            return False
                        
        #Insert a new song if it does not exist
        qry = model.Session.query(model.Song).filter(
            model.Song.mbid==file["mbtrackid"]
        )
        song = qry.first()
        if song == None:
            song = model.Song()
            song.title = file['title']
            song.length = file['length']
            song.tracknumber = file['tracknumber']
            song.mbid = file['mbtrackid']
            log.debug("Saving new song %s", song.title)
            model.Session.save(song)

            # Insert a new album if it does not exist
            qry = model.Session.query(model.Album).filter(
                model.Album.mbid == file['mbalbumid']
            )
            album = qry.first()
            if album == None:
                album = model.Album()
                for key in file.keys():
                    try:
                        setattr(album, key, file[key])
                    except:
                        pass #This just means the album table doesn't store that piece of info
                album.title = file['album']
                album.mbid = file['mbalbumid']
                log.debug("Saving new album %s", album.title)
                model.Session.save(album)

        model.Session.commit()

        #Make sure our cross links are all in place
        song.albumid = album.albumid
        model.Session.update(song)
        owner.fileid = dbfile.id
        owner.uid = user.id
        model.Session.update(owner)
        dbfile.songid = song.id
        model.Session.update(dbfile)
        model.Session.commit()

        file['songid'] = song.id
        file['fileid'] = dbfile.id
        file['albumid'] = album.albumid
        file['ownerid'] = owner.id

        log.info('%s by %s successfully inserted into the database', 
            file['title'], file['artist'])

        return file
