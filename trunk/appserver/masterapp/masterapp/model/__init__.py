from pylons import config
from sqlalchemy import Column, MetaData, Table, ForeignKey, types, sql
from sqlalchemy.orm import mapper, relation
from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session(sessionmaker(
                        autoflush=True,
                        transactional=True, 
                        bind=config['pylons.g'].sa_engine))

metadata = MetaData()

#music table defn
songs_table = Table("songs", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("mbid", types.String, index=True, unique=True),
    Column("title", types.String, index=True),
    Column("length", types.Integer, nullable=False),
    Column("albumid", types.Integer, ForeignKey("albums.id"), index=True),
    Column("tracknumber", types.Integer),
)

files_table = Table("files", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("sha", types.String, index=True, unique=True),
    Column("songid", types.Integer, ForeignKey("songs.id"),index=True),
    Column("inuse", types.Boolean, nullable=False, default=False)
)

albums_table = Table("albums", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("mbid", types.String, index=True, unique=True),
    Column("artist", types.String, nullable=False,index=True),
    Column("artistsort", types.String),
    Column("mbartistid", types.String, unique=True),
    Column("asin", types.String, unique=True),
    Column("title", types.String, index=True),
    Column("year", types.Integer, index=True),
    Column("totaltracks", types.Integer)
)

owners_table = Table("owners", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("fbid", types.Integer, index=True),
    Column("fileid", types.Integer, ForeignKey("files.id"), index=True),
    Column("recommendations", types.Integer, nullable=False),
    Column("playcount", types.Integer, nullable=False)
)

tagdata = sql.join(songs_table, albums_table,
    songs_table.c.albumid == albums_table.c.id)

"""
Classes that represent above tables. You can add abstractions here
(like constructors) that make the tables even easier to work with
"""

class Song(object): 
    pass
    
class File(object):
    pass

class Album(object):
    pass
        
class Owner(object):
    pass

class TagData(object):
    pass


mapper(Song, songs_table)
mapper(File, files_table, properties={
    'song': relation(Song, backref='files')}
)
mapper(Album, albums_table, properties={  
    'songs':relation(Song, backref='album')}
)
mapper(Owner, owners_table, properties={
    'file': relation(File, backref='owners')}
)
mapper(TagData, tagdata, properties={
    'id': songs_table.c.id,
    'songid': songs_table.c.id,
    'album': albums_table.c.title,
    'albumid': albums_table.c.id
})
