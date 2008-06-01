from sqlalchemy import *
from sqlalchemy import exceptions
from sqlalchemy.schema import DDL
import migrate.changeset
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

#Old table definitions
songs_table = Table("songs", metadata,
    Column("id", Integer, primary_key=True),
    Column("mbid", Unicode(36), index=True, unique=True),
    Column("title", Unicode(255), index=True),
    Column("length", Integer),
    Column("albumid", Integer, ForeignKey("albums.id"), nullable=False, index=True),
    Column("tracknumber", Integer, default=0)
)

songstats_table = Table("songstats", metadata,
    Column("id", Integer, primary_key=True),
    Column("songid", Integer, ForeignKey("songs.id"), nullable=False, index=True),
    Column("uid", Integer, ForeignKey('users.id'), index=True),
    Column("lastrecommended", DateTime, nullable=False),
    Column("playcount", Integer, nullable=False)
)

users_table = Table("users", metadata,
    Column("id", Integer, primary_key=True),
    Column("fbid", Integer, nullable=False, index=True, unique=True),
)

# New Columns
lastseen = Column("lastseen", DateTime)
nowplaying = Column("nowplayingid", Integer, ForeignKey("songs.id"))
fbsession = Column("fbsession", Unicode(40))

lastplayed = Column("lastplayed", DateTime)

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.

    migrate.changeset.create_column(lastseen, users_table)
    migrate.changeset.create_column(nowplaying, users_table)
    migrate.changeset.create_column(fbsession, users_table)

    migrate.changeset.create_column(lastplayed, songstats_table)

def downgrade():
    # Operations to reverse the above upgrade go here.
    try:
        migrate.changeset.drop_column(lastseen, users_table)
        migrate.changeset.drop_column(nowplaying, users_table)
        migrate.changeset.drop_column(fbsession, users_table)

        migrate.changeset.drop_column(lastplayed, songstats_table)
    except NotSupportedError, e:
        pass
