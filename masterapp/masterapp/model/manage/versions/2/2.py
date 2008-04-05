from sqlalchemy import *
from sqlalchemy.schema import DDL
import migrate.changeset
from migrate import *

metadata = MetaData(migrate_engine)
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
        migrate.changeset.create_column(col, albums_table)

def downgrade():
    # Operations to reverse the above upgrade go here.
    for col in newcols:
        try:
            migrate.changeset.drop_column(col, albums_table)
        except NotSupportedError, e:
            pass
