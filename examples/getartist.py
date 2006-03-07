#! /usr/bin/env python
import sys
import logging
from musicbrainz2.webservice import WebService, Query, WebServiceError

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


if len(sys.argv) < 2:
	print "Usage: getartist.py artistId"
	sys.exit(1)

ws = WebService(host='test.musicbrainz.org', port=80)
q = Query(ws)

try:
	artist = q.getArtistById(sys.argv[1])
except WebServiceError, e:
	print 'Error:', e
	sys.exit(1)


print "Id        :", artist.getId()
print "Name      :", artist.getName()
print "SortName  :", artist.getSortName()
print "Type      :", artist.getType()
print "BeginDate :", artist.getBeginDate()
print "EndDate   :", artist.getEndDate()


if len(artist.getReleases()) > 0:
	print
	print "Releases:"

for release in artist.getReleases():
	print "Id          :", release.getId()
	print "Title       :", release.getTitle()
	print "ASIN        :", release.getAsin()
	print "Lang/Script :", release.getTextLanguage(), \
				'/', release.getTextScript()

# EOF
