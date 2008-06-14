import logging
import os
import subprocess
from baseaction import BaseAction
from fileprocess.processingthread import na
from fileprocess.configuration import config
import fileprocess
from xml.etree import cElementTree as ElementTree

log = logging.getLogger(__name__)

class PuidGenerator(BaseAction):
    def process(self, file):
        if file.has_key('puid'):
            if file['puid'] != None:
                return file

        if not file.has_key('fname'):
            return file

        if not os.path.exists(file.get('fname')):
            return file

        gp = subprocess.Popen(
            ['genpuid', config['musicdns.key'], '-xml', 
            os.path.abspath(file['fname'])],
            stdout=subprocess.PIPE
        )
        
        gp.wait()
        std = gp.stdout.read()
        try:
            out = ElementTree.fromstring(std)
            track = out.find('track')
            if track != None:
                file['puid'] = track.get('puid') #This is just blank if no PUID
        except SyntaxError, e:
            log.info("Could not parse %s: %s", std, e)

        return file

