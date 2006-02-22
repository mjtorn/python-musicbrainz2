Python Bindings for the MusicBrainz XML Web Service
---------------------------------------------------

NOTE: This is an alpha release. Interfaces may change in case serious
      issues are found.

This python package contains various modules for accessing the MusicBrainz
web service, as well as parsing the MusicBrainz Metadata XML (MMD), or
calculating DiscIDs from Audio CDs.

Except for the DiscID generation, everything should work with standard
python 2.3 or later. However, for DiscID calculation, the MusicBrainz client
library (libmusicbrainz) and the ctypes package are required. See the
installation instructions for details.

To get started quickly have a look at the examples directory which
contains various sample scripts. API documentation can be generated
using epydoc (http://epydoc.sourceforge.net).

Please report all bugs you find via the MusicBrainz bug tracker:

	http://musicbrainz.org/bugs

Questions about this package may be posted to the MusicBrainz
development mailing list (mb-devel):

	http://musicbrainz.org/list.html

--
$Id$
