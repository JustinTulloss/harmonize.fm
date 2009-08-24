# dave paola
# check the asin of the file and make sure it doesn't return
# an error from amazon before inserting into the database

import logging
from pylons import config
from baseaction import BaseAction
from ecs import *
log = logging.getLogger(__name__)
from time import sleep
from lrucache import LRUCache
CACHE_EXPIRATION = 60*60

class CheckForBadAsin(BaseAction):
    def __init__(self, *args, **kwargs):
        super(CheckForBadAsin, self).__init__(*args, **kwargs)
        self.cache = LRUCache(size=100)
    
    def process(self, file):
        if not file.has_key(u'asin'):
            return file
        
        if file[u'asin'] in self.cache:
            file[u'asin'] = self.cache[file[u'asin']]
            return file

        return self.check_asin(file)

    def check_asin(self, file):
        asin = file.get(u'asin')
        
        try:
            response = ItemLookup(asin, IdType="ASIN", AWSAccessKeyId='17G635SNK33G1Y7NZ2R2')
            sleep(1)
        except:
            # asin not found in amazon's database
            file[u'asin'] = ''
            sleep(1)
            return file
        # this asin is valid, make sure the cache says so
        self.cache[file[u'asin']] = file[u'asin']
        return file

