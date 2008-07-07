from sqlalchemy import *
from sqlalchemy.exceptions import OperationalError
from sqlalchemy.schema import DDL
import migrate.changeset
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

users_table = Table('users', metadata,
	Column('id', Integer, primary_key=True))

premiumcol = Column('premium', Boolean)

def upgrade():
	users_table.append_column(premiumcol)
	migrate.changeset.create_column(premiumcol, users_table)

def downgrade():
	try:
		migrate.changeset.drop_column('premium', users_table)
	except NotSupportedError:
		print 'Unable to downgrade!'
