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
)

owners_table = Table("owners", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("uid", types.Integer, ForeignKey('users.id'), index=True),
    Column("fileid", types.Integer, ForeignKey("files.id"), index=True),
)

users_table = Table("users", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("fbid", types.Integer, index=True),
)

songstats_table = Table("songstats", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("songid", types.Integer, ForeignKey("songs.id"), index=True),
    Column("uid", types.Integer, ForeignKey('users.id'), index=True),
    Column("lastrecommended", types.DateTime, nullable=False),
    Column("playcount", types.Integer, nullable=False)
)

songs_table = Table("songs", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("mbid", types.String, index=True, unique=True),
    Column("title", types.String, index=True),
    Column("length", types.Integer, nullable=False),
    Column("albumid", types.Integer, ForeignKey("albums.id"), index=True),
    Column("tracknumber", types.Integer)
)

albums_table = Table("albums", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("mbid", types.String, index=True, unique=True),
    Column("artist", types.String, nullable=False,index=True),
    Column("artistsort", types.String),
    Column("mbartistid", types.String),
    Column("asin", types.String, unique=True),
    Column("title", types.String, index=True),
    Column("year", types.Integer, index=True),
    Column("totaltracks", types.Integer)
)

playlists_table = Table("playlists", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("ownerid", types.Integer, ForeignKey("users.id"), index=True),
    Column("name", types.String)
)

playlistsongs_table= Table("playlistsongs", metadata,
    Column("id", types.Integer, primary_key=True),
    Column("playlistid", types.Integer, ForeignKey("playlists.id"), index=True),
    Column("songindex", types.Integer),
    Column("songid", types.Integer, ForeignKey("songs.id"))
)

artists = select([albums_table.c.id,albums_table.c.artist, albums_table.c.artistsort, albums_table.c.mbartistid], group_by=albums_table.c.mbartistid, distinct=True).alias('artists')

"""
Classes that represent above tables. You can add abstractions here
(like constructors) that make the tables even easier to work with
"""

class User(object):
    def __init__(self, fbid):
        self.fbid = fbid

class Owner(object):
    def __init__(self, uid, fid):
        self.uid = uid
        self.fileid = fid

class File(object):
    def __init__(self, sha, songid):
        self.sha = sha
        self.songid = songid

class Song(object): 
    def __init__(self, title, albumid, mbid='', length=0, tracknum=None):
        self.title = title
        self.albumid = albumid
        self.mbid = mbid
        self.length = length
        self.tracknum =tracknum
    
class Album(object):
    def __init__(self, title, mbid=None, artist=None, artistsort=None,
        mbartistid=None, asin=None, year=None, totaltracks=0):
        self.title = title
        self.artist = None
        if artistsort != None:
            self.artistsort = artistsort
        else:
            self.artistsort = artist
        self.mbartistid = mbartistid
        self.asin = asin
        self.year = year
        self.totaltracks = totaltracks

class Artist(object):
    pass

class Playlist(object):
    def __init__(self, name, ownerid, *songs):
        """
        Constructs a new playlist.

        *songs should really be a list of PlaylistSong
        """
        self.name = name
        self.ownerid = ownerid
        Session.save(self)
        Session.commit()

        for song in songs:
            song.playlistid = self.id
            self.songs.append(song)

class PlaylistSong(Song):
    def __init__(self, playlistid, songindex, songid):
        self.playlistid = playlistid
        self.songindex = songindex
        self.songid = songid
"""
The mappers. This is where the cool stuff happens, like adding fields to the
classes that represent complicated queries
"""
mapper(User, users_table)
mapper(File, files_table, properties={
    'song': relation(Song, backref='files')
})
mapper(Owner, owners_table, properties={
    'file': relation(File, backref='owners'),
    'user': relation(User)
})
mapper(Song, songs_table)
mapper(Album, albums_table, properties={  
    'songs':relation(Song, backref='album'),
    'albumid': albums_table.c.id,
    'album':albums_table.c.title,
    'albumlength': column_property(
        select([func.sum(songs_table.c.length).label('albumlength')],
            songs_table.c.albumid == albums_table.c.id,
            group_by=songs_table.c.albumid
        ).correlate(albums_table).label('albumlength')
    )
})
mapper(Artist, artists, properties={
    'songs':relation(Song)
})

mapper(PlaylistSong, playlistsongs_table, inherits=Song)

mapper(Playlist, playlists_table, properties={
    'playlistid': playlists_table.c.id,
    'owner':relation(User),
    'songs':relation(PlaylistSong, backref='playlist')
})
