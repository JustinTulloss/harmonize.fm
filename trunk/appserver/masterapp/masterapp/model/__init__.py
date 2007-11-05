from pylons import config
from sqlalchemy import Column, MetaData, Table, ForeignKey, types
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
    Column("sha", types.String, index=True, unique=True),
    Column("title", types.String, index=True),
    Column("artist", types.String, index=True),
    Column("album_id", types.Integer, ForeignKey("albums.id"), index=True),
    Column("tracknumber", types.Integer),
    Column("recommendations", types.Integer)
)

albums_table = Table("albums", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("album_title", types.String, index=True),
    Column("genre", types.String, index=True),
    Column("year", types.Integer, index=True),
    Column("totaltracks", types.Integer)
)

ownership_table = Table("ownership", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("uid", types.Integer, index=True),
    Column("mid", types.Integer, ForeignKey("songs.id"), index=True)
)

"""
Classes that represent above tables. You can add abstractions here
(like constructors) that make the tables even easier to work with
"""

class Songs(object):
    pass
class Albums(object):
    pass
class Ownership(object):
    pass

mapper(Songs, songs_table)
mapper(Albums, albums_table, properties={  
        'songs':relation(Songs, backref='album')}
    )
mapper(Ownership, ownership_table, properties={  
        'ownedsongs':relation(Songs, backref='owner')}
    )
