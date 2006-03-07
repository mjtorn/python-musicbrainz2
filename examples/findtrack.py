#! /usr/bin/env python
import sys
import logging
from musicbrainz2.webservice import Query, TrackFilter, WebServiceError

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
	

if len(sys.argv) < 2:
	print "Usage: findartist.py 'track name' ['artist name']"
	sys.exit(1)

if len(sys.argv) > 2:
	artistName = sys.argv[2]
else:
	artistName = None

q = Query()

try:
	f = TrackFilter(title=sys.argv[1], artistName=artistName)
	tracks = q.getTracks(f)
except WebServiceError, e:
	print 'Error:', e
	sys.exit(1)


for track in tracks:
	print "Id        :", track.getId()
	print "Name      :", track.getTitle()
	print "Artist    :", track.getArtist().getUniqueName()
	print

