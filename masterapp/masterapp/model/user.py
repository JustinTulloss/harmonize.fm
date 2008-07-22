# Justin Tulloss
# 
# Putting user in its own file since it's huge

import logging
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
    SongStat,
    Recommendation
)

from facebook.wsgi import facebook
from facebook import FacebookError

from masterapp.lib import fblogin
from masterapp.lib.fbaccess import fbaccess
from operator import itemgetter, attrgetter
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
    _name = __table__.c.name
    playlists = relation(Playlist, order_by=playlists_table.c.name)

    fbid = None
    fbinfo = None
    listeningto = None
    fbcache = None
    fbfriendscache = None
    fballfriendscache = None
    present_mode = False

    def __init__(self, fbid, **kws):
        Base.__init__(self, **kws)
        self.fbid = fbid
        self.premium = False

    def personal_cache(type=None, expiretime=None, addsession = False):
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
            val = c.get_value(**funcargs)
            if addsession:
                if hasattr(val, '__iter__'):
                    for r in xrange(0, len(val)):
                        val[r] = Session.merge(val[r], dont_load=True)
                else:
                    val = Session.merge(val, dont_load=True)
            return val
        return decorator(wrapper)

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
            self._fbfriends = self.fbfriendscache.get_value(self.fbid,
                expiretime = self._fbexpiration,
                createfunc = self._get_fbfriends
            )
            return func(self, *args, **kwargs)

    @decorator
    def fballfriends(func, self, *args, **kwargs):
        self._setup_fballfriends_cache()
        self._fballfriends = self.fballfriendscache.get_value(self.fbid,
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

    def _setup_fbfriends_cache(self):
        if not self.fbfriendscache:
            self._get_caches()

    def _setup_fballfriends_cache(self):
        if not self.fballfriendscache:
            self._get_caches()

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
        olduid = facebook.uid
        oldsession = facebook.session_key
        if self.fbid != int(facebook.uid):
            facebook.uid = unicode(self.fbid)
            facebook.session_key = self.fbsession
            log.debug("Querying for wrong user's friends, trying to sub in their session")
        try:
            ids = facebook.friends.getAppUsers()
            if self.present_mode:
                ids.extend([1909354, 1908861])
            # I'm banking on caches in a big way here. I'm assuming that the vast
            # majority of additional facebook information will be cached per user,
            # so when we're actually accessing the attributes of these users 1 by 1,
            # it won't be too expensive.
            friendor = or_()
            for id in ids:
                friendor.append(User.fbid == id)
            users = Session.query(User).filter(friendor).order_by(User._name)
        finally:
            facebook.uid = olduid
            facebook.session_key = oldsession
        return users.all()

    @fbaccess
    def _get_fballfriends(self):
        ids = facebook.friends.get()
        users = facebook.users.getInfo(ids)
        return sorted(users, key=itemgetter('name'))
    
    @fbattr
    def get_name(self):
        if self._name != self.fbinfo['name']:
            self._name = self.fbinfo['name']
            Session.add(self)
            Session.commit()

        return self._name
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
        if self._fbfriends:
            for i in xrange(0, len(self._fbfriends)):
                self._fbfriends[i]= Session.merge(self._fbfriends[i], dont_load=True)
            return self._fbfriends
        else:
            return []
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
                    if friend.id == someguy.id:
                        return True
                return False
        else:
            if someguy['uid'] == self.fbid:
                return True
            else:
                for friend in self.friends:
                    if friend.fbid == someguy['uid']:
                        return True
                return False

    @personal_cache(expiretime=600, type='memory')
    def get_songcount(self):
        count = Session.query(func.sum(AlbumCounts.songcount).label('songs')).\
            filter(AlbumCounts.userid == self.id).first().songs
        if count:
            return int(count)
        else:
            return 0
    songcount = property(get_songcount)

    @personal_cache(expiretime=600, type='memory')
    def get_albumcount(self):
        return Session.query(func.count(AlbumCounts.albumid).label('albums')).\
            filter(AlbumCounts.userid == self.id).first().albums
    albumcount = property(get_albumcount)

        
    def get_nowplaying(self):
        return self._nowplaying

    def set_nowplaying(self, song):
        self._nowplayingid = song.id
        stats = Session.query(SongStat).\
            filter(SongStat.song == song).\
            filter(SongStat.user == self)
        
        if session.has_key('src'):
            stats = stats.filter(SongStat.source == session['src'])

        stats = stats.first()
        if not stats:
            stats = SongStat(user = self, song = song)

        stats.playcount = stats.playcount + 1
        stats.lastplayed = datetime.now()
        if session.has_key('src'):
            stats.source = session['src']
        Session.add(stats)

    nowplaying = property(get_nowplaying,set_nowplaying)
    def get_url(self):
        return 'http://%s/player#/people/profile/%d' % (request.host, self.id)
    url = property(get_url)

    def get_top_10_artists(self):
        totalcount = Session.query(Artist.id, Artist.name,
            func.sum(SongStat.playcount).label('totalcount')
        )
        totalcount = totalcount.join([Artist.songs, SongStat])
        totalcount = totalcount.filter(SongStat.uid == self.id)
        # this excludes any songs listened to on friend radio:
        totalcount = totalcount.filter(or_(SongStat.source == SongStat.FROM_OWN_LIBRARY, SongStat.source == SongStat.FROM_BROWSE, SongStat.source == SongStat.FROM_SPOTLIGHT, SongStat.source == None))
        totalcount = totalcount.group_by(Artist.id)
        totalcount = totalcount.order_by(sql.desc('totalcount')).limit(10)
        return totalcount.all()
    top_10_artists = property(get_top_10_artists)

    @personal_cache(expiretime=600, type='memory', addsession=True)
    def get_feed_entries(self):
        max_count=20
        entries = Session.query(BlogEntry)[:max_count]
        myor = or_()
        for friend in self.friends:
            myor.append(Spotlight.uid == friend.id)

        if len(myor)>0:
            entries.extend(Session.query(Spotlight).filter(
                and_(myor, Spotlight.active==True)).\
                order_by(sql.desc(Spotlight.timestamp))\
                    [:max_count])

        commentor = or_()
        spotlightor = or_()
        for friend in self.friends:
            commentor.append(SpotlightComment.uid == friend.id)
            spotlightor.append(Spotlight.uid == friend.id)
            

        if len(commentor)>0 and len(spotlightor)>0:
            entries.extend(Session.query(SpotlightComment).\
                    join((Spotlight, SpotlightComment.spotlight)).\
                    filter(and_(
                        SpotlightComment.uid!=session['userid'],
                        or_(Spotlight.uid==session['userid'],
                            and_(commentor, spotlightor)),
                        Spotlight.active == True)).\
                    order_by(sql.desc(SpotlightComment.timestamp))[:max_count])

        entries.extend(Session.query(Recommendation).\
                filter(and_(
                    Recommendation.recommendeefbid == self.fbid,
                    Recommendation.active == True))[:max_count])

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
        query = Session.query(SongOwner.uid.label('Friend_id'),
            User._name.label('Friend_name'), *dbfields['song'])
        query = query.join(Song.album).reset_joinpoint()
        query = query.join(Song.artist).reset_joinpoint()
        query = query.join(SongOwner, SongOwner.user).filter(SongOwner.uid == self.id)
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
            havesongs.c.Album_length, User._name.label('Friend_name'),
            *dbfields['album'])
        joined = join(Album, havesongs, Album.id == havesongs.c.albumid)
        query = query.select_from(joined)
        query = query.join(Album.artist).reset_joinpoint()
        query = query.join(Album.songs, SongOwner, SongOwner.user).filter(SongOwner.uid == self.id)
        query = query.group_by(Album)
        return query
    album_query = property(get_album_query)
    
    def get_playlist_query(self):
        from masterapp.config.schema import dbfields

        query = Session.query(Playlist.ownerid.label('Friend_id'),
                        *dbfields['playlist']).\
                    filter(Playlist.ownerid == self.id)
        return query
    playlist_query = property(get_playlist_query)

    def get_artist_query(self):
        from masterapp.config.schema import dbfields

        # Build the main query
        query = Session.query(SongOwner.uid.label('Friend_id'),
            User._name.label('Friend_name'),
            ArtistCounts.songcount.label('Artist_availsongs'), 
            ArtistCounts.albumcount.label('Artist_numalbums'),
            *dbfields['artist'])

        query = query.join(Artist.albums, Song, SongOwner, SongOwner.user).\
            join((ArtistCounts, and_( 
                SongOwner.uid == ArtistCounts.userid,
                Artist.id == ArtistCounts.artistid,
                Artist.id == Album.artistid)))
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

    def get_inactive_spotlights(self):
        return Session.query(Spotlight).filter(sql.and_(
                Spotlight.uid==self.id, Spotlight.active==False)).\
                order_by(sql.desc(Spotlight.timestamp))
    inactive_spotlights = property(get_inactive_spotlights)
        
    def get_playlist_by_id(self, id):
        qry = self.playlist_query
        qry = qry.filter(Playlist.id == id)
        return qry.first()            

    def get_song_by_id(self, id):
        return self.song_query.filter(Song.id == id).first()

    def add_song(self, song):
        """
        Adds a song to this user's collection. Keeps counts up to date.
        """

        # Add to collection
        owner = SongOwner(song = song, user = self)

        # Keep counts up to date
        new_album = False
        albumc = Session.query(AlbumCounts).get((song.album.id, self.id))
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
                user=self, artist=song.album.artist, songcount=1, albumcount=1)

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

    @fbaccess
    def update_profile(self):
        c.user = self
        fbml = render('facebook/profile.mako.fbml')
        facebook.profile.setFBML(fbml)

    @fbaccess
    def publish_spotlight(self, spot):
        title_t = '{actor} created <fb:if-multiple-actors>Spotlights <fb:else>a Spotlight </fb:else></fb:if-multiple-actors>on {album} at <a href="http://harmonize.fm" target="_blank">harmonize.fm</a>'
        title_d = '{"album":"%s"}' % spot.title
        r = facebook.feed.publishTemplatizedAction(
            title_template=title_t, 
            title_data=title_d
        )
        return r

    def add_spotlight(self, spotlight):
        spotlight.user = self
        Session.add(spotlight)
        spotlight.unactivate_lru()
        self.publish_spotlight(spotlight)
        self.update_profile()

    def add_me_to_friends(self):
        for friend in self.friends:
            try:
                friend.friends.append(self)
                friend.friends.sort(key=attrgetter('name'))
            except:
                # oh well, they'll find me eventually
                logging.debug('Could not be added to %s', friend.id)

    def update_friends_caches(self):
        for friend in self.friends:
            self.fbfriendscache.remove_value(friend.id)

    def get_recommendations(self):
        return Session.query(Recommendation).filter(
                sql.and_(Recommendation.recommendeefbid == self.fbid, 
                    Recommendation.active == True)).\
                order_by(sql.desc(Recommendation.timestamp))
    recommendations = property(get_recommendations)


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
