from sqlalchemy import *
from migrate import *

metadata = MetaData(migrate_engine)

files_table = Table("files", metadata,
    Column("id", Integer, primary_key=True),
    Column("sha", String(40), index=True, unique=True),
    Column("songid", Integer, ForeignKey("songs.id"), nullable=False, index=True),
)

owners_table = Table("owners", metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", Integer, ForeignKey('users.id'), nullable=False, index=True),
    Column("fileid", Integer, ForeignKey("files.id"), nullable=False, index=True),
)

users_table = Table("users", metadata,
    Column("id", Integer, primary_key=True),
    Column("fbid", Integer, nullable=False, index=True, unique=True),
)

songstats_table = Table("songstats", metadata,
    Column("id", Integer, primary_key=True),
    Column("songid", Integer, ForeignKey("songs.id"), nullable=False, index=True),
    Column("uid", Integer, ForeignKey('users.id'), index=True),
    Column("lastrecommended", DateTime, nullable=False),
    Column("playcount", Integer, nullable=False)
)

songs_table = Table("songs", metadata,
    Column("id", Integer, primary_key=True),
    Column("mbid", Unicode(36), index=True, unique=True),
    Column("title", Unicode(255), index=True),
    Column("length", Integer),
    Column("albumid", Integer, ForeignKey("albums.id"), nullable=False, index=True),
    Column("tracknumber", Integer, default=0)
)

albums_table = Table("albums", metadata,
    Column("id", Integer, primary_key=True),
    Column("mbid", Unicode(36), index=True),
    Column("artist", Unicode(255), index=True),
    Column("artistsort", Unicode(255)),
    Column("mbartistid", Unicode(36), index=True),
    Column("asin", Unicode(10)),
    Column("title", Unicode(255), index=True),
    Column("year", Integer, index=True),
    Column("totaltracks", Integer, default=0)
)

playlists_table = Table("playlists", metadata,
    Column("id", Integer, primary_key=True),
    Column("ownerid", Integer, ForeignKey("users.id"), nullable=False, index=True),
    Column("name", Unicode(255))
)

playlistsongs_table= Table("playlistsongs", metadata,
    Column("id", Integer, primary_key=True),
    Column("playlistid", Integer, ForeignKey("playlists.id"), nullable=False, index=True),
    Column("songindex", Integer),
    Column("songid", Integer, ForeignKey("songs.id"), nullable=False)
)

blockedfriends_table = Table("blockedfriends", metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", Integer, ForeignKey('users.id'), index=True),
    Column("blockid", Integer, ForeignKey('users.id'))
)

blockedartists_table = Table("blockedartists", metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", Integer, ForeignKey('users.id'), index=True),
    Column("mbartistid", Unicode(36))
)

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    metadata.create_all(bind=migrate_engine)

def downgrade():
    # Operations to reverse the above upgrade go here.
    metadata.drop_all()
