from sqlalchemy import *
from sqlalchemy.schema import DDL
from migrate import *

meta = MetaData(migrate_engine)
songs_table = Table("songs", meta,
    Column("id", Integer, primary_key=True),
    Column("mbid", Unicode(36), index=True, unique=True),
    Column("title", Unicode(255), index=True),
    Column("length", Integer),
    Column("albumid", Integer, ForeignKey("albums.id"), nullable=False, index=True),
    Column("tracknumber", Integer, default=0)
)

newcols = [
    Column('swatch', Unicode(255)),
    Column('smallart', Unicode(255)),
    Column('medart', Unicode(255)),
    Column('largeart', Unicode(255))
]

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    for col in newcols:
        songs_table.append_column(col)

def downgrade():
    # Operations to reverse the above upgrade go here.
    for col in newcols:
        drp = DDL('ALTER TABLE songs DROP COLUMN '+col.name, on='mysql')
        drp.execute(bind=migrate_engine)
