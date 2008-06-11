"""
Justin Tulloss

A simple library that takes a fingerprint and finds a puid.
"""

MD_HOST = 'ofa.musicdns.org'
MD_KEY = 'ffa7339e1b6bb1d26593776b4257fce1'
MD_PORT = 80
MD_REQ = '/ofa/1/track'

from xml.etree import cElementTree as ElementTree

def lookup_fingerprint(fingerprint, duration, **tags):
    """
    Looks up a MusicIP PUID based on the raw fingerprint, duration, and tagging
    data
    """
    url = 'http://%s:%d%s' % (MD_HOST, MD_PORT, req)
    postargs = dict(
        # Identification.
        cid = MD_KEY,
        cvr = "harmonize.fm/alpha1",
        
        # The given fingerprint.
        fpt=fingerprint,

        # These are required by the license agreement, to help fill out the
        # MusicDNS database.
        art=opt.pop('artist', ''),
        ttl=opt.pop('title', ''),
        alb=opt.pop('album', ''),
        tnm=opt.pop('tracknumer', ''),
        gnr=opt.pop('genre', ''),
        yrr=opt.pop('date', ''),
        brt=opt.pop('bitrate', ''),
        fmt=opt.pop('format', ''),
        dur=str(duration),

        # Return the metadata?
        rmd='0',
    )

    data = urllib.urlencode(postargs)
    response = urllib.urlopen(url, data)

    presp = ElementTree.parse(response)
    el = presp.find('//puid')

    if el is not None:
        return el.attrib['id']

    return None
