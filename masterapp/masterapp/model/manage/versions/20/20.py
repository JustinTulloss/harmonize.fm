from datetime import datetime
from sqlalchemy import *
from sqlalchemy.exceptions import OperationalError
from sqlalchemy.schema import DDL
import migrate.changeset
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

users_table = Table("users", metadata,
    Column("id", Integer, primary_key=True),
)

volcol = Column('lastvolume', Integer)
emailcol = Column('email', Unicode(255))

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    try:
        users_table.append_column(volcol)
        migrate.changeset.create_column(volcol, users_table)

        users_table.append_column(emailcol)
        migrate.changeset.create_column(emailcol, users_table)
    except Exception, e:
        print "Couldn't add columns to users.  Already done? %s" % e

def downgrade():
    # Operations to reverse the above upgrade go here.
    try:
        migrate.changeset.drop_column("email", albums_table)
        migrate.changeset.drop_column("lastvolume", albums_table)
    except:
        print "Couldn't drop columns from users table."
