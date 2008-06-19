"""
Justin Tulloss

A simple library that takes a fingerprint and finds a puid.

Inspired by pyofa: http://furius.ca/pyofa/
"""

from xml.etree import cElementTree as ElementTree
import urllib

MD_HOST = 'ofa.musicdns.org'
MD_KEY = 'ffa7339e1b6bb1d26593776b4257fce1'
MD_PORT = 80
MD_REQ = '/ofa/1/track'
MD_URL = 'http://%s:%d%s' % (MD_HOST, MD_PORT, MD_REQ)
MD_NAMESPACE = 'http://musicbrainz.org/ns/mmd-1.0#'

def lookup_fingerprint(fingerprint, **tags):
    """
    Looks up a MusicIP PUID based on the raw fingerprint, duration, and tagging
    data
    """
    postargs = dict(
        # Identification.
        cid = MD_KEY,
        cvr = "harmonize.fm/alpha1",
        
        # The given fingerprint.
        fpt=fingerprint,

        # These are required by the license agreement, to help fill out the
        # MusicDNS database.
        art=tags.get('artist', ''),
        ttl=tags.get('title', ''),
        alb=tags.get('album', ''),
        tnm=tags.get('tracknumer', ''),
        gnr=tags.get('genre', ''),
        yrr=tags.get('date', ''),
        brt=tags.get('bitrate', ''),
        fmt=tags.get('format', ''),
        dur=str(int(float(tags.get('duration', '')))),

        # Return the metadata?
        rmd='0',
    )

    data = urllib.urlencode(postargs)
    response = urllib.urlopen(MD_URL, data)

    presp = ElementTree.parse(response)
    el = presp.find('{%s}puid'%MD_NAMESPACE)
    raise RuntimeError()

    if el is not None:
        return el.attrib['id']

    return None
