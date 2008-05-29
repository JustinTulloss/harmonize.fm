from pylons import config
from datetime import datetime
from sqlalchemy import Column, MetaData, Table, ForeignKey, types, sql
from sqlalchemy.sql import func, select
from sqlalchemy.orm import mapper, relation, column_property
from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session(sessionmaker(
                        autoflush=True,
                        transactional=True, 
                        bind=config['pylons.g'].sa_engine))

metadata = MetaData(bind=Session.bind)

# Reflect all the tables out of the database
files_table = Table("files", metadata, autoload=True)
owners_table = Table("owners", metadata, autoload=True)
users_table = Table("users", metadata, autoload=True)
songstats_table = Table("songstats", metadata, autoload=True)
songs_table = Table("songs", metadata, autoload=True)
albums_table = Table("albums", metadata,autoload=True)
artists_table = Table("artists", metadata, autoload=True)
playlists_table = Table("playlists", metadata, autoload=True)
playlistsongs_table= Table("playlistsongs", metadata, autoload=True)
blockedfriends_table = Table("blockedfriends", metadata, autoload=True)
blockedartists_table = Table("blockedartists", metadata, autoload=True)
blog_table = Table("blog", metadata, autoload=True)
spotlight_table = Table('spotlights', metadata, autoload=True)

"""
Classes that represent above tables. You can add abstractions here
(like constructors) that make the tables even easier to work with
"""

class User(object):
    def __init__(self, fbid=None):
        self.fbid = fbid

class Owner(object):
    def __init__(self, uid=None, fid=None):
        self.uid = uid
        self.fileid = fid

class File(object):
    def __init__(self, sha=None, songid=None):
        self.sha = sha
        self.songid = songid

class Song(object): 
    def __init__(self, title=None, albumid=None, mbid=None, 
            length=0, tracknumber=None):
        self.title = title
        self.albumid = albumid
        self.mbid = mbid
        self.length = length
        self.tracknumber =tracknumber
    
class Album(object):
    def __init__(self, title=None, mbid=None,
            asin=None, year=None, totaltracks=0):
        self.title = title
        self.asin = asin
        self.year = year
        self.totaltracks = totaltracks

class Artist(object):
    def __init__(self, name=None, mbid=None, sort=None):
        self.name = name
        self.mbid = mbid
        if sort:
            self.sort = sort
        else:
            self.sort = name

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

class BlogEntry(object):
    def __init__(self, title=None, author=None, entry=None):
        self.title = title
        self.author = author
        self.entry = entry
        self.timestamp = datetime.now()

class Spotlight(object):
	def __init__(self, uid, albumid, comment=None):
		self.uid = uid
		self.albumid = albumid
		self.comment = comment
		self.timestamp = datetime.now()

"""
The mappers. This is where the cool stuff happens, like adding fields to the
classes that represent complicated queries
"""
mapper(User, users_table)

mapper(File, files_table, properties={
    'owners': relation(Owner, backref='file', cascade='all, delete-orphan')
})

mapper(Owner, owners_table, properties={
    'user': relation(User, backref='owners')
})

mapper(Artist, artists_table, properties={
    'songs': relation(
        Song, 
        lazy = True, 
        cascade = 'all, delete-orphan',
        foreign_keys = [songs_table.c.artistid],
        primaryjoin = artists_table.c.id == songs_table.c.artistid,
    ),
    'albums': relation(
        Album, 
        lazy = True, 
        foreign_keys = [albums_table.c.artistid],
        primaryjoin = artists_table.c.id == albums_table.c.artistid,
    ),
    'availsongs': column_property(
        select([func.count(songs_table.c.id).label('availsongs')],
            songs_table.c.artistid == artists_table.c.id,
            group_by = artists_table.c.id,
        ).correlate(artists_table).label('availsongs')
    ),
    'numalbums': column_property(
        select([func.count(albums_table.c.artistid).label('numalbums')],
            albums_table.c.artistid == artists_table.c.id,
            group_by = artists_table.c.id,
            distinct = True).correlate(artists_table).label('numalbums'),
        deferred = True
    ),
})

mapper(Song, songs_table, properties = {
    'files': relation(File, backref='song', cascade='all, delete-orphan'),
    'artist':relation(Artist, 
        lazy = False,
        foreign_keys = [songs_table.c.artistid],
        primaryjoin = artists_table.c.id == songs_table.c.artistid,
    ),
})


mapper(Album, albums_table, allow_column_override = True, 
    exclude_properties = ['artist', 'mbartistid', 'artistsort'],
    properties={  
    'songs': relation(Song, 
        backref = 'album', 
        lazy = True,
        cascade = 'all, delete-orphan',
        order_by = songs_table.c.tracknumber
    ),
    'artist': relation(Artist,
        lazy = False,
        foreign_keys = [albums_table.c.artistid],
        primaryjoin = artists_table.c.id == albums_table.c.artistid
    ),
    'havesongs': column_property(
        select([func.count(songs_table.c.id).label('havesongs')],
            songs_table.c.albumid == albums_table.c.id,
            group_by=songs_table.c.albumid
        ).correlate(albums_table).label('havesongs')
    ),
    'length': column_property(
        select([func.sum(songs_table.c.length).label('length')],
            songs_table.c.albumid == albums_table.c.id,
            group_by=songs_table.c.albumid 
        ).correlate(albums_table).label('length')
    )
})


mapper(PlaylistSong, playlistsongs_table, inherits=Song)

mapper(Playlist, playlists_table, properties={
    'playlistid': playlists_table.c.id,
    'owner': relation(User),
    'songs': relation(PlaylistSong, backref='playlist')
})

mapper(BlogEntry, blog_table)

mapper(Spotlight, spotlight_table)
