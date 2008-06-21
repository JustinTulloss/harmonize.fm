# vim:expandtab:smarttab
import logging
from pylons import config
from datetime import datetime
from sqlalchemy import Column, MetaData, Table, ForeignKey, types, sql
from sqlalchemy.sql import func, select, join, or_, and_
from sqlalchemy.orm import mapper, relation, column_property, deferred, join
from sqlalchemy.orm import scoped_session, sessionmaker

from facebook.wsgi import facebook
from facebook import FacebookError

from pylons import cache

from time import sleep
from decorator import decorator

log = logging.getLogger(__name__)

Session = scoped_session(sessionmaker(
                        autoflush = True,
                        autocommit = False, 
                        bind = config['pylons.g'].sa_engine))

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
spotlights_table = Table('spotlights', metadata, autoload=True)
spotlight_comments_table = Table('spotlight_comments', metadata, autoload=True)
puids_table = Table('puids', metadata, autoload=True)
songowners_table = Table('songowners', metadata, autoload=True)

"""
Classes that represent above tables. You can add abstractions here
(like constructors) that make the tables even easier to work with
"""

class User(object):
    fbid = None
    fbinfo = None
    listeningto = None
    fbcache = None
    def __init__(self, fbid=None):
        self.fbid = fbid

    @decorator
    def fbattr (func, self, *args, **kwargs):
        if not self.fbcache:
            self._create_cache()
        if not self.fbcache.has_key(self.fbid):
            self.fbcache[self.fbid] = self._get_fbinfo()
        self.fbinfo = self.fbcache.get_value(
            key = self.fbid,
            expiretime = 24*60*60*60, # 24 hours
            createfunc = self._get_fbinfo
        )
        return func(self, *args, **kwargs)

    def _create_cache(self):
        self.fbcache = cache.get_cache('fbprofile')

    def _get_fbinfo(self):
        info = None
        while not info:
            try:
                fields = [
                    'name',
                    'first_name',
                    'pic',
                    'pic_big',
                    'music',
                    'sex'
                ]
                info = facebook.users.getInfo(self.fbid, fields=fields)[0]
            except FacebookError, e:
                log.warn("Could not connect to facebook, retrying: %s", e)
                sleep(.1)
        return info

    @fbattr
    def get_name(self):
        return self.fbinfo['name']
    name = property(get_name)

    @fbattr
    def get_firstname(self):
        return self.fbinfo['first_name']
    firstname = property(get_firstname)

    @fbattr
    def get_picture(self):
        return self.fbinfo['pic']
    picture = property(get_picture)

    @fbattr
    def get_bigpicture(self):
        return self.fbinfo['pic_big']
    bigpicture = property(get_bigpicture)

    @fbattr
    def get_musictastes(self):
        return self.fbinfo['music']
    musictastes = property(get_musictastes)

    @fbattr
    def get_sex(self):
        return self.fbinfo['sex']
    sex = property(get_sex)

    def are_friends(self, user):
        return user in self.friends

    def get_friends(self):
        if self._friendids == None:
            self._friendids = facebook.friends.getAppUsers()
            allfriends = or_()
            for id in self._friendids:
                allfriends.append(User.fbid == id)
            self._friends == Session.query(User).filter(allfriends).all()
        return self._friends
    friends = property(get_friends)
    
    def get_nowplaying(self):
        return self._nowplaying

    def set_nowplaying(self, song):
        self._nowplayingid = song.id
        stats = Session.query(SongStat).\
            filter(SongStat.song == song).\
            filter(SongStat.user == self).first()
        if not stats:
            stats = SongStat(user = self, song = song)

        stats.playcount = stats.playcount + 1
        stats.lastplayed = datetime.now()
        Session.add(stats)
    nowplaying = property(get_nowplaying, set_nowplaying)

    def get_from_fbid(fbid, create=False):
        """
        Fetches a user by facebook id. Set create to true to create it if it
        doesn't exist
        """
        pass

    def get_top_10_artists(self):
        totalcount = Session.query(Artist.id, Artist.name,
            func.sum(SongStat.playcount).label('totalcount')
        )
        totalcount = totalcount.join([Artist.songs, SongStat])
        totalcount = totalcount.filter(SongStat.uid == self.id)
        totalcount = totalcount.group_by(Artist.id)
        totalcount = totalcount.order_by(sql.desc('totalcount')).limit(10)
        return totalcount.all()
    top_10_artists = property(get_top_10_artists)

    def _build_song_query(self):
        from masterapp.config.schema import dbfields
        query = Session.query(SongOwner.uid.label('Friend_id'), *dbfields['song'])
        query = query.join(Song.album).reset_joinpoint()
        query = query.join(Song.artist).reset_joinpoint()
        query = query.join(Song.files, SongOwner).filter(SongOwner.uid == self.id)
        return query
        
    def get_song_query(self):
        query = self._build_song_query()
        query = query.group_by(Song)
        return query
    song_query = property(get_song_query)
    
    def get_song_count(self):
        query = self._build_song_query()
        query = len(query.all())
        return query
    song_count = property(get_song_count)

    def get_album_query(self):
        from masterapp.config.schema import dbfields

        # Number of songs available on this album subquery
        havesongs = Session.query(Album.id.label('albumid'),
            func.count(Song.id).label('Album_havesongs'),
            func.sum(Song.length).label('Album_length')
        ).join(Album.songs, SongOwner).filter(SongOwner.uid == self.id)
        havesongs = havesongs.group_by(Album.id).subquery()

        query = Session.query(SongOwner.uid.label('Friend_id'), havesongs.c.Album_havesongs,
            havesongs.c.Album_length,
            *dbfields['album'])
        joined = join(Album, havesongs, Album.id == havesongs.c.albumid)
        query = query.select_from(joined)
        query = query.join(Album.artist).reset_joinpoint()
        query = query.join(Album.songs, SongOwner).filter(SongOwner.uid == self.id)
        query = query.group_by(Album)
        return query
    album_query = property(get_album_query)

    def get_artist_query(self):
        from masterapp.config.schema import dbfields

        # Number of songs by this artist subquery
        numsongs = Session.query(Artist.id.label('artistid'),
            func.count(Song.id).label('Artist_availsongs')
        ).join(Artist.songs, SongOwner).filter(SongOwner.uid == self.id)
        numsongs = numsongs.group_by(Artist.id).subquery()
        
        # Number of albums by this artist subquery
        albumquery = self._build_song_query().group_by(Song.albumid).subquery()
        numalbums = Session.query(albumquery.c.Song_artistid.label('artistid'),
            func.count(albumquery.c.Song_albumid).label('Artist_numalbums')
        ).select_from(albumquery).group_by(albumquery.c.Song_artistid).subquery()

        # Build the main query
        query = Session.query(SongOwner.uid.label('Friend_id'), numsongs.c.Artist_availsongs,
            numalbums.c.Artist_numalbums,
            *dbfields['artist'])
        joined = join(Artist, numsongs, Artist.id == numsongs.c.artistid)
        #joined2 = join(Artist, numalbums, Artist.id == numalbums.c.artistid)
        query = query.select_from(joined)
        query = query.join((numalbums, numalbums.c.artistid == Artist.id)).reset_joinpoint()
        query = query.join(Artist.albums, Song, SongOwner)
        query = query.filter(SongOwner.uid == self.id)
        query = query.group_by(Artist)
        return query
    artist_query = property(get_artist_query)

    def get_album_by_id(self, id):
        qry = self.album_query
        qry = qry.filter(Album.id == id)
        return qry.first()

    def get_active_spotlights(self):
        return Session.query(Spotlight).filter(sql.and_(\
                Spotlight.uid==self.id, Spotlight.active==True)).\
                order_by(sql.desc(Spotlight.timestamp))
        
            

class Owner(object):
    def __init__(self, user=None, file=None):
        self.file = file
        self.user = user

class File(object):
    def __init__(self, sha=None, songid=None):
        self.sha = sha
        self.songid = songid

class Song(object): 
    def __init__(self, title=None, albumid=None, mbid=None, 
            length=0, tracknumber=None, sha=None, size=None, bitrate=None):
        self.title = title
        self.albumid = albumid
        self.mbid = mbid
        self.length = length
        self.tracknumber = tracknumber
        self.sha = sha
        self.size = size
        self.bitrate = bitrate
        self.pristine = False
    
class Album(object):
    def __init__(self, title=None, mbid=None,
            asin=None, year=None, totaltracks=0,
            smallart=None, medart=None, largeart=None, swatch=None):
        self.title = title
        self.mbid = mbid
        self.asin = asin
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
    def __init__(self, uid, albumid, comment=None, active=True):
        self.uid = uid
        self.albumid = albumid
        self.comment = comment[:255]
        self.timestamp = datetime.now()
        self.active = active
        if active:
            self._unactivate_lru()

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

"""
The mappers. This is where the cool stuff happens, like adding fields to the
classes that represent complicated queries
"""
mapper(User, users_table, allow_column_override = True, properties = {
    '_nowplayingid': users_table.c.nowplayingid,
    '_nowplaying': relation(Song,
        primaryjoin=users_table.c.nowplayingid==songs_table.c.id,
        foreign_keys = [users_table.c.nowplayingid]
    ),
    'playlists': relation(Playlist, order_by=playlists_table.c.name)
})

mapper(File, files_table, properties={
    'owners': relation(Owner, backref='file', cascade='all, delete-orphan')
})

mapper(Owner, owners_table, properties={
    'user': relation(User),
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
        lazy = False,
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
        lazy = False,
        foreign_keys = [albums_table.c.artistid],
        primaryjoin = artists_table.c.id == albums_table.c.artistid
    )
})


mapper(PlaylistSong, playlistsongs_table, properties={
    'song' : relation(Song, backref='playlistsongs')})

mapper(Playlist, playlists_table, properties={
    'owner': relation(User),
    'songs': relation(PlaylistSong, backref='playlist', 
                        cascade='all, delete, delete-orphan'),
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
    'user' : relation(User, lazy=False, backref='spotlights')
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
