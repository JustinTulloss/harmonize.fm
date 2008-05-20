from datetime import datetime
from sqlalchemy import *
from sqlalchemy.exceptions import OperationalError
from sqlalchemy.schema import DDL
import migrate.changeset
from migrate.changeset.exceptions import NotSupportedError
from migrate import *

metadata = MetaData(migrate_engine)

blog_table = Table("blog", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", Unicode(255), index=True),
    Column("entry", UnicodeText),
    Column("author", Unicode(255), index=True),
    Column("timestamp", DateTime, default = datetime.now),
)

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    blog_table.create()

def downgrade():
    # Operations to reverse the above upgrade go here.
    blog_table.drop()
