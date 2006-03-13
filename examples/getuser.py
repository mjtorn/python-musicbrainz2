#! /usr/bin/env python
import sys
import logging
import getpass
from musicbrainz2.webservice import WebService, WebServiceError, Query

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


user = raw_input('User name: ')
passwd = getpass.getpass('Password: ')

try:
	ws = WebService(host='musicbrainz.org', port=80,
		username=user, password=passwd)
	q = Query(ws)

	user = q.getUserByName(user)

except WebServiceError, e:
	print 'Error:', e
	sys.exit(1)


print 'Name            :', user.getName()
print 'ShowNag         :', user.getShowNag()
print 'Types           :', ' '.join(user.getTypes())

# EOF
