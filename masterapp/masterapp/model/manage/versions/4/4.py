
from sqlalchemy import *
from sqlalchemy.exceptions import OperationalError
from sqlalchemy.schema import DDL
import migrate.changeset
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)


newcol1 = Column('artistid', Integer, ForeignKey("artists.id"), index = True)

albums_table = Table("albums", metadata,
    Column("id", Integer, primary_key=True),
    Column("mbid", Unicode(36), index=True),
    Column("artist", Unicode(255), index=True),
    Column("artistsort", Unicode(255)),
    Column("mbartistid", Unicode(36), index=True),
    Column("asin", Unicode(10)),
    Column("title", Unicode(255), index=True),
    Column("year", Integer, index=True),
    Column("totaltracks", Integer, default=0),
    Column('artistid', Integer, ForeignKey("artists.id"), index = True),
)

songs_table = Table("songs", metadata,
    Column("id", Integer, primary_key=True),
    Column("mbid", Unicode(36), index=True, unique=True),
    Column("title", Unicode(255), index=True),
    Column("length", Integer),
    Column("albumid", Integer, ForeignKey("albums.id"), nullable=False, index=True),
    Column("tracknumber", Integer, default=0),
    Column('artistid', Integer, ForeignKey("artists.id"), index = True),
)

artists_table = Table("artists", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Unicode(255)),
    Column("mbid", Unicode(36)),
    Column("sort", Unicode(255))
)


def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.

    # I forgot to update the songs table in the last version, so doing that here
    artistids = select(
        [albums_table.c.artistid],
        albums_table.c.id == songs_table.c.albumid,
    )
    updater = songs_table.update(values = {songs_table.c.artistid: artistids})
    migrate_engine.execute(updater)

def downgrade():
    # Operations to reverse the above upgrade go here.
    updater = songs_table.update(values = {songs_table.c.artistid: None})
    migrate_engine.execute(updater)
