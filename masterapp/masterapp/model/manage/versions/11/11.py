from sqlalchemy import *
from sqlalchemy.exceptions import OperationalError
import migrate.changeset
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

songs_table = Table("songs", metadata,
    Column("id", Integer, primary_key=True),
)

owners_table = Table("owners", metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", Integer, ForeignKey('users.id'), nullable=False, index=True),
    Column("fileid", Integer, ForeignKey("files.id"), nullable=False, index=True),
)

files_table = Table("files", metadata,
    Column("id", Integer, primary_key=True),
    Column("sha", String(40), index=True, unique=True),
    Column("songid", Integer, ForeignKey("songs.id"), nullable=False, index=True),
)

songidcol = Column("songid", Integer, ForeignKey("songs.id"))

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    try:
        owners_table.append_column(songidcol)
        migrate.changeset.create_column(songidcol, owners_table)
    except OperationalError, e:
        print "Couldn't create new columns, already created?"


    conn = migrate_engine.connect()

    # Populate the table with our old data
    ids = select(
        [files_table.c.songid], 
        owners_table.c.fileid == files_table.c.id
    )
    updater = owners_table.update(values = {owners_table.c.songid: ids})
    conn.execute(updater)

    conn.close()

def downgrade():
    # Operations to reverse the above upgrade go here.
    try:
        migrate.changeset.drop_column(songidcol, owners_table)
    except NotSupportedError, e:
        print "Couldn't drop column"
