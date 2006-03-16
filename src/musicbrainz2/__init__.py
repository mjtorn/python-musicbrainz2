"""A collection of classes for MusicBrainz.

This package contains the following modules:

 1. L{model}: The MusicBrainz domain model, containing classes like
    L{Artist <model.Artist>}, L{Release <model.Release>}, or
    L{Track <model.Track>}

 2. L{webservice}: An interface to the MusicBrainz XML web service.

 3. L{wsxml}: A parser for the web service XML format.

To get started quickly, have a look at L{webservice.Query} and the examples
there. The source distribution also contains example code you might find
interesting.

@author: Matthias Friedrich <matt@mafr.de>
"""
__revision__ = '$Id$'
__version__ = '0.2.1'

# EOF
