#! /usr/bin/env python
import sys
import logging
from musicbrainz2.webservice import WebService, Query, WebServiceError,\
	ReleaseIncludes

logging.basicConfig(
        level=logging.DEBUG,
	format='%(levelname)-8s: %(message)s'
)


if len(sys.argv) < 2:
	print "Usage: getrelease.py releaseId"
	sys.exit(1)

ws = WebService(host='test.musicbrainz.org', port=80)
q = Query(ws)

try:
	inc = ReleaseIncludes(artist=True, releaseEvents=True,
		discs=True, tracks=True)
	release = q.getReleaseById(sys.argv[1], inc)
except WebServiceError, e:
	print 'Error:', e
	sys.exit(1)


print "Id          :", release.getId()
print "Title       :", release.getTitle()
print "ASIN        :", release.getAsin()
print "Lang/Script :", release.getTextLanguage(), '/', release.getTextScript()


artist = release.getArtist()

if artist:
	print
	print "Artist:"
	print "  Id        :", artist.getId()
	print "  Name      :", artist.getName()
	print "  SortName  :", artist.getSortName()


if len(release.getReleaseEvents()) > 0:
	print
	print "Released:"

for event in release.getReleaseEvents():
	print "  %s %s" % (event.getCountryId(), event.getDate())


if len(release.getDiscs()) > 0:
	print
	print "Discs:"

for disc in release.getDiscs():
	print "  DiscId: %s (%d sectors)" % (disc.getId(), disc.getSectors())


if len(release.getTracks()) > 0:
	print
	print "Tracks:"

for track in release.getTracks():
	print "  Id        :", track.getId()
	print "  Title     :", track.getTitle()
	print "  Duration  :", track.getDuration()
	print

# EOF
