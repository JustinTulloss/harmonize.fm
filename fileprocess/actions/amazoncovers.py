import logging
from baseaction import BaseAction
import ecs
from time import sleep
from configuration import config

log = logging.getLogger(__name__)

class AmazonCovers(BaseAction):
    covercache = {}

    def process(self, file):
        if not file.has_key(u'asin'):
            return file

        if self.covercache.has_key(file[u'asin']):
            return self.fill_file(file, self.covercache[file[u'asin']])

        ecs.setLicenseKey(config['S3.accesskey'])
        try:
            aitem = ecs.ItemLookup(
                file[u'asin'], 
                IdType='ASIN',
                ResponseGroup='Images'
            )
        except ecs.AWSException, e:
            sleep(1)
            return file #just keep going, we don't need albumart

        images = aitem.next()
        self.covercache[file[u'asin']] = images

        sleep(1) #We're only allowed to make 1 request per second. Lame.
        log.info("Found album art for %s", file.get('title'))
        return self.fill_file(file, images)

    def fill_file(self, file, images):
        try:
            if isinstance(images.ImageSets.ImageSet, list):
                file[u'swatch'] = images.ImageSets.ImageSet[0].SwatchImage.URL
            else:
                file[u'swatch'] = images.ImageSets.ImageSet.SwatchImage.URL
            file[u'smallart'] = images.SmallImage.URL
            file[u'medart'] = images.MediumImage.URL
            file[u'largeart'] = images.LargeImage.URL
        except:
            pass # album art doesn't matter
        return file