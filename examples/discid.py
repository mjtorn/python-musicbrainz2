#! /usr/bin/env python
import sys
from musicbrainz2.disc import readDisc, getSubmissionUrl, DiscError

try:
	disc = readDisc()
except DiscError, e:
	print "DiscID calculation failed:", str(e)
	sys.exit(1)

print 'DiscID      :', disc.getId()
print 'First Track :', disc.getFirstTrackNum()
print 'Last Track  :', disc.getLastTrackNum()
print 'Length      :', disc.getSectors(), 'sectors'

i = disc.getFirstTrackNum()
for (offset, length) in disc.getTracks():
	print "Track %-2d    : %8d %8d" % (i, offset, length)
	i += 1

print 'Submit via  :', getSubmissionUrl(disc)

# EOF
