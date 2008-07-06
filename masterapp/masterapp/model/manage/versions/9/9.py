from sqlalchemy import *
from sqlalchemy.exceptions import OperationalError
from migrate import *
import migrate.changeset
from migrate.changeset.exceptions import NotSupportedError

metadata = MetaData(migrate_engine)

users = Table('users', metadata,
	Column('id', Integer, primary_key=True))

albums = Table('albums', metadata,
	Column('id', Integer, primary_key=True))

spotlight = Table('spotlights', metadata,
	Column('id', Integer, primary_key=True),
	Column('uid', Integer, ForeignKey('users.id'), index=True),
	Column('albumid', Integer, ForeignKey('albums.id')),
	Column('timestamp', DateTime),
	Column('comment', Unicode(255)))

spot_active = Column('active', Boolean)

def upgrade():
    try:
	    migrate.changeset.create_column(spot_active, spotlight)
    except OperationalError, e:
        print "Couldn't create new columns, already created? %s" % e

def downgrade():
	try:
		migrate.changeset.drop_column(spot_active, spotlight)
	except NotSupportedError:
		pass
