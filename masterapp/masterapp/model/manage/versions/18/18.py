from sqlalchemy import *
from sqlalchemy.exceptions import OperationalError
from migrate import *
import migrate.changeset
from migrate.changeset.exceptions import NotSupportedError

metadata = MetaData(migrate_engine)

users = Table('users', metadata,
    Column('id', Integer, primary_key=True)
)

songs = Table('songs', metadata,
    Column('id', Integer, primary_key=True)
)
    
removedowners = Table('removedowners', metadata,
    Column('id', Integer, primary_key=True),
    Column('songid', Integer, ForeignKey('songs.id')),
    Column('uid', Integer, ForeignKey('users.id'))
)

def upgrade():
    removedowners.create()

def downgrade():
    removedowners.drop()
