
from sqlalchemy import *
import migrate.changeset
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

#Old table definitions
users_table = Table("users", metadata,
    Column("id", Integer, primary_key=True),
    Column("fbid", Integer, nullable=False, index=True, unique=True),
)

spotlight = Table('spotlights', metadata,
	Column('id', Integer, primary_key=True),
	Column('uid', Integer, ForeignKey('users.id'), index=True),
	Column('albumid', Integer, ForeignKey('albums.id')),
	Column('timestamp', DateTime),
	Column('comment', Unicode(255))
)

# New Table
spot_comments_table = Table('spotlight_comments', metadata,
    Column('id', Integer, primary_key=True),
    Column('uid', Integer, ForeignKey('users.id')),
    Column('spotlightid', Integer, ForeignKey('spotlights.id'), index=True),
    Column('timestamp', DateTime),
    Column('comment', Text)
)


def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    spot_comments_table.create()

def downgrade():
    # Operations to reverse the above upgrade go here.
    spot_comments_table.drop()
