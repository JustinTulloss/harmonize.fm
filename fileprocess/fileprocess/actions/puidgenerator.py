import logging
import os
import subprocess
from baseaction import BaseAction
from fileprocess.processingthread import na
from fileprocess.configuration import config
active = True
try:
    import musicdns
except ImportError:
    active = False

import fileprocess

log = logging.getLogger(__name__)

class PuidGenerator(BaseAction):
    def __init__(self, *args, **kwargs):
        global active
        super(PuidGenerator, self).__init__(*args, **kwargs)
        if active:
            musicdns.initialize()

    def process(self, file):
        global active
        if not active:
            return file

        if file.get('puid'):
            return file

        if not file.has_key('fname'):
            return file

        if not os.path.exists(file.get('fname')):
            return file

        try:
            fp = musicdns.create_fingerprint(file['fname'])
            puid = musicdns.lookup_fingerprint(fp[0], fp[1], config['musicdns.key'])
        except IOError, e:
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

