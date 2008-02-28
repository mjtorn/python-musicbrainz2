#! /usr/bin/env python
#
# This queries the tags a user has applied to an entity and submits a changed
# list of tags to the MusicBrainz server.
#
# Usage:
#    python tag.py
#
# $Id$
#
import sys
import logging
import musicbrainz2.webservice as mbws
from musicbrainz2.model import Tag
from musicbrainz2.utils import extractUuid

MB_HOST = 'test.musicbrainz.org'

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# Get the username and password
print 'Username: ',
username = sys.stdin.readline().strip()
print 'Password: ',
password = sys.stdin.readline().strip()

# Ask for an entity type to tag.
print 'Entity type to tag (artist, release, track or label): ',
entity = sys.stdin.readline().strip()

# Ask for a MBID to tag.
print 'Enter a MBID: ',
id_ = sys.stdin.readline().strip()
mbid = extractUuid(id_)

# Set the authentication for the webservice.
service = mbws.WebService(host=MB_HOST, username=username, password=password)

# Create a new Query object which will provide
# us an interface to the MusicBrainz web service.
query = mbws.Query(service)

# Read and print the current tags for the given MBID
tags = query.getUserTags(entity, mbid)
print
print 'Current tags: '
print ', '.join([tag.value for tag in tags])

# Ask the user for new tags and submit them
print 'Enter new tags: '
tag_str = sys.stdin.readline().strip()
new_tags = [Tag(tag) for tag in tag_str.split(',')]
query.submitUserTags('artist', mbid, new_tags)

print 'Tags applied'
