import sqlalchemy
from sqlalchemy import engine_from_config
import re

from mock import Mock
from fileprocess.configuration import config
from pylons import config as pconfig
pconfig['pylons.g'] = Mock()
pconfig['pylons.g'].sa_engine = engine_from_config(config,
    prefix = 'sqlalchemy.default.'
)
from masterapp import model

cleaner = re.compile('^([!@#$%^&*\-_+=<>,.;:\'{}|`~".()\[\]\\\]+|the )', re.IGNORECASE)


artists = model.Session.query(model.Artist).all()

for artist in artists:
    newname = cleaner.sub('', artist.name)
    if newname:
        artist.sort = newname
        model.Session.add(artist)

model.Session.commit()
