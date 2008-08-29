import logging
import os
import subprocess
from baseaction import BaseAction
from fileprocess.processingthread import na
from fileprocess.configuration import config
try:
    import musicdns
except ImportError:
    musicdns = None

import fileprocess

log = logging.getLogger(__name__)

class PuidGenerator(BaseAction):
    def __init__(self, *args, **kwargs):
        global musicdns 
        super(PuidGenerator, self).__init__(*args, **kwargs)
        if musicdns:
            musicdns.initialize()

    def can_skip(self, new_file):
        if file.get('puid'):
            return True
        else: 
            return False

    def process(self, file):
        global musicdns 
        if not musicdns:
            return file

        if file.get('puid'):
            return file

        if not file.has_key('fname'):
            return file

        if not os.path.exists(file['fname']):
            return file

        try:
            fp = musicdns.create_fingerprint(file['fname'])
            puid = musicdns.lookup_fingerprint(fp[0], fp[1], config['musicdns.key'])
        except Exception, e:
            log.warn("Could not fingerprint %s: %s", file['fname'], e)
            return file #We don't need the fingerprint per say
        
        log.debug('%s has puid %s', file.get('title'), puid)
        if puid != None:
            file['puid'] = puid
            return file
        else:
            # Spin off a process to do the analysis, we don't care if it
            # succeeds or fails, we're just helping out MusicDNS
            try:
                gp = subprocess.Popen(
                    ['genpuid', config['musicdns.key'], '-xml', 
                    os.path.abspath(file['fname'])],
                    stdout=open('/dev/null')
                )
            except Exception, e:
                log.info("Could not generate puid: %s", e)
            return file

