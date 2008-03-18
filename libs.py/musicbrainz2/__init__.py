"""A collection of classes for MusicBrainz.

To get started quickly, have a look at L{webservice.Query} and the examples
there. The source distribution also contains example code you might find
interesting.

This package contains the following modules:

 1. L{model}: The MusicBrainz domain model, containing classes like
    L{Artist <model.Artist>}, L{Release <model.Release>}, or
    L{Track <model.Track>}

 2. L{webservice}: An interface to the MusicBrainz XML web service.

 3. L{wsxml}: A parser for the web service XML format (MMD).

 4. L{disc}: Functions for creating and submitting DiscIDs.

 5. L{utils}: Utilities for working with URIs and other commonly needed tools.

@author: Matthias Friedrich <matt@mafr.de>
"""
__revision__ = '$Id: __init__.py 9317 2007-08-11 07:42:59Z matt $'
__version__ = '0.5.0'

# EOF
