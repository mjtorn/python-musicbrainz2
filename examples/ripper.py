#! /usr/bin/env python
import sys
import logging
import musicbrainz2.disc as mbdisc
import musicbrainz2.webservice as mbws

# Activate logging.
#
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# Setup a Query object.
#
service = mbws.WebService(host='test.musicbrainz.org')
query = mbws.Query(service)

# Read the disc in the drive
#
try:
	disc = mbdisc.readDisc()
	#disc.setId('YipB1z_otuvvPZBCi3yR0pcsUi0-') # FIXME: just for testing
except mbdisc.DiscError, e:
	print "Error:", e
	sys.exit(1)

# Query for all discs matching the given DiscID.
#
try:
	filter = mbws.ReleaseFilter(discId=disc.getId())
	releases = query.getReleases(filter)
except mbws.WebServiceError, e:
	print "Error:", e
	sys.exit(2)

# No disc matching this DiscID has been found.
#
if len(releases) == 0:
	print "Disc is not yet in the MusicBrainz database."
	print "Consider adding it via", mbdisc.getSubmissionUrl(disc)
	sys.exit(0)

# Select one of the returned releases. Usually the user should be asked.
#
selectedRelease = releases[0]


# The returned release object only contains title and artist, but no tracks.
# Query the web service once again to get all data we need.
#
try:
	inc = mbws.ReleaseIncludes(artist=True, tracks=True, releaseEvents=True)
	release = query.getReleaseById(selectedRelease.getId(), inc)
except mbws.WebServiceError, e:
	print "Error:", e
	sys.exit(2)


# Now display the returned data.
#
artist = release.getArtist()
isSingleArtist = release.isSingleArtistRelease()

print "%s - %s" % (artist.getUniqueName(), release.getTitle())

i = 1
for t in release.getTracks():
	if isSingleArtist:
		title = t.getTitle()
	else:
		title = t.getArtist().getName() + ' - ' +  t.getTitle()

	(minutes, seconds) = t.getDurationSplit()
	print " %2d. %s (%d:%02d)" % (i, title, minutes, seconds)
	i+=1


# Now actually rip the CD :-)
#

# EOF
