#! /usr/bin/env python
#
# Retrieve a release group by ID and display it.
#
# Usage:
#	python getreleasegroup.py releasegroup-id
#
# Interesting release group IDs for testing:
# http://musicbrainz.org/release-group/e49e2f8a-94c0-3dcf-8ce6-9bc52a1a7867
# http://musicbrainz.org/release-group/c7a0fc4d-b6a0-3a43-9e25-4052e4fe33b2
# http://musicbrainz.org/release-group/055be730-dcad-31bf-b550-45ba9c202aa3
# http://musicbrainz.org/release-group/963eac15-e3da-3a92-aa5c-2ec23bfb6ec2
#
#
import sys
import logging
import musicbrainz2.webservice as ws
import musicbrainz2.utils as u

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


if len(sys.argv) < 2:
	print "Usage: getreleasegroup.py releasegroup-id"
	sys.exit(1)

q = ws.Query()

try:
	# Additionally to the release itself, we want the server to include
	# the release's artist, all release events, associated discs and
	# the track list.
	#
	inc = ws.ReleaseGroupIncludes(artist=True, releases=True, tags=False)
	releaseGroup = q.getReleaseGroupById(sys.argv[1], inc)
except ws.WebServiceError, e:
	print 'Error:', e
	sys.exit(1)


print "Id          :", releaseGroup.id
print "Title       :", releaseGroup.title
print "Type        :", releaseGroup.type


# Print the main artist of this release group.
#
if releaseGroup.artist:
	print
	print "Artist:"
	print "  Id        :", releaseGroup.artist.id
	print "  Name      :", releaseGroup.artist.name
	print "  SortName  :", releaseGroup.artist.sortName


# Show the releases contained by this release group.
#
for release in releaseGroup.releases:
	print
	print "Release:"
	print "  Id        :", release.id
	print "  Title     :", release.title
	print "  Types     :", release.types

# EOF
