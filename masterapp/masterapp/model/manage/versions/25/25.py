from sqlalchemy import *
from sqlalchemy.sql import insert, text
import migrate.changeset
from sqlalchemy.exceptions import OperationalError
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)


users_table = Table('users', metadata,
    Column('id', Integer, primary_key = True)
)

namecol = Column('name', Unicode(255), index = True)

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.

    try:
        users_table.append_column(namecol)
        migrate.changeset.create_column(namecol, users_table)
    except OperationalError, e:
        print "Could not create all columns", e

def downgrade():
    try:
        migrate.changeset.drop_column("name", users_table)
    except NotSupportedError:
        print "Couldn't drop name column from users table, not supported"
