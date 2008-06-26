from sqlalchemy import *
import migrate.changeset
from sqlalchemy.exceptions import OperationalError
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

# Old tables
songs_table = Table("songs", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", Unicode(255)),
    Column("mbid", String(36), index=True)
)

albums_table = Table("albums", metadata,
    Column("title", Unicode(255))
)

artists_table = Table("artists", metadata,
    Column("name", Unicode(255)),
    Column("mbid", String(36), index=True)
)
# New indices
atitle = Index('ix_albums_title', albums_table.c.title)
stitle = Index('ix_songs_title', songs_table.c.title)
aname = Index('ix_artists_name', artists_table.c.name)
ambid = Index('ix_artists_mbid', artists_table.c.mbid)

smbid = Index('ix_songs_mbid', songs_table.c.mbid)

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    try:
        atitle.create()
        stitle.create()
        aname.create()

        smbid.drop()
        smbid.create() #keep the index, it used to be unique
    except OperationalError, e:
        print "Could not upgrade everything, some existed?: %s", e

def downgrade():
    try:
        atitle.drop()
        stitle.drop()
        aname.drop()

    except OperationalError, e:
        print "Could not downgrade everything, did some indices not exist?, %s", e
