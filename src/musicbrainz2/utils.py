"""Various utilities to simplify common tasks.

This module contains helper functions to make common tasks easier.

@author: Matthias Friedrich <matt@mafr.de>
"""
__revision__ = '$Id$'

import re
import urlparse

__all__ = [ 'extractUuid', 'extractFragment' ]


def extractUuid(uriStr, resType=None):
	"""Extract the UUID part from a MusicBrainz identifier.

	This function takes a MusicBrainz ID (an absolute URI) as the input
	and returns the UUID part of the URI, thus turning it into a relative
	URI. If C{uriStr} is None or a relative URI, then it is returned
	unchanged.

	The C{resType} parameter can be used for error checking. Set it to
	'artist', 'release', or 'track' to make sure C{uriStr} is a
	syntactically valid MusicBrainz identifier of the given resource
	type. If it isn't, a C{ValueError} exception is raised.
	This error checking only works if C{uriStr} is an absolute URI, of
	course.

	Example:

	>>> from musicbrainz2.utils import extractUuid
	>>>  extractUuid('http://musicbrainz.org/artist/c0b2500e-0cef-4130-869d-732b23ed9df5', 'artist')
	'c0b2500e-0cef-4130-869d-732b23ed9df5'
	>>>

	@param uriStr: a string containing a MusicBrainz ID (an URI), or None
	@param resType: a string containing a resource type

	@return: a string containing a relative URI, or None

	@raise ValueError: the given URI is no valid MusicBrainz ID
	"""
	if uriStr is None:
		return None

	(scheme, netloc, path) = urlparse.urlparse(uriStr)[:3]

	if scheme == '':
		return uriStr	# no URI, probably already the UUID

	if scheme != 'http' or netloc != 'musicbrainz.org':
		raise ValueError('%s is no MB ID.' % uriStr)

	m = re.match('^/(artist|release|track)/([^/]*)$', path)

	if m:
		if resType is None:
			return m.group(2)
		else:
			if m.group(1) == resType:
				return m.group(2)
			else:
				raise ValueError('expected "%s" Id' % resType)
	else:
		raise ValueError('%s is no valid MB ID.' % uriStr)


def extractFragment(uriStr, uriPrefix=None):
	"""Extract the fragment part from a URI.

	If C{uriStr} is None or no absolute URI, then it is returned unchanged.

	The C{uriPrefix} parameter can be used for error checking. If C{uriStr}
	is an absolute URI, then the function checks if it starts with
	C{uriPrefix}. If it doesn't, a C{ValueError} exception is raised.

	@param uriStr: a string containing an absolute URI
	@param uriPrefix: a string containing an URI prefix

	@return: a string containing the fragment, or None

	@raise ValueError: the given URI doesn't start with C{uriPrefix}
	"""
	if uriStr is None:
		return None

	(scheme, netloc, path, params, query, frag) = urlparse.urlparse(uriStr)
	if scheme == '':
		return uriStr # this is no URI

	if uriPrefix is None or uriStr.startswith(uriPrefix):
		return frag
	else:
		raise ValueError("prefix doesn't match URI %s" % uriStr)


# EOF
