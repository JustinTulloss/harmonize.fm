from time import sleep
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
from masterapp.model import *

from fileprocess.actions import AmazonASINConvert

albums = model.Session.query(Album).all()
file = {}

for album in albums:
    if album.title and album.artist and album.artist.name and album.asin:
        file['album'] = album.title
        file['artist'] = album.artist.name
        file['asin'] = album.asin
        a = AmazonASINConvert()
        file = a.process(file)

        album.mp3_asin = file['mp3_asin']



model.Session.commit()
