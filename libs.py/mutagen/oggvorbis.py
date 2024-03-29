# Ogg Vorbis support.
#
# Copyright 2006 Joe Wreschnig <piman@sacredchao.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# $Id: oggvorbis.py 4153 2007-08-05 07:07:49Z piman $

"""Read and write Ogg Vorbis comments.

This module handles Vorbis files wrapped in an Ogg bitstream. The
first Vorbis stream found is used.

Read more about Ogg Vorbis at http://vorbis.com/. This module is based
on the specification at http://www.xiph.org/vorbis/doc/Vorbis_I_spec.html.
"""

__all__ = ["OggVorbis", "Open", "delete"]

import struct

from mutagen._vorbis import VCommentDict
from mutagen.ogg import OggPage, OggFileType, error as OggError

class error(OggError): pass
class OggVorbisHeaderError(error): pass

class OggVorbisInfo(object):
    """Ogg Vorbis stream information.

    Attributes:
    length - file length in seconds, as a float
    bitrate - nominal ('average') bitrate in bits per second, as an int
    """

    length = 0

    def __init__(self, fileobj):
        page = OggPage(fileobj)
        while not page.packets[0].startswith("\x01vorbis"):
            page = OggPage(fileobj)
        if not page.first:
            raise OggVorbisHeaderError(
                "page has ID header, but doesn't start a stream")
        (self.channels, self.sample_rate, max_bitrate, nominal_bitrate,
         min_bitrate) = struct.unpack("<B4I", page.packets[0][11:28])
        self.serial = page.serial

        if nominal_bitrate == 0:
            self.bitrate = (max_bitrate + min_bitrate) // 2
        elif max_bitrate and max_bitrate < nominal_bitrate:
            # If the max bitrate is less than the nominal, we know
            # the nominal is wrong.
            self.bitrate = max_bitrate
        elif min_bitrate > nominal_bitrate:
            self.bitrate = min_bitrate
        else:
            self.bitrate = nominal_bitrate

    def pprint(self):
        return "Ogg Vorbis, %.2f seconds, %d bps" % (self.length, self.bitrate)

class OggVCommentDict(VCommentDict):
    """Vorbis comments embedded in an Ogg bitstream."""

    def __init__(self, fileobj, info):
        pages = []
        complete = False
        while not complete:
            page = OggPage(fileobj)
            if page.serial == info.serial:
                pages.append(page)
                complete = page.complete or (len(page.packets) > 1)
        data = OggPage.to_packets(pages)[0][7:] # Strip off "\x03vorbis".
        super(OggVCommentDict, self).__init__(data)

    def _inject(self, fileobj):
        """Write tag data into the Vorbis comment packet/page."""

        # Find the old pages in the file; we'll need to remove them,
        # plus grab any stray setup packet data out of them.
        fileobj.seek(0)
        page = OggPage(fileobj)
        while not page.packets[0].startswith("\x03vorbis"):
            page = OggPage(fileobj)

        old_pages = [page]
        while not (old_pages[-1].complete or len(old_pages[-1].packets) > 1):
            page = OggPage(fileobj)
            if page.serial == old_pages[0].serial:
                old_pages.append(page)

        packets = OggPage.to_packets(old_pages, strict=False)

        # Set the new comment packet.
        packets[0] = "\x03vorbis" + self.write()

        new_pages = OggPage.from_packets(packets, old_pages[0].sequence)
        OggPage.replace(fileobj, old_pages, new_pages)

class OggVorbis(OggFileType):
    """An Ogg Vorbis file."""

    _Info = OggVorbisInfo
    _Tags = OggVCommentDict
    _Error = OggVorbisHeaderError
    _mimes = ["audio/vorbis", "audio/x-vorbis"]

    def score(filename, fileobj, header):
        return (header.startswith("OggS") * ("\x01vorbis" in header))
    score = staticmethod(score)

Open = OggVorbis

def delete(filename):
    """Remove tags from a file."""
    OggVorbis(filename).delete()
