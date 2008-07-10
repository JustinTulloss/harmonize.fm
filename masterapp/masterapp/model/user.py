# Justin Tulloss
# 
# Putting user in its own file since it's huge

from pylons import cache, request, session, c
from pylons.templating import render
from decorator import decorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Table, sql
from sqlalchemy.sql import func, select, join, or_, and_
from sqlalchemy.orm import relation, join, synonym, aliased
from datetime import datetime
from . import (
    metadata,
    Session,
    songs_table,
    artists_table,
    playlists_table,
    spotlights_table,
    Artist,
    Album,
    Song,
    SongOwner,
    RemovedOwner,
    Playlist,
    Spotlight,
    SpotlightComment,
    BlogEntry,
    SongStat
)

from facebook.wsgi import facebook
from facebook import FacebookError

from masterapp.lib import fblogin
from operator import itemgetter
import time



Base = declarative_base(metadata=metadata)

class User(Base):
    """
    User class that abstracts away all information that deals with a user. It
    pulls that data from whereever it might live, and takes care of all caching
    and refetching of that data as well.

    At the risk of being inconsistent, this is also the first mapped class to
    take advantage of sqlalchemy's declarative extension, which is included with
    sqlalchemy .5
    """

    # Declarative constructs
    __table__ = Table("users", Base.metadata, autoload=True)
    
    __mapper_args__ = {'allow_column_override': True}

    _nowplayingid = __table__.c.nowplayingid
    playlists = relation(Playlist, order_by=playlists_table.c.name)

    fbid = None
    fbinfo = None
    listeningto = None
    fbcache = None
    fbfriendscache = None
    fballfriendscache = None
    present_mode = False

    def personal_cache(type=None, expiretime=None):
        def wrapper(func, self, *args, **kwargs):
            c = cache.get_cache('%s.%s' % 
                (func.__module__, func.__name__))
            funcargs = {
                'key': self.id,
                'createfunc': lambda: func(self, *args, **kwargs)
            }
            if type:
                funcargs['type'] = type
            if expiretime:
                funcargs['expiretime'] = expiretime
            return c.get_value(**funcargs)
        return decorator(wrapper)

    @decorator
    def fbaccess(func, self, *args, **kwargs):
        tries = 0
        while tries < 4:
            try:
                return func(self, *args, **kwargs)
            except FacebookError, e:
                if e.code == 102:
                    method = request.environ.get('HTTP_X_REQUESTED_WITH')
                    if method == 'XMLHttpRequest':
                        abort(401, 'Please re-login to facebook')
                    else: 
                        fblogin.login()
                else:
                    tries = tries + 1
                    time.sleep(.1)
    @decorator
    def fbfriends(func, self, *args, **kwargs):
        self._setup_fbfriends_cache()
        self._fbfriends = self.fbfriendscache.get_value(
            key = self.fbid,
            expiretime = self._fbexpiration,
            createfunc = self._get_fbfriends
        )
        try:
            return func(self, *args, **kwargs)
        except:
            # Try invalidating the cache
            self.fbfriendscache.remove_value(self.fbid)
            self._setup_fbfriends_cache()
            self._fbfriends = self.fbfriendscache.get_value(
                key = self.fbid,
                expiretime = self._fbexpiration,
                createfunc = self._get_fbfriends
            )
            return func(self, *args, **kwargs)

    @decorator
    def fballfriends(func, self, *args, **kwargs):
        self._setup_fballfriends_cache()
        self._fballfriends = self.fballfriendscache.get_value(
            key = self.fbid,
            expiretime = self._fbexpiration,
            createfunc = self._get_fballfriends
        )
        try:
            return func(self, *args, **kwargs)
        except:
            # Try invalidating the cache
            self.fballfriendscache.remove_value(self.fbid)
            self._setup_fballfriends_cache()
            self._fballfriends = self.fballfriendscache.get_value(
                key = self.fbid,
                expiretime = self._fbexpiration,
                createfunc = self._get_fballfriends
            )
            return func(self, *args, **kwargs)

    @decorator
    def fbattr (func, self, *args, **kwargs):
        self._setup_fbinfo_cache()
        self.fbinfo = self.fbcache.get_value(
            key = self.fbid,
            expiretime = self._fbexpiration,
            createfunc = self._get_fbinfo
        )
        try:
            return func(self, *args, **kwargs)
        except:
            self.fbcache.remove_value(self.fbid)
            self.fbcache[self.fbid] = self._get_fbinfo()
            self.fbinfo = self.fbcache.get_value(
                key = self.fbid,
                expiretime = self._fbexpiration,
                createfunc = self._get_fbinfo
            )
            return func(self, *args, **kwargs)
            

    def _get_caches(self):
        self.fbcache = cache.get_cache('fbprofile')
        self.fbfriendscache = cache.get_cache('fbfriends')
        self.fballfriendscache = cache.get_cache('fballfriends')
        # Facebook session_key_expires is not set for some reason
        #self._fbexpiration = facebook.session_key_expires - time.time()
        self._fbexpiration = 24*60*60 #24 hours

    def _setup_fbinfo_cache(self):
        if not self.fbcache:
            self._get_caches()
        if not self.fbcache.has_key(self.fbid):
            self.fbcache[self.fbid] = self._get_fbinfo()

    def _setup_fbfriends_cache(self):
        if not self.fbfriendscache:
            self._get_caches()
        if not self.fbfriendscache.has_key(self.fbid):
            self.fbfriendscache[self.fbid] = self._get_fbfriends()

    def _setup_fballfriends_cache(self):
        if not self.fballfriendscache:
            self._get_caches()
        if not self.fballfriendscache.has_key(self.fbid):
            self.fballfriendscache[self.fbid] = self._get_fballfriends()

    @fbaccess
    def _get_fbinfo(self):
        fields = [
            'name',
            'first_name',
            'pic',
            'pic_big',
            'pic_square',
            'music',
            'sex',
            'has_added_app'
        ]
        info = facebook.users.getInfo(self.fbid, fields=fields)[0]
        return info

    @fbaccess
    def _get_fbfriends(self):
        ids = facebook.friends.getAppUsers()
        if self.present_mode:
            ids.extend([1909354, 1908861])
        users = facebook.users.getInfo(ids)
        return sorted(users, key=itemgetter('name'))

    @fbaccess
    def _get_fballfriends(self):
        ids = facebook.friends.get()
        users = facebook.users.getInfo(ids)
        return sorted(users, key=itemgetter('name'))
    
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
    def get_swatch(self):
        return self.fbinfo['pic_square']
    swatch = property(get_swatch)

    @fbattr
    def get_musictastes(self):
        return self.fbinfo['music']
    musictastes = property(get_musictastes)

    @fbattr
    def get_sex(self):
        return self.fbinfo['sex']
    sex = property(get_sex)

    @fbattr
    def get_hasfbapp(self):
        return self.fbinfo['has_added_app']
    hasfbapp = property(get_hasfbapp)

    def are_friends(self, user):
        return user in self.friends

    @fbfriends
    def get_friends(self):
        return self._fbfriends
    friends = property(get_friends)

    @fballfriends
    def get_all_friends(self):
        return self._fballfriends
    allfriends = property(get_all_friends)

    def is_friends_with(self, someguy):
        """
        Tells you if a user is friends with another user.
        """
        if isinstance(someguy, User):
            if someguy.id == self.id:
                return True
            else:
                for friend in self.friends:
                    if friend['uid'] == someguy.fbid:
                        return True
                return False
        else:
            if someguy['uid'] == self.fbid:
                return True
            else:
                for friend in self.friends:
                    if friend['uid'] == someguy['uid']:
                        return True
                return False

    def is_fbfriends_with(self, fbid):
        """
        Tells you if a user is friends with another user on any network we know
        about
        """
        if fbid == self.fbid:
            return True
        else:
            for fbuser in self.allfriends:
                if fbuser['uid'] == fbid:
                    return True
            return False

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

    def get_url(self):
        return 'http://%s/player#/people/profile/%d' % (request.host, self.id)
    url = property(get_url)

    @personal_cache(expiretime=600, type='memory')
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

    @personal_cache(expiretime=600, type='memory')
    def get_feed_entries(self):
        max_count=20
        entries = Session.query(BlogEntry)[:max_count]
        myor = or_()
        for friend in self.friends:
            myor.append(User.fbid == friend['uid'])

        entries.extend(Session.query(Spotlight).join(User).filter(and_(
                myor, Spotlight.active==True))\
                [:max_count])

        CommentUser = aliased(User)
        SpotlightUser = aliased(User)
        commentor = or_()
        spotlightor = or_()
        for friend in self.friends:
            commentor.append(CommentUser.fbid == friend['uid'])
            spotlightor.append(SpotlightUser.fbid == friend['uid'])
            

        entries.extend(Session.query(SpotlightComment).\
                join(CommentUser,
                    (Spotlight, SpotlightComment.spotlight), 
                    (SpotlightUser, Spotlight.user)).\
                filter(and_(
                    SpotlightComment.uid!=session['userid'],
                    or_(Spotlight.uid==session['userid'],
                        and_(commentor, spotlightor)),
                    Spotlight.active == True))[:max_count])

        def sort_by_timestamp(x, y):
            if x.timestamp == None:
                if y.timestamp == None:
                    return 0
                return 1
            elif y.timestamp == None:
                return -1
            elif x.timestamp > y.timestamp:
                return -1
            elif x.timestamp == y.timestamp:
                return 0
            else:
                return 1

        entries.sort(sort_by_timestamp)
        return entries[:max_count]
    feed_entries = property(get_feed_entries)
        

    def _build_song_query(self):
        from masterapp.config.schema import dbfields
        query = Session.query(SongOwner.uid.label('Friend_id'), *dbfields['song'])
        query = query.join(Song.album).reset_joinpoint()
        query = query.join(Song.artist).reset_joinpoint()
        query = query.join(SongOwner).filter(SongOwner.uid == self.id)
        return query
        
    def get_song_query(self):
        query = self._build_song_query()
        return query.distinct()
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
    
    def get_playlist_query(self):
        from masterapp.config.schema import dbfields

        # Number of songs available on this album subquery
        havesongs = Session.query(Playlist.id.label('playlistid'),
            func.count(Song.id).label('Playlist_havesongs'),
            func.sum(Song.length).label('Playlist_length')
        )
        havesongs = havesongs.group_by(Playlist.id).subquery()

        query = Session.query(SongOwner.uid.label('Friend_id'), havesongs.c.Playlist_havesongs,
            havesongs.c.Playlist_length,
            *dbfields['playlist'])
        joined = join(Playlist, havesongs, Playlist.id == havesongs.c.playlistid)
        query = query.select_from(joined)
        # the following line is throwing all sorts of fits, not sure why
        # query = query.join(Song.artist).reset_joinpoint()
        query = query.group_by(Playlist)
        return query
    playlist_query = property(get_playlist_query)

    def get_artist_query(self):
        from masterapp.config.schema import dbfields

        # Build the main query
        query = Session.query(SongOwner.uid.label('Friend_id'),
            ArtistCounts.songcount.label('Artist_availsongs'), 
            ArtistCounts.albumcount.label('Artist_numalbums'),
            *dbfields['artist'])
        query = query.join(Artist.albums, Song, SongOwner, ArtistCounts)
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
    active_spotlights = property(get_active_spotlights)
        
    def get_playlist_by_id(self, id):
        qry = self.playlist_query
        qry = qry.filter(Playlist.id == id)
        return qry.first()            

    def add_song(self, song):
        """
        Adds a song to this user's collection. Keeps counts up to date.
        """

        # Add to collection
        owner = SongOwner(song = song, user = self)

        # Keep counts up to date
        new_album = False
        albumc = Session.query(AlbumCounts).get((song.albumid, self.id))
        if albumc:
            albumc.songcount += 1
        else:
            new_album = True
            albumc = AlbumCounts(user = self, album = song.album, songcount=1)

        artistc = Session.query(ArtistCounts).get((song.album.artistid, self.id))
        if artistc:
            artistc.songcount += 1
            if new_album:
                artistc.albumcount += 1
        else:
            artistc = ArtistCounts(
                user=self, artist=song.artist, songcount=1, albumcount=1)

        Session.add_all([owner, artistc, albumc])
        Session.commit()
        return owner

    def remove_song(self, songrow):
        """
        Removes a song from the users's collection and updates the counts.
        """
        # the passed song is a RowTuple, so we convert it so a Song object
        song =  Session.query(Song).get(songrow.Song_id)
        movedowner = RemovedOwner(
            song = song,
            user = self
        )
        Session.add(movedowner)

        owner = Session.query(SongOwner).\
            filter(SongOwner.song == song).\
            filter(SongOwner.user == self).first()
        Session.delete(owner) 

        albumc = Session.query(AlbumCounts).get((song.albumid, self.id))
        albumc.songcount -= 1
        remove_album = False
        if albumc.songcount == 0:
            remove_album = True

        artistc = Session.query(ArtistCounts).get((song.album.artistid, self.id))
        artistc.songcount -= 1
        if remove_album:
            artistc.albumcount -= 1
        Session.add(artistc)
        return True

    def update_profile(self):
        c.user = self
        fbml = render('facebook/profile.mako.fbml')
        facebook.profile.setFBML(fbml)

    @fbaccess
    def publish_spotlight(self, spot):
        title_t = """
        {actor} created 
        <fb:if-multiple-actors>Spotlights
        <fb:else>a Spotlight</fb:else>
        </fb:if-multiple-actors> on {album} at 
        <a href="http://harmonize.fm" target="_blank">harmonize.fm</a>
        """
        title_d = '{"album":"%s"}' % spot.title
        r = facebook.feed.publishTemplatizedAction(
            title_template=title_t, 
            title_data=title_d
        )
        return r

    def add_spotlight(self, spotlight):
        spotlight.user = self
        spotlight.unactivate_lru()
        Session.add(spotlight)
        self.publish_spotlight(spotlight)
        self.update_profile()


class ArtistCounts(Base):
    __table__ = Table('counts_artist', metadata, autoload=True)
    key = [__table__.c.artistid, __table__.c.userid]
    __mapper_args__ = {'primary_key': key}

    artist = relation(Artist)
    user = relation(User)

class AlbumCounts(Base):
    __table__ = Table('counts_album', metadata, autoload=True)

    key = [__table__.c.albumid, __table__.c.userid]
    __mapper_args__ = {'primary_key': key}
    album = relation(Album)
    user = relation(User)
