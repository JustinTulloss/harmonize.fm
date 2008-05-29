from sqlalchemy import *
from migrate import *

metadata = MetaData(migrate_engine)

users = Table('users', metadata,
	Column('id', Integer, primary_key=True))

users = Table('albums', metadata,
	Column('id', Integer, primary_key=True))

spotlight = Table('spotlights', metadata,
	Column('id', Integer, primary_key=True),
	Column('uid', Integer, ForeignKey('users.id'), index=True),
	Column('albumid', Integer, ForeignKey('albums.id')),
	Column('timestamp', DateTime),
	Column('comment', Unicode(255)))

def upgrade():
    spotlight.create()

def downgrade():
	spotlight.drop()
