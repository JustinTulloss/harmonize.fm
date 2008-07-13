from sqlalchemy import *
from sqlalchemy.exceptions import OperationalError
from sqlalchemy.schema import DDL
import migrate.changeset
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

users = Table('users', metadata, Column('id', Integer, primary_key=True))
albums = Table('albums', metadata, Column('id', Integer, primary_key=True))
playlists = Table('playlists', metadata, Column('id',Integer, primary_key=True))
songs = Table('songs', metadata, Column('id', Integer, primary_key=True))

recommendations = Table('recommendations', metadata,
	Column('id', Integer, primary_key=True),
	Column('recommenderid', Integer, ForeignKey('users.id')),
	Column('recommendeefbid', Integer),
	Column('albumid', Integer, ForeignKey('albums.id')),
	Column('playlistid', Integer, ForeignKey('playlists.id')),
	Column('songid', Integer, ForeignKey('songs.id')),
	Column('timestamp', DateTime),
	Column('active', Boolean),
	Column('comment', Text)
)

def upgrade():
	recommendations.create()

def downgrade():
	recommendations.drop()
