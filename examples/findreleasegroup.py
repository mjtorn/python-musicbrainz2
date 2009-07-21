#! /usr/bin/env python
#
# Search for a release group by name.
#
# Usage:
#	python findreleasegroup.py 'album name/Lucene query'
#
# Examples:
#	findreleasegroup.py "Signal morning"
#	findreleasegroup.py '"Gimme Fiction" AND artist:"Spoon"'
#	findreleasegroup.py '"Skylarking" AND type:"Album"'
#
import sys
import logging
from musicbrainz2.webservice import Query, ReleaseGroupFilter, WebServiceError

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
	

if len(sys.argv) < 2:
	print "Usage: findreleasegroup.py 'release group name/Lucene query'"
	sys.exit(1)

q = Query()

try:
	# Search for all release groups matching the given query. Limit the results
	# to the 5 best matches. The offset parameter could be used to page
	# through the results.
	#
	f = ReleaseGroupFilter(query=sys.argv[1], limit=5)
	results = q.getReleaseGroups(f)
except WebServiceError, e:
	print 'Error:', e
	sys.exit(1)


# No error occurred, so display the results of the search. It consists of
# ReleaseGroupResult objects, where each contains an artist.
#
for result in results:
	releaseGroup = result.releaseGroup
	print "Score\t\t :", result.score
	print "Id        :", releaseGroup.id
	print "Name      :", releaseGroup.title
	print "Artist    :", releaseGroup.artist.name
	print "Type      :", releaseGroup.type
	print

#
# Now that you have release group IDs, you can request a release group in more detail, for
# example to display all official releases in that group. See the 'getreleasegroup.py'
# example on how achieve that.
#

# EOF
