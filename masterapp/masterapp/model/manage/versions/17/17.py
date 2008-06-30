from sqlalchemy import *
from sqlalchemy.exceptions import OperationalError
import migrate.changeset
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

table = Table("notifications", metadata,
    Column("id", Integer, primary_key=True),
)

typecol = Column("type", Unicode(255))
datacol = Column("data", PickleType)

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    try:
        table.append_column(typecol)
        table.append_column(datacol)
        migrate.changeset.create_column(typecol, table)
        migrate.changeset.create_column(datacol, table)
    except OperationalError, e:
        print "Couldn't create new columns, already created?"

def downgrade():
    # Operations to reverse the above upgrade go here.
    try:
        migrate.changeset.drop_column(typecol, table)
        migrate.changeset.drop_column(datacol, table)
    except NotSupportedError, e:
        print "Couldn't drop column"
