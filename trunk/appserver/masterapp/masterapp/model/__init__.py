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
    Column("length", types.String, nullable=False),
    Column("artist", types.String, nullable=False,index=True),
    Column("album_id", types.Integer, ForeignKey("albums.id"), index=True),
    Column("tracknumber", types.Integer),
    Column("recommendations", types.Integer, nullable=False),
    Column("owner_id", types.Integer, ForeignKey("friend.id"), index=True),
    Column("filename", types.String, nullable=False)
)

albums_table = Table("albums", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("album_title", types.String, index=True),
    Column("genre", types.String, index=True),
    Column("year", types.Integer, index=True),
    Column("totaltracks", types.Integer)
)

friend_table = Table("friend", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("name", types.String, index=True)
)

"""
Classes that represent above tables. You can add abstractions here
(like constructors) that make the tables even easier to work with
"""

class Songs(object): 
    def __init__(self, id, sha, title, artist, album_id, tracknumber, recommendations, owner_id, length):
        self.id = id
        self.sha = sha
        self.title = title
        self.length = length
        self.artist = artist
        self.album_id = album_id
        self.tracknumber = tracknumber
        self.recommendations = recommendations
        self.owner_id = owner_id
        self.filename = filename
    
class Albums(object):
    def __init__(self, id, album_title, genre, year, totaltracks):
        self.id = id
        self.album_title = album_title
        self.genre = genre
        self.year = year
        self.totaltracks = totaltracks
        
class Friends(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name    
        


mapper(Songs, songs_table)
mapper(Albums, albums_table, properties={  
        'songs':relation(Songs, backref='album')}
    )
mapper(Friends, friend_table, properties={
        'songs':relation(Songs, backref='friend')}
    )
    
