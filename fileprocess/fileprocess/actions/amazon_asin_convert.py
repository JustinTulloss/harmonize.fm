# dave paola
# grabs mp3 asins from amazon if they can be found
# and puts them into the mp3_asin field

import logging
from pylons import config
from baseaction import BaseAction
from ecs import *
from beaker.cache import Cache
log = logging.getLogger(__name__)
from time import sleep
CACHE_EXPIRATION = 60*60*60

class AmazonASINConvert(BaseAction):
    cache = Cache(
        namespace = 'amazon.mp3_asins',
        expires = CACHE_EXPIRATION
    )

    def process(self, file):
        if not file.has_key(u'asin'):
            return file
        if not file.has_key(u'artist'):
            return file
        if not file.has_key(u'album'):
            return file
        
        if self.cache.has_key(file[u'album']):
            file[u'mp3_asin'] = self.cache[file[u'album']]
            return file
        return self.get_asin(file)


    def get_asin(self,file):
        asin = file.get(u'asin')
        artist = file.get(u'artist')
        album = file.get(u'album')
        file[u'mp3_asin'] = ''

        try:
            items = ItemSearch(file['artist'], Title=file['album'], SearchIndex="MP3Downloads", AWSAccessKeyId='17G635SNK33G1Y7NZ2R2')
            for item in items:
                if item.ProductGroup == "Digital Music Album" and item.Creator.lower() == file['artist'].lower():
                    file[u'mp3_asin'] = item.ASIN
                    break
        except:
            file[u'mp3_asin'] = ''
        self.cache[file[u'album']] = file[u'mp3_asin']
        sleep(1) # to satisfy 1 request per second from amazon :-(
        return file

