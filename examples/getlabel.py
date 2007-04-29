#! /usr/bin/env python
#
# Retrieve a label by ID.
#
# Usage:
#	python getlabel.py label-id
#
# $Id$
#
import sys
import logging
import musicbrainz2.webservice as ws
import musicbrainz2.model as m

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


if len(sys.argv) < 2:
	print "Usage: getlabel.py label-id"
	sys.exit(1)

q = ws.Query()

try:
	# The result should include all official albums.
	#
	#inc = ws.ArtistIncludes(
	#	releases=(m.Release.TYPE_OFFICIAL, m.Release.TYPE_ALBUM))
	label = q.getLabelById(sys.argv[1])
except ws.WebServiceError, e:
	print 'Error:', e
	sys.exit(1)


print "Id         :", label.id
print "Name       :", label.name
print "SortName   :", label.sortName
print "UniqueName :", label.getUniqueName()
print "Type       :", label.type
print "BeginDate  :", label.beginDate
print "EndDate    :", label.endDate
print "Country    :", label.country
print "Label-Code :", label.code
print

# EOF
