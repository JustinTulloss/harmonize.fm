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
            ['genpuid', config['musicdns.key'], '-xml', file.get('fname')],
            stdout=subprocess.PIPE
        )
        
        out = ElementTree.fromstring(gp.stdout.read())
        track = out.find('track')
        file['puid'] = track.get('puid') #This is just blank if no PUID

        return file

