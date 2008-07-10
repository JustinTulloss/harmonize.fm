from sqlalchemy import *
from sqlalchemy.exceptions import OperationalError
from sqlalchemy.schema import DDL
import migrate.changeset
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

songstats = Table('songstats', metadata,
    Column('id', Integer, primary_key=True)
)

source_col = Column('source', Integer)

def upgrade():
    songstats.append_column(source_col)
    migrate.changeset.create_column(source_col, songstats)

def downgrade():
    try:
        migrate.changeset.drop_column('source', songstats)
    except NotSupportedError:
        print "Can't downgrade."
