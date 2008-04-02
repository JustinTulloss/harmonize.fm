import logging
from baseaction import BaseAction
import ecs
from time import sleep
from pylons import config

log = logging.getLogger(__name__)

class AmazonCovers(BaseAction):
    def process(self, file):
        if not file.has_key('asin'):
            return file

        ecs.setLicenseKey(config['S3.accesskey'])
        try:
            aitem = ecs.ItemLookup(
                file['asin'], 
                IdType='ASIN',
                ResponseGroup='Images'
            )
        except ecs.AWSException, e:
            sleep(1)
            return file #just keep going, we don't need albumart

        images = aitem.next()
        file[u'swatch'] = images.ImageSets.ImageSet.SwatchImage.URL
        file[u'smallart'] = images.SmallImage.URL
        file[u'medart'] = images.MediumImage.URL
        file[u'largeart'] = images.LargeImage.URL
        sleep(1) #We're only allowed to make 1 request per second. Lame.
        return file
