from pylons import config
from sqlalchemy import Column, MetaData, Table, ForeignKey, types, sql
from sqlalchemy.sql import func, select
from sqlalchemy.orm import mapper, relation, column_property
from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session(sessionmaker(
                        autoflush=True,
                        transactional=True, 
                        bind=config['pylons.g'].sa_engine))

metadata = MetaData()

files_table = Table("files", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("sha", types.String, index=True, unique=True),
    Column("songid", types.Integer, ForeignKey("songs.id"),index=True),
    Column("inuse", types.Boolean, nullable=False, default=False)
)

owners_table = Table("owners", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("fbid", types.Integer, index=True),
    Column("fileid", types.Integer, ForeignKey("files.id"), index=True),
    Column("recommendations", types.Integer, nullable=False),
    Column("playcount", types.Integer, nullable=False)
)

songs_table = Table("songs", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("mbid", types.String, index=True, unique=True),
    Column("title", types.String, index=True),
    Column("length", types.Integer, nullable=False),
    Column("albumid", types.Integer, ForeignKey("albums.id"), index=True),
    Column("tracknumber", types.Integer),
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

playlists_table = Table("playlists", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("owner", types.Integer, ForeignKey("owners.id"), index=True)
)

playlistsongs_table= Table("playlistsongs", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("playlistid", types.Integer, ForeignKey("playlists.id"), index=True),
    Column("songid", types.Integer, ForeignKey("songs.id"))
)

artists = select([albums_table.c.id, albums_table.c.artist, albums_table.c.mbartistid], distinct=True).alias('artists')

tagdata = sql.join(songs_table, albums_table,
    songs_table.c.albumid == albums_table.c.id).join(files_table,
    files_table.c.songid == songs_table.c.id)

"""
Classes that represent above tables. You can add abstractions here
(like constructors) that make the tables even easier to work with
"""

class Owner(object):
    pass

class File(object):
    pass

class Song(object): 
    pass
    
class Album(object):
    pass

class Artist(object):
    pass

class Playlist(object):
    pass
        
class TagData(object):
    pass


"""
The mappers. This is where the cool stuff happens, like adding fields to the
classes that represent complicated queries
"""
mapper(File, files_table, properties={
    'song': relation(Song, backref='files')
})
mapper(Owner, owners_table, properties={
    'file': relation(File, backref='owners')
})
mapper(Song, songs_table)
mapper(Album, albums_table, properties={  
    'songs':relation(Song, backref='album'),
    'albumid': albums_table.c.id,
    'album':albums_table.c.title,
    'albumlength': column_property(
        select([func.sum(songs_table.c.length).label('albumlength')],
            songs_table.c.albumid == albums_table.c.id, correlate=False
        ).as_scalar().label('albumlength')
    )
})
mapper(Artist, artists, properties={
    'songs':relation(Song)
})
mapper(Playlist, playlistsongs_table, properties={
    'songs':relation(Song),
})
mapper(TagData, tagdata, properties={
    'id': songs_table.c.id,
    'fileid': files_table.c.id,
    'songid': songs_table.c.id,
    'album': albums_table.c.title,
    'albumid': albums_table.c.id,
    'owners': relation(Owner)
})
