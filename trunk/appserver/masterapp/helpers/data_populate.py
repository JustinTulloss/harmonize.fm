#
#
# This is supposed to automatically populate a database with data from a folder.
#

from sqlalchemy import create_engine, Column, MetaData, Table, types
from sqlalchemy.orm import mapper, relation
from sqlalchemy.orm import scoped_session, sessionmaker

import os
import sys
import shutil

sys.path.append("../../../libs.py")
from mutagen.easyid3 import EasyID3


MUSIC_FOLDER = "/mnt/data/Users/justin/Music/Radiohead"

DATABASE = "sqlite:///../music.db"

engine = create_engine(DATABASE)

Session = scoped_session(sessionmaker(
                        autoflush=True,
                        transactional=True, 
                        bind=engine))

metadata = MetaData()

songs = Table("songs", metadata, autoload=True, autoload_with=engine)
albums = Table("albums", metadata, autoload=True, autoload_with=engine)
friends = Table("friend", metadata, autoload=True, autoload_with=engine)

class Songs(object):
    pass

class Albums(object):
    pass
    
class Friends(object):
    pass

mapper(Songs, songs)
mapper(Albums, albums)
mapper(Friends, friends)

here = os.getcwd()

def iter_tags(dbobj, tags):
    for key in tags.keys():
        try:
            setattr(dbobj, key, tags[key])
        except:
            pass #This just means the database doesn't store that 
    Session.save(dbobj)


def parse_songs(arg, dirname, fnames):
    os.chdir(dirname)
    for file in fnames:
        try:
            tags = EasyID3(file)
            dbtags = {}
            for k in tags.keys():
                dbtags[k] = ','.join(tags[k])
                #print k
            qry = Session.query(Albums).filter(
                Albums.album ==dbtags["album"])
            album = qry.all()
            if len(album) == 0:
                newalbum = Albums()
                #newalbum.album_title = dbtags['album']
                #newalbum.year = dbtags['year']
                iter_tags(newalbum, dbtags)
                album_id = newalbum.id
            else:
                album_id = album[0].id

            newsong = Songs()
            newsong.album_id= album_id
            newsong.recommendations = 0
            newsong.owner_id = (album_id % 6) + 1
            newsong.length = "4:02"
            newsong.filename = file
            iter_tags(newsong, dbtags)
        except:
            print "Could not process %s" % file 
            
def add_friends():
    friends = ["Alex Mohr", "James Truty", "Justin Tulloss", "Paul Casperson", "Brian Smith", "Mike Phelan"]
    id = 1
    for friend in friends:
        newfriend = Friends()
        newfriend.id = id
        newfriend.name = friend        
        id += 1
        Session.save(newfriend)
    

os.path.walk(MUSIC_FOLDER, parse_songs, None)
#add_friends()

Session.commit()
