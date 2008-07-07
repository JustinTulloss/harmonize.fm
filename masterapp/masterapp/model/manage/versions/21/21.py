from sqlalchemy import *
from sqlalchemy.sql import insert, text
import migrate.changeset
from sqlalchemy.exceptions import OperationalError
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

# Old tables
songs_table = Table("songs", metadata,
    Column("id", Integer, primary_key=True),
    Column("artistid", Integer, ForeignKey("artists.id")),
    Column("albumid", Integer, ForeignKey("albums.id")),
)

artists_table = Table("artists", metadata,
    Column("id", Integer, primary_key=True),
)

albums_table = Table("albums", metadata,
    Column("id", Integer, primary_key=True),
    Column("artistid", Integer, ForeignKey("artists.id")),
)

songowners_table = Table('songowners', metadata,
    Column("id", Integer, primary_key=True),
    Column("songid", Integer, ForeignKey("songs.id")),
    Column("uid", Integer, ForeignKey("users.id"))
)

users_table = Table("users", metadata,
    Column("id", Integer, primary_key=True)
)

# New tables
artist_count_table = Table("counts_artist", metadata,
    Column("artistid", Integer, ForeignKey("artists.id")),
    Column("userid", Integer, ForeignKey("users.id")),
    Column("albumcount", Integer),
    Column("songcount", Integer)
)

album_count_table = Table("counts_album", metadata,
    Column("albumid", Integer, ForeignKey("albums.id")),
    Column("userid", Integer, ForeignKey("users.id")),
    Column("songcount", Integer)
)

# New Indexes
ix_artist = Index('ix_counts_artist', artist_count_table.c.artistid,
    artist_count_table.c.userid, unique=True)
ix_album = Index('ix_counts_album', album_count_table.c.albumid,
    album_count_table.c.userid, unique=True)

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.

    try:
        try:
            artist_count_table.create()
            album_count_table.create()

            ix_artist.create()
            ix_album.create()
        except Exception, e:
            print e
        # Populate table
        """
        data = select(
            [artists_table.c.id, users_table.c.id, func.count(albums_table.c.id)],
            albums_table.c.artistid == artists_table.c.id, 
            from_obj = artists_table.join(albums_table).join(songs_table).join(
            songowners_table).join(users_table)).group_by(users_table.c.id, albums_table.c.id)
        """
        songs_artist_counts = text("""
            SELECT albums.artistid, users.id, count(songs.id) as songs_artist FROM users join songowners on users.id = songowners.uid join songs on songowners.songid = songs.id join albums on songs.albumid = albums.id group by users.id, songs.albumid; """) 
        songs_album_count = text("""
            insert into counts_album select songs.albumid, songowners.uid, count(songs.id) from songs 
            join songowners on songs.id = songowners.songid group by songowners.uid,
            songs.albumid;
        """)

        albums_artist_count = text("""
            select albums.artistid, useralbums.uid, count(albums.id) from albums join (select songowners.uid as uid, songs.albumid as aid from songs join songowners on songs.id = songowners.songid group by songowners.uid, songs.albumid) as useralbums on albums.id = useralbums.aid group by useralbums.uid, albums.artistid;
        """)

        artist_counts = text("""
        insert into counts_artist selecT mesongs.artistid, mesongs.uid,
        mealbums.albums_artist, sum(mesongs.songs_artist) from (SELECT albums.artistid as artistid, users.id as uid, count(songs.id) as songs_artist FROM users join songowners on users.id = songowners.uid join songs on songowners.songid = songs.id join albums on songs.albumid = albums.id group by users.id, songs.albumid) as mesongs, (seLect albums.artistid as artistid, useralbums.uid as uid, count(albums.id) as albums_artist from albums join (selEct songowners.uid as uid, songs.albumid as aid from songs join songowners on songs.id = songowners.songid group by songowners.uid, songs.albumid) as useralbums on albums.id = useralbums.aid group by useralbums.uid, albums.artistid) as mealbums where mealbums.artistid = mesongs.artistid and mealbums.uid = mesongs.uid group by mesongs.uid, mesongs.artistid;    """)

        #ins_artists = artist_count_table.(artist_counts)
        #ins_albums = album_count_table.insert(songs_album_count)
        migrate_engine.execute(artist_counts)
        migrate_engine.execute(songs_album_count)
    except Exception, e:
        print "Couldn't do everything, some things already done?", e


    

def downgrade():
    # Operations to reverse the above upgrade go here.
    try:
        artist_count_table.drop()
        album_count_table.drop()
    except:
        print "Couldn't drop everything"


