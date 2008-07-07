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
from ecs import *

albums = model.Session.query(Album).all()

for album in albums:
    if album.title and album.artist and album.artist.name and album.asin:
        try:
            response = ItemLookup(album.asin, IdType="ASIN", AWSAccessKeyId='17G635SNK33G1Y7NZ2R2')
            # at this point, we know that the ItemLookup returned, so the ASIN must be valid.
            #print album.title + " is ok."
            sleep(1)
        except:
            # this asin must not exist because it threw an exception.  We need to remove the ASIN field from the album.
            #print album.title + " does not have an asin, correcting..."
            album.asin = ''
            album.mp3asin = ''
            
            Session.commit()
            #print "done."
            sleep(1)
print "All done."
