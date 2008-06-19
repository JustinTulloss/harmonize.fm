from sqlalchemy import *
import migrate.changeset
from sqlalchemy.exceptions import OperationalError
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

# Old tables
users_table = Table("users", metadata,
    Column("id", Integer, primary_key=True)
)

songs_table = Table("songs", metadata,
    Column("id", Integer, primary_key=True),
)

files_table = Table("files", metadata,
    Column("id", Integer, primary_key=True),
    Column("sha", String(40), index=True, unique=True),
    Column("songid", Integer, ForeignKey("songs.id"), nullable=False, index=True),
)

owners_table = Table("owners", metadata,
    Column("songid", Integer, ForeignKey("songs.id")),
    Column("uid", Integer, ForeignKey("users.id")),
    Column("fileid", Integer, ForeignKey("files.id"))
)

# New tables
songowners_table = Table("songowners", metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", Integer, ForeignKey("users.id")),
    Column("songid", Integer, ForeignKey("songs.id"))
)

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.

    songowners_table.create()
    try:
        migrate.changeset.drop_column(owners_table.c.songid, owners_table)
    except NotSupportedError, e:
        print "Couldn't drop the songid column"

    conn = migrate_engine.connect()
    # Populate the table with our old data
    owners = select([
        owners_table.c.uid,
        files_table.c.songid
        ], owners_table.c.fileid==files_table.c.id)
    
    ins = "insert into songowners (uid, songid) %s" % owners;
    conn.execute(ins)

def downgrade():
    # Operations to reverse the above upgrade go here.
    songowners_table.drop()
