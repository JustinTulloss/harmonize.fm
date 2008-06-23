from sqlalchemy import *
from migrate import *
import migrate.changeset
from sqlalchemy import exceptions
from migrate.changeset.exceptions import NotSupportedError


metadata = MetaData(migrate_engine)

spotlights = Table('spotlights', metadata,
        Column('id', Integer, primary_key=True),
        Column('uid', Integer, ForeignKey('users.id'), index=True),
        Column('albumid', Integer, ForeignKey('albums.id')),
        Column('timestamp', DateTime),
        Column('comment', Unicode(255)))

playlistid = Column('playlistid', Integer, ForeignKey('playlists.id'))

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
	migrate.changeset.create_column(playlistid, spotlights)

def downgrade():
    # Operations to reverse the above upgrade go here.
	try:
		migrate.changeset.drop_column(playlistid, spotlights)
	except NotSupportedError, e:
		pass
