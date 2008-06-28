from sqlalchemy import *
from migrate import *
import migrate.changeset
from sqlalchemy import exceptions
from migrate.changeset.exceptions import NotSupportedError

metadata = MetaData(migrate_engine)

whitelists_table = Table('whitelists', metadata,
        Column('id', Integer, primary_key = True),
        Column('fbid', Integer),
        Column('registered', Boolean)
)

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    whitelists_table.create()

def downgrade():
    # Operations to reverse the above upgrade go here.
    whitelists_table.drop()
