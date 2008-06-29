from sqlalchemy import *
from migrate import *
import migrate.changeset
from sqlalchemy import exceptions
from migrate.changeset.exceptions import NotSupportedError

metadata = MetaData(migrate_engine)

notifications_table = Table('notifications', metadata,
    Column('id', Integer, primary_key = True),
    Column('email', Unicode(255))
)

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    notifications_table.create()

def downgrade():
    # Operations to reverse the above upgrade go here.
    notifications_table.drop()
