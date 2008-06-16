import logging
import os
import subprocess
from baseaction import BaseAction
from fileprocess.processingthread import na
from fileprocess.configuration import config
import musicdns
import fileprocess
from xml.etree import cElementTree as ElementTree

log = logging.getLogger(__name__)

class PuidGenerator(BaseAction):
    def __init__(self, *args, **kwargs):
        super(PuidGenerator, self).__init__(*args, **kwargs)
        musicdns.initialize()

    def process(self, file):
        if file.get('puid'):
            return file

        if not file.has_key('fname'):
            return file

        if not os.path.exists(file.get('fname')):
            return file

        fp = musicdns.create_fingerprint(file['fname'])
        puid = musicdns.lookup_fingerprint(fp[0], fp[1], config['musicdns.key'])
        
        log.debug('%s has puid %s', file.get('title'), puid)
        if puid:
            file['puid'] = puid
            return file
        else:
            # Spin off a process to do the analysis, we don't care if it
            # succeeds or fails, we're just helping out MusicDNS
            gp = subprocess.Popen(
                ['genpuid', config['musicdns.key'], '-xml', 
                os.path.abspath(file['fname'])],
                stdout=open('/dev/null')
            )
            return file

