from sqlalchemy import *
import migrate.changeset
from sqlalchemy.exceptions import OperationalError
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

# Old tables
songs_table = Table("songs", metadata,
    Column("id", Integer, primary_key=True),
)

files_table = Table("files", metadata,
    Column("id", Integer, primary_key=True),
    Column("sha", String(40), index=True, unique=True),
    Column("songid", Integer, ForeignKey("songs.id"), nullable=False, index=True),
)

# New tables
puid_table = Table("puids", metadata,
    Column("id", Integer, primary_key = True),
    Column("puid", Unicode(36), index=True),
    Column("songid", Integer, ForeignKey("songs.id"), index=True)
)

# New Columns
shacol = Column("sha", String(40))
pristinecol = Column("pristine",Boolean)
bitratecol = Column("bitrate", Integer)
sizecol = Column("size", Integer) #Can't support files > 4 GB
bitratecol1 = Column("bitrate", Integer)
sizecol1 = Column("size", Integer) #Can't support files > 4 GB

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.

    puid_table.create()
    try:

        songs_table.append_column(shacol)
        songs_table.append_column(pristinecol)
        songs_table.append_column(bitratecol)
        songs_table.append_column(sizecol)

        files_table.append_column(bitratecol1)
        files_table.append_column(sizecol1)

        migrate.changeset.create_column(shacol, songs_table)
        migrate.changeset.create_column(pristinecol, songs_table)
        migrate.changeset.create_column(bitratecol, songs_table)
        migrate.changeset.create_column(sizecol, songs_table)

        migrate.changeset.create_column(bitratecol1, files_table)
        migrate.changeset.create_column(sizecol1, files_table)

    except OperationalError, e:
        print "Couldn't create new columns, already created? %s" % e

def downgrade():
    # Operations to reverse the above upgrade go here.
    puid_table.drop()
    try:

        migrate.changeset.drop_column(shacol, songs_table)
        migrate.changeset.drop_column(pristinecol, songs_table)
        migrate.changeset.drop_column(bitratecol, songs_table)
        migrate.changeset.drop_column(sizecol, songs_table)

        migrate.changeset.drop_column(bitratecol1, files_table)
        migrate.changeset.drop_column(sizecol1, files_table)

    except NotSupportedError, e:
        print "Couldn't drop everything"
