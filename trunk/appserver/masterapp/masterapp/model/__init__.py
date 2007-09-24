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
music_table = Table("music", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("sha", types.String, index=True, unique=True),
    Column("title", types.String, index=True),
    Column("artist", types.String, index=True),
    Column("album", types.String, index=True),
    Column("genre", types.String),
    Column("tracknumber", types.Integer),
    Column("totaltracks", types.Integer),
)

ownership_table = Table("ownership", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("uid", types.Integer, index=True),
    Column("mid", types.Integer, ForeignKey("music.id"), index=True)
)

"""
Classes that represent above tables. You can add abstractions here
(like constructors) that make the tables even easier to work with
"""
class Music(object):
    pass

class Ownership(object):
    pass

mapper(Music, music_table)
mapper(Ownership, ownership_table)
