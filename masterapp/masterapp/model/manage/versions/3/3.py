import pdb
from sqlalchemy import *
from sqlalchemy.exceptions import OperationalError
from sqlalchemy.schema import DDL
import migrate.changeset
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

artists_table = Table("artists", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Unicode(255)),
    Column("mbid", Unicode(36)),
    Column("sort", Unicode(255))
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
    Column("totaltracks", Integer, default=0),
)

songs_table = Table("songs", metadata,
    Column("id", Integer, primary_key=True),
    Column("mbid", Unicode(36), index=True, unique=True),
    Column("title", Unicode(255), index=True),
    Column("length", Integer),
    Column("albumid", Integer, ForeignKey("albums.id"), nullable=False, index=True),
    Column("tracknumber", Integer, default=0)
)

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    artists_table.create()

    newcol = Column('artistid', Integer, ForeignKey("artists.id"), index = True)
    newcol1 = Column('artistid', Integer, ForeignKey("artists.id"), index = True)

    try:
        albums_table.append_column(newcol)
        songs_table.append_column(newcol1)
        migrate.changeset.create_column(newcol, albums_table)
        migrate.changeset.create_column(newcol1, songs_table)
    except OperationalError, e:
        print "Couldn't create new columns, already created?"


    conn = migrate_engine.connect()

    # Populate the table with our old data
    artists = select([
        albums_table.c.artist, 
        albums_table.c.mbartistid,
        albums_table.c.artistsort, 
        ], group_by=albums_table.c.mbartistid, distinct=True)
    
    ins = "insert into artists (name, mbid, sort) %s" % artists;
    conn.execute(ins)

    artistids = select(
        [artists_table.c.id], 
        artists_table.c.mbid == albums_table.c.mbartistid,
    )
    updater = albums_table.update(values = {albums_table.c.artistid: artistids})
    conn.execute(updater)

    conn.close()

    # Drop the old data
    try:
        migrate.changeset.drop_column("artist", albums_table)
        migrate.changeset.drop_column("artistsort", albums_table)
        migrate.changeset.drop_column("mbartistid", albums_table)
    except NotSupportedError, e:
        print "Couldn't drop old artist columns"

def downgrade():
    # Operations to reverse the above upgrade go here.
    try:
        pass
        artists_table.drop()
        migrate.changeset.drop_column(newcol, albums_table)
        migrate.changeset.drop_column(newcol1, songs_table)
    except NotSupportedError, e:
        print "Couldn't drop everything"
