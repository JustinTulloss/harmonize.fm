# vim:expandtab:smarttab
import logging
from pylons import config
from pylons import cache, request, session
from pylons.controllers.util import abort
import cPickle as pickle
from datetime import datetime
from sqlalchemy import Column, MetaData, Table, ForeignKey, types, sql
from sqlalchemy.sql import func, select, join, or_, and_
from sqlalchemy.orm import mapper, relation, column_property, deferred, join
from sqlalchemy.orm import scoped_session, sessionmaker

from pylons.decorators.cache import beaker_cache
from decorator import decorator
import time


log = logging.getLogger(__name__)

Session = scoped_session(sessionmaker(
                        autoflush = True,
                        autocommit = False, 
                        bind = config['pylons.g'].sa_engine))

metadata = MetaData(bind=Session.bind)

# Reflect all the tables out of the database
files_table = Table("files", metadata, autoload=True)
owners_table = Table("owners", metadata, autoload=True)
songstats_table = Table("songstats", metadata, autoload=True)
songs_table = Table("songs", metadata, autoload=True)
albums_table = Table("albums", metadata,autoload=True)
artists_table = Table("artists", metadata, autoload=True)
playlists_table = Table("playlists", metadata, autoload=True)
playlistsongs_table= Table("playlistsongs", metadata, autoload=True)
blockedfriends_table = Table("blockedfriends", metadata, autoload=True)
blockedartists_table = Table("blockedartists", metadata, autoload=True)
blog_table = Table("blog", metadata, autoload=True)
spotlights_table = Table('spotlights', metadata, autoload=True)
spotlight_comments_table = Table('spotlight_comments', metadata, autoload=True)
puids_table = Table('puids', metadata, autoload=True)
songowners_table = Table('songowners', metadata, autoload=True)
whitelists_table = Table('whitelists', metadata, autoload=True)
notifications_table = Table('notifications', metadata, autoload=True)
removedowners_table = Table('removedowners', metadata, autoload=True)

"""
Classes that represent above tables. You can add abstractions here
(like constructors) that make the tables even easier to work with
"""


class Owner(object):
    def __init__(self, user=None, file=None):
        self.file = file
        self.user = user

class File(object):
    def __init__(self, sha=None, song=None, bitrate=None, size=None):
        self.sha = sha
        self.bitrate = bitrate
        self.size = size
        self.song = song

class Song(object): 
    def __init__(self, title=None, albumid=None, mbid=None, 
            length=0, tracknumber=None, sha=None, size=None, bitrate=None,
            pristine=None):
        self.title = title
        self.albumid = albumid
        self.mbid = mbid
        self.length = length
        self.tracknumber = tracknumber
        self.sha = sha
        self.size = size
        self.bitrate = bitrate
        self.pristine = pristine
    
class Album(object):
    def __init__(self, title=None, mbid=None,
            asin=None, mp3_asin=None, year=None, totaltracks=0,
            smallart=None, medart=None, largeart=None, swatch=None):
        self.title = title
        self.mbid = mbid
        self.asin = asin
        self.mp3_asin = mp3_asin
        self.year = year
        self.totaltracks = totaltracks

        # Album art URLs
        self.smallart = smallart
        self.medart = medart
        self.largeart = largeart
        self.swatch = swatch

class Artist(object):
    def __init__(self, name=None, mbid=None, sort=None):
        self.name = name
        self.mbid = mbid
        if sort:
            self.sort = sort
        else:
            self.sort = name

class Playlist(object):
    def __init__(self, name, ownerid):
        """
        Constructs a new playlist.
        """
        self.name = name
        self.ownerid = ownerid

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
    def __init__(self, uid, albumid, comment=None, active=True, playlistid=None):
        self.uid = uid
        self.albumid = albumid
        self.comment = comment[:255]
        self.timestamp = datetime.now()
        self.active = active
        self.playlistid = playlistid
        if active:
            self._unactivate_lru()

    def get_title(self):
        if self.albumid:
            qry = Session.query(Album).get(self.albumid)
            return qry.title
        elif self.playlistid:
            qry = Session.query(Playlist).get(self.playlistid)
            return qry.name
    title = property(get_title)

    def get_author(self):
        if self.albumid:
            return self.album.artist.name
        elif self.playlistid:
            user = Session.query(User).get(self.uid)
            return user.name
    author = property(get_author)

    def _unactivate_lru(self):
        if Session.query(func.count(Spotlight.id)).filter(sql.and_(
                Spotlight.uid==self.uid, Spotlight.active==True)).one()[0] >= 3:
            lru = Session.query(Spotlight).\
                    filter(sql.and_(
                            Spotlight.uid==self.uid, 
                            Spotlight.active==True))\
                    .order_by(Spotlight.timestamp)[0]
            lru.active = False

class SpotlightComment(object):
    def __init__(self, uid, spotlightid, comment):
        self.uid = uid
        self.spotlightid = spotlightid
        self.comment = comment
        self.timestamp = datetime.now()

class SongStat(object):
    def __init__(self, user = None, song = None):
        self.user = user
        self.song = song
        self.playcount = 0
        self.lastrecommended = datetime.now() #we don't currently use this

class Puid(object):
    def __init__(self, puid = None, song = None):
        self.song = song
        self.puid = puid

class SongOwner(object):
    def __init__(self, song=None, user=None):
        self.song = song
        self.user = user

class Whitelist(object):
    def __init__(self, fbid=None, registered=False):
        self.fbid = fbid
        self.registered = registered

class Notification(object):
    def __init__(self, email, type, data = None):
        self.email = email
        self.type = type
        self.data = pickle.dumps(data)

class RemovedOwner(object):
    def __init__(self, song=None, user=None):
        self.song = song
        self.user = user



"""
The mappers. This is where the cool stuff happens, like adding fields to the
classes that represent complicated queries
"""
from user import User

mapper(File, files_table, properties={
    'owners': relation(Owner, backref='file', cascade='all, delete-orphan')
})

mapper(Owner, owners_table, properties={
    'user': relation(User)
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
})

mapper(Song, songs_table, properties = {
    'files': relation(File, backref='song', cascade='all, delete-orphan'),
    'owners': relation(SongOwner, backref='song', cascade='all, delete-orphan'),
    'stats': relation(SongStat, backref='song', lazy=True, cascade='all, delete-orphan'),
    'puids': relation(Puid, backref='song', lazy=True, cascade='all, delete-orphan'),
    'artist': relation(Artist, 
        lazy = True,
        foreign_keys = [songs_table.c.artistid],
        primaryjoin = artists_table.c.id == songs_table.c.artistid,
    )
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
        lazy = True,
        foreign_keys = [albums_table.c.artistid],
        primaryjoin = artists_table.c.id == albums_table.c.artistid
    )
})

mapper(PlaylistSong, playlistsongs_table, properties={
    'song' : relation(Song, backref='playlistsongs')})

mapper(Playlist, playlists_table, properties={
    'owner': relation(User),
    'songs': relation(PlaylistSong, backref='playlist', 
                        cascade='all, delete-orphan'),
    'songcount': column_property(
            select(
                [func.count(playlistsongs_table.c.id)],
                playlistsongs_table.c.playlistid == playlists_table.c.id
            ).label('songcount')
        ),
    'length': column_property(
            select(
                [func.sum(songs_table.c.length)],
                and_(playlistsongs_table.c.playlistid == playlists_table.c.id,
                    songs_table.c.id == playlistsongs_table.c.songid)
            ).label('length')
        )
})

mapper(BlogEntry, blog_table)

mapper(Spotlight, spotlights_table, properties={
    'album': relation(Album, lazy=False),
    'user' : relation(User, lazy=False, backref='spotlights'),
    'playlist' : relation(Playlist, foreign_keys = [spotlights_table.c.playlistid], primaryjoin = playlists_table.c.id == spotlights_table.c.playlistid),
})

mapper(SpotlightComment, spotlight_comments_table, properties={
    'user' : relation(User),
    'spotlight' : relation(Spotlight, backref='friend_comments')
})

mapper(SongStat, songstats_table, properties={
    'user': relation(User, backref='songstats')
})

mapper(Puid, puids_table)

mapper(SongOwner, songowners_table, properties={
    'user': relation(User, lazy=True, backref='owners')
})

mapper(RemovedOwner, removedowners_table, properties={
    'user': relation(User),
    'song': relation(Song)
})

mapper(Whitelist, whitelists_table)

mapper(Notification, notifications_table)

#additional mappings for declarative classes
User._nowplaying = relation(Song,
    primaryjoin=User.__table__.c.nowplayingid==songs_table.c.id,
    foreign_keys = [User.__table__.c.nowplayingid]
)

