from pylons import config
from sqlalchemy import Column, MetaData, Table, types
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
    Column("title", types.String),
    Column("artist", types.String),
    Column("album", types.String),
    Column("genre", types.String),
    Column("tracknumber", types.Integer),
    Column("total_tracks", types.Integer),
)

class Music(object):
    pass

mapper(Music, music_table)
