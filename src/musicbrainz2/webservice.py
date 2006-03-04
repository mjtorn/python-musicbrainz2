"""Classes for interacting with the MusicBrainz XML web service.

The L{WebService} class talks to a server implementing the MusicBrainz XML
web service. It mainly handles URL generation and network I/O. Use this
if maximum control is needed.

The L{Query} class provides a convenient interface to the most commonly
used features of the web service. By default it uses L{WebService} to
retrieve data and the L{XML parser <musicbrainz2.wsxml>} to parse the
responses. The results are object trees using the L{MusicBrainz domain
model <musicbrainz2.model>}.

@author: Matthias Friedrich <matt@mafr.de>
"""
__revision__ = '$Id$'

import re
import httplib
import urllib
import urllib2
import urlparse
import logging
import os.path
from StringIO import StringIO
import musicbrainz2
from musicbrainz2.model import Artist, Release, Track
from musicbrainz2.wsxml import MbXmlParser, ParseError


class IWebService:
	"""An interface all concrete web service classes have to implement.

	All web service classes have to implement this and follow the
	method specifications.
	"""

	def get(self, entity, id_, include, filter, version):
		"""Query the web service.

		Using this method, you can either get a resource by id (using
		the C{id_} parameter, or perform a query on all resources of
		a type.

		The C{filter} and the C{id_} parameter exclude each other. If
		you are using a filter, you may not set C{id_} and vice versa.

		Returns a file-like object containing the result or raises a
		L{WebServiceError} or one of its subclasses in case of an
		error. Which one is used depends on the implementing class.

		@param entity: a string containing the entity's name
		@param id_: a string containing a UUID, or the empty string
		@param include: a tuple containing values for the 'inc' parameter
		@param filter: parameters, depending on the entity
		@param version: a string containing the web service version to use

		@return: a file-like object

		@raise WebServiceError: in case of errors
		"""
		raise NotImplementedError()


	def post(self, entity, id_, data, version):
		"""Submit data to the web service.

		@param entity: a string containing the entity's name
		@param id_: a string containing a UUID, or the empty string
		@param data: A string containing the data to post
		@param version: a string containing the web service version to use

		@raise WebServiceError: in case of errors
		"""
		raise NotImplementedError()


class WebServiceError(Exception):
	"""A web service error has occurred.

	This is the base class for several other web service related
	exceptions.
	"""

	def __init__(self, msg='Webservice Error', reason=None):
		"""Constructor.

		Set C{msg} to an error message which explains why this
		exception was raised. The C{reason} parameter should be the
		original exception which caused this L{WebService} exception
		to be raised. If given, it has to be an instance of
		C{Exception} or one of its child classes.

		@param msg: a string containing an error message
		@param reason: another exception instance, or None
		"""
		Exception.__init__(self)
		self.msg = msg
		self.reason = reason

	def __str__(self):
		"""Makes this class printable.

		@return: a string containing an error message
		"""
		return self.msg


class ConnectionError(WebServiceError):
	"""Getting a server connection failed.

	This exception is mostly used if the client couldn't connect to
	the server because of an invalid host name or port. It doesn't
	make sense if the web service in question doesn't use the network.
	"""
	pass


class RequestError(WebServiceError):
	"""An invalid request was made.

	This exception is raised if the client made an invalid request.
	That could be syntactically invalid identifiers or unknown or
	invalid parameter values.
	"""
	pass


class ResourceNotFoundError(WebServiceError):
	"""No resource with the given ID exists.

	This is usually a wrapper around IOError (which is superclass of
	HTTPError).
	"""
	pass


class AuthenticationError(WebServiceError):
	"""Authentication failed.

	This is thrown if user name, password or realm were invalid while
	trying to access a protected resource.
	"""
	pass


class ResponseError(WebServiceError):
	"""The returned resource was invalid.

	This may be due to a malformed XML document or if the requested
	data wasn't part of the response. It can only occur in case of
	bugs in the web service itself.
	"""
	pass


class WebService(IWebService):
	"""An interface to the MusicBrainz XML web service via HTTP.

	By default, this class uses the MusicBrainz server but may be
	configured for accessing other servers as well using the
	L{constructor <__init__>}. This implements L{IWebService}, so
	additional documentation on method parameters can be found there.
	"""

	def __init__(self, host='musicbrainz.org', port=80, pathPrefix='/ws',
			username=None, password=None, realm='musicbrainz.org',
			opener=None):
		"""Constructor.

		This can be used without parameters. In this case, the
		MusicBrainz server will be used.

		@param host: a string containing a host name
		@param port: an integer containing a port number
		@param pathPrefix: a string prepended to all URLs
		@param username: a string containing a MusicBrainz user name
		@param password: a string containing the user's password
		@param realm: a string containing the realm used for authentication
		@param opener: an C{urllib2.OpenerDirector} object used for queries
		"""
		self.host = host
		self.port = port
		self.username = username
		self.password = password
		self.realm = realm
		self.pathPrefix = pathPrefix
		self.log = logging.getLogger(str(self.__class__))

		if opener is None:
			self.opener = urllib2.build_opener()
		else:
			self.opener = opener

		authHandler = urllib2.HTTPDigestAuthHandler()
		authHandler.add_password(self.realm, self.host,
			self.username, self.password)
		self.opener.add_handler(authHandler)


	def _makeUrl(self, entity, id_, include=( ), filter={ },
			version='1', type_='xml'):
		params = dict(filter)
		if type_ is not None:
			params['type'] = type_
		if len(include) > 0:
			params['inc'] = ' '.join(include)

		netloc = self.host
		if self.port != 80:
			netloc += ':' + str(self.port)
		path = '/'.join((self.pathPrefix, version, entity, id_))

		query = urllib.urlencode(params)

		url = urlparse.urlunparse(('http', netloc, path, '', query,''))

		return url


	def get(self, entity, id_, include=( ), filter={ }, version='1'):
		"""Query the web service via HTTP-GET.

		Returns a file-like object containing the result or raises a
		L{WebServiceError}. Conditions leading to errors may be
		invalid entities, IDs, C{include} or C{filter} parameters
		and unsupported version numbers.

		@raise ConnectionError: couldn't connect to server
		@raise RequestError: invalid IDs or parameters
		@raise AuthenticationError: invalid user name and/or password
		@raise ResourceNotFoundError: resource doesn't exist

		@see: L{IWebService.get}
		"""
		url = self._makeUrl(entity, id_, include, filter, version)

		self.log.debug('GET ' + url)

		try:
			return self.opener.open(url)
		except urllib2.HTTPError, e:
			self.log.debug("GET failed: " + str(e))
			if e.code == httplib.BAD_REQUEST:
				raise RequestError(str(e), e)
			elif e.code == httplib.UNAUTHORIZED:
				raise AuthenticationError(str(e), e)
			elif e.code == httplib.NOT_FOUND:
				raise ResourceNotFoundError(str(e), e)
			else:
				raise WebServiceError(str(e), e)
		except urllib2.URLError, e:
			self.log.debug("GET failed: " + str(e))
			raise ConnectionError(str(e), e)


	def post(self, entity, id_, data, version='1'):
		"""Send data to the web service via HTTP-POST.

		Note that this may require authentication. You can set
		user name, password and realm in the L{constructor <__init__>}.

		@raise ConnectionError: couldn't connect to server
		@raise RequestError: invalid IDs or parameters
		@raise AuthenticationError: invalid user name and/or password
		@raise ResourceNotFoundError: resource doesn't exist

		@see: L{IWebService.post}
		"""
		url = self._makeUrl(entity, id_, version=version, type_=None)

		userAgent = 'python-musicbrainz/' + musicbrainz2.__version__

		try:
			req = urllib2.Request(url)
			req.add_header('User-Agent', userAgent)

			self.log.debug('POST ' + url)
			self.log.debug('POST-BODY: ' + data)
			self.opener.open(req, data)
		except urllib2.HTTPError, e:
			self.log.debug("POST failed: " + str(e))
			if e.code == httplib.BAD_REQUEST:
				raise RequestError(str(e), e)
			elif e.code == httplib.UNAUTHORIZED:
				raise AuthenticationError(str(e), e)
			elif e.code == httplib.NOT_FOUND:
				raise ResourceNotFoundError(str(e), e)
			else:
				raise WebServiceError(str(e), e)
		except urllib2.URLError, e:
			self.log.debug("POST failed: " + str(e))
			raise ConnectionError(str(e), e)


class IFilter:
	"""A filter for collections.

	This is the interface all filters have to implement.
	"""
	def createParameters(self):
		"""Create a list of query parameters.

		This method creates a list of (C{parameter}, C{value}) tuples,
		based on the contents of the implementing subclass.
		C{parameter} is a string containing a parameter name
		and C{value} an arbitrary string. No escaping of those strings
		is required. 

		@return: a sequence of (key, value) pairs
		"""
		raise NotImplementedError()


class ArtistFilter(IFilter):
	"""A filter for the artist collection."""

	def __init__(self, name=None, limit=None):
		"""Constructor.

		@param name: a string containing the artist's name
		@param limit: the maximum number of artists to return
		"""
		self.params = [
			('name', name),
			('limit', limit),
		]

	def createParameters(self):
		return filter(lambda x: x[1] is not None, self.params)


class ReleaseFilter(IFilter):
	"""A filter for the release collection."""

	def __init__(self, title=None, discId=None, releaseTypes=None,
			artistName=None, artistId=None, limit=None):
		"""Constructor.

		If C{discId} or C{artistId} are set, only releases matching
		those IDs are returned. The C{releaseTypes} parameter allows
		to limit the types of the releases returned. You can set it to
		('Album', 'Official'), for example, to only get officially 
		released albums. Note that those values are connected using
		the I{AND} operator. MusicBrainz' support is currently very
		limited, so 'Live' and 'Compilation' exclude each other (see
		U{the documentation on release attributes
		<http://wiki.musicbrainz.org/AlbumAttribute>} for more
		information and all valid values).

		If both the C{artistName} and the C{artistId} parameter are
		given, the server will ignore C{artistName}.

		@param title: a string containing the release's title
		@param discId: a string containing the DiscID
		@param releaseTypes: a sequence of strings with release types
		@param artistName: a string containing the artist's name
		@param artistId: a string containing the artist's ID
		@param limit: the maximum number of releases to return
		"""
		if releaseTypes is None or len(releaseTypes) == 0:
			releaseTypesStr = None
		else:
			releaseTypesStr = ' '.join(releaseTypes)

		self.params = [
			('title', title),
			('discid', discId),
			('release-type', releaseTypesStr),
			('artist', artistName),
			('artistid', artistId),
			('limit', limit),
		]

	def createParameters(self):
		return filter(lambda x: x[1] is not None, self.params)


class TrackFilter(IFilter):
	"""A filter for the track collection."""

	def __init__(self, title=None, artistName=None, artistId=None,
			releaseTitle=None, releaseId=None,
			duration=None, trmId=None, limit=None):
		"""Constructor.

		If C{artistId}, C{releaseId} or C{trmId} are set, only tracks
		matching those IDs are returned.

		The server will ignore C{artistName} and C{releaseTitle} if
		C{artistId} or ${releaseId} are set respectively.

		@param title: a string containing the track's title
		@param artistName: a string containing the artist's name
		@param artistId: a string containing the artist's ID
		@param releaseTitle: a string containing the release's title
		@param releaseId: a string containing the release's title
		@param duration: the track's length in milliseconds
		@param trmId: a string containing a TRM ID
		@param limit: the maximum number of releases to return
		"""
		self.params = [
			('title', title),
			('artist', artistName),
			('artistid', artistId),
			('release', releaseTitle),
			('releaseid', releaseId),
			('duration', duration),
			('trmid', trmId),
			('limit', limit),
		]

	def createParameters(self):
		return filter(lambda x: x[1] is not None, self.params)


class UserFilter(IFilter):
	"""A filter for the user collection."""

	def __init__(self, name=None):
		"""Constructor.

		@param name: a string containing a MusicBrainz user name
		"""
		self.name = name

	def createParameters(self):
		if self.name is not None:
			return [ ('name', self.name) ]
		else:
			return [ ]


class IIncludes:
	"""An interface implemented by include tag generators."""
	def createIncludeTags(self):
		raise NotImplementedError()


class ArtistIncludes(IIncludes):
	"""A specification on how much data to return with an artist.

	Example:

	>>> from musicbrainz2.model import Release
	>>> from musicbrainz2.webservice import ArtistIncludes
	>>> inc = ArtistIncludes(artistRelations=True, releaseRelations=True,
	... 		releases=(Release.TYPE_ALBUM, Release.TYPE_OFFICIAL))
	>>>

	The MusicBrainz server only supports some combinations of release
	types for the C{releases} and C{vaReleases} include tags. At the
	moment, not more than two release types should be selected, while
	one of them has to be C{Release.TYPE_OFFICIAL},
	C{Release.TYPE_PROMOTION} or C{Release.TYPE_BOOTLEG}.

	@note: Only one of C{releases} and C{vaReleases} may be given.
	"""
	def __init__(self, aliases=False, releases=(), vaReleases=(),
			artistRelations=False, releaseRelations=False,
			trackRelations=False, urlRelations=False):

		assert not isinstance(releases, basestring)
		assert not isinstance(vaReleases, basestring)
		assert len(releases) == 0 or len(vaReleases) == 0

		self.includes = {
			'aliases':		aliases,
			'artist-rels':		artistRelations,
			'release-rels':		releaseRelations,
			'track-rels':		trackRelations,
			'url-rels':		urlRelations,
		}

		for elem in releases:
			self.includes['sa-' + _extractFragment(elem)] = True

		for elem in vaReleases:
			self.includes['va-' + _extractFragment(elem)] = True

	def createIncludeTags(self):
		return _createIncludes(self.includes)


class ReleaseIncludes(IIncludes):
	"""A specification on how much data to return with a release."""
	def __init__(self, artist=False, counts=False, releaseEvents=False,
			discs=False, tracks=False,
			artistRelations=False, releaseRelations=False,
			trackRelations=False, urlRelations=False):
		self.includes = {
			'artist':		artist,
			'counts':		counts,
			'release-events':	releaseEvents,
			'discs':		discs,
			'tracks':		tracks,
			'artist-rels':		artistRelations,
			'release-rels':		releaseRelations,
			'track-rels':		trackRelations,
			'url-rels':		urlRelations,
		}

	def createIncludeTags(self):
		return _createIncludes(self.includes)


class TrackIncludes(IIncludes):
	"""A specification on how much data to return with a track."""
	def __init__(self, artist=False, releases=False, trmIds=False,
			artistRelations=False, releaseRelations=False,
			trackRelations=False, urlRelations=False):
		self.includes = {
			'artist':		artist,
			'releases':		releases,
			'trmids':		trmIds,
			'artist-rels':		artistRelations,
			'release-rels':		releaseRelations,
			'track-rels':		trackRelations,
			'url-rels':		urlRelations,
		}

	def createIncludeTags(self):
		return _createIncludes(self.includes)


class Query:
	"""A simple interface to the MusicBrainz web service.

	This is a facade which provides a simple interface to the MusicBrainz
	web service. It hides all the details like fetching data from a server,
	parsing the XML and creating an object tree. Using this class, you can
	request data by ID or search the I{collection} of all resources
	(artists, releases, or tracks) to retrieve those matching given
	criteria. This document contains examples to get you started.


	Working with Identifiers
	========================

	MusicBrainz uses absolute URIs as identifiers. For example, the artist
	'Tori Amos' is identified using the following URI::
		http://musicbrainz.org/artist/c0b2500e-0cef-4130-869d-732b23ed9df5

	In some situations it is obvious from the context what type of 
	resource an ID refers to. In these cases, abbreviated identifiers may
	be used, which are just the I{UUID} part of the URI. Thus the ID above
	may also be written like this::
		c0b2500e-0cef-4130-869d-732b23ed9df5

	All methods in this class which require IDs accept both the absolute
	URI and the abbreviated form (aka the relative URI).


	Creating a Query Object
	=======================

	In most cases, creating a L{Query} object is as simple as this:

	>>> import musicbrainz2.webservice as ws
	>>> q = ws.Query()
	>>>

	The instantiated object uses the standard L{WebService} class to
	access the MusicBrainz web service. If you want to use a different 
	server or you have to pass user name and password because one of
	your queries requires authentication, you have to create the
	L{WebService} object yourself and configure it appropriately.
	This example uses the MusicBrainz test server and also sets
	authentication data:

	>>> import musicbrainz2.webservice as ws
	>>> service = ws.WebService(host='test.musicbrainz.org',
	...				username='whatever', password='secret')
	>>> q = ws.Query(service)
	>>>


	Querying for Individual Resources
	=================================

	If the MusicBrainz ID of a resource is known, then the L{getArtistById},
	L{getReleaseById}, or L{getTrackById} method can be used to retrieve
	it. Example:

	>>> import musicbrainz2.webservice as ws
	>>> q = ws.Query()
	>>> artist = q.getArtistById('c0b2500e-0cef-4130-869d-732b23ed9df5')
	>>> print artist.getName()
	Tori Amos
	>>> print artist.getSortName()
	Amos, Tori
	>>> print artist.getType()
	http://musicbrainz.org/ns/mmd-1.0#Person
	>>>

	This returned just the basic artist data, however. To get more detail
	about a resource, the C{include} parameters may be used which expect
	an L{ArtistIncludes}, L{ReleaseIncludes}, or L{TrackIncludes}) object,
	depending on the resource type.

	To get data about a release which also includes the main artist
	and all tracks, for example, the following query can be used:

	>>> import musicbrainz2.webservice as ws
	>>> q = ws.Query()
	>>> releaseId = '33dbcf02-25b9-4a35-bdb7-729455f33ad7'
	>>> include = ws.ReleaseIncludes(artist=True, tracks=True)
	>>> release = q.getReleaseById(releaseId, include)
	>>> print release.getTitle()
	Tales of a Librarian
	>>> print release.getArtist().getName()
	Tori Amos
	>>> print release.getTracks()[0].getTitle()
	Precious Things
	>>>

	Note that the query gets more expensive for the server the more
	data you request, so please be nice.


	Searching in Collections
	========================

	Searching for resources matching given criteria works using the
	L{getArtists}, L{getReleases}, and L{getTracks} methods and their
	corresponding filter classes L{ArtistFilter}, L{ReleaseFilter},
	and L{TrackFilter}. This is an example to query for all releases
	matching a given DiscID:

	>>> import musicbrainz2.webservice as ws
	>>> q = ws.Query()
	>>> filter = ws.ReleaseFilter(discId='8jJklE258v6GofIqDIrE.c5ejBE-')
	>>> releases = q.getReleases(filter=filter)
	>>> print releases[0].getTitle()
	Under the Pink
	>>>

	All filters also support a C{limit} argument to limit the number of
	results returned.


	Error Handling
	==============

	All methods in this class raise a L{WebServiceError} exception in case
	of errors. Depending on the method, a subclass of L{WebServiceError} may
	be raised which allows an application to handle errors more precisely.
	The following example handles connection errors (invalid host name
	etc.) separately and all other web service errors in a combined
	catch clause:

	>>> try:
	...     artist = q.getArtistById('c0b2500e-0cef-4130-869d-732b23ed9df5')
	... except ws.ConnectionError, e:
	...     pass # implement your error handling here
	... except ws.WebServiceError, e:
	...     pass # catches all other web service errors
	... 
	>>>
	"""

	def __init__(self, ws=None, wsFactory=WebService, clientId=None):
		"""Constructor.

		The C{ws} parameter has to be a subclass of L{IWebService}.
		If it isn't given, the C{wsFactory} parameter is used to
		create an L{IWebService} subclass.

		If the constructor is called without arguments, an instance
		of L{WebService} is used, preconfigured to use the MusicBrainz
		server. This should be enough for most users.

		If you want to use queries which require authentication you
		have to pass a L{WebService} instance where user name and
		password have been set.

		The C{clientId} parameter is required for data submission.
		The format is C{'application-version'}, where C{application}
		is your application's name and C{version} is a version
		number which may not include a '-' character.

		@param ws: a subclass instance of L{IWebService}, or None
		@param wsFactory: a callable object which creates an object
		@param clientId: a string containing the application's ID
		"""
		if ws is None:
			self.ws = wsFactory()
		else:
			self.ws = ws

		self.clientId = clientId
		self.log = logging.getLogger(str(self.__class__))


	def getArtistById(self, id_, include=None):
		"""Returns an artist.

		If no artist with that ID can be found, C{include} contains
		invalid tags or there's a server problem, an exception is
		raised.

		@param id_: a string containing the artist's ID
		@param include: an L{ArtistIncludes} object, or None

		@return: an L{Artist <musicbrainz2.model.Artist>} object, or None

		@raise ConnectionError: couldn't connect to server
		@raise RequestError: invalid ID or include tags
		@raise ResourceNotFoundError: artist doesn't exist
		@raise ResponseError: server returned invalid data
		"""
		uuid = _extractUuid(id_, 'artist')
		result = self._getFromWebService('artist', uuid, include)
		artist = result.getArtist()
		if artist is not None:
			return artist
		else:
			raise ResponseError("server didn't return artist")


	def getArtists(self, filter):
		"""Returns artists matching given criteria.

		@param filter: an L{ArtistFilter} object

		@return: a list of L{musicbrainz2.model.Artist} objects

		@raise ConnectionError: couldn't connect to server
		@raise RequestError: invalid ID or include tags
		@raise ResponseError: server returned invalid data
		"""
		result = self._getFromWebService('artist', '', filter=filter)
		return result.getArtistList()


	def getReleaseById(self, id_, include=None):
		"""Returns a release.

		If no release with that ID can be found, C{include} contains
		invalid tags or there's a server problem, and exception is
		raised.

		@param id_: a string containing the release's ID
		@param include: a L{ReleaseIncludes} object, or None

		@return: a L{Release <musicbrainz2.model.Release>} object, or None

		@raise ConnectionError: couldn't connect to server
		@raise RequestError: invalid ID or include tags
		@raise ResourceNotFoundError: release doesn't exist
		@raise ResponseError: server returned invalid data
		"""
		uuid = _extractUuid(id_, 'release')
		result = self._getFromWebService('release', uuid, include)
		release = result.getRelease()
		if release is not None:
			return release
		else:
			raise ResponseError("server didn't return release")


	def getReleases(self, filter):
		"""Returns releases matching given criteria.

		@param filter: a L{ReleaseFilter} object

		@return: a list of L{musicbrainz2.model.Release} objects

		@raise ConnectionError: couldn't connect to server
		@raise RequestError: invalid ID or include tags
		@raise ResponseError: server returned invalid data
		"""
		result = self._getFromWebService('release', '', filter=filter)
		return result.getReleaseList()


	def getTrackById(self, id_, include=None):
		"""Returns a track.

		If no track with that ID can be found, C{include} contains
		invalid tags or there's a server problem, and exception is
		raised.

		@param id_: a string containing the track's ID
		@param include: a L{TrackIncludes} object, or None

		@return: a L{Track <musicbrainz2.model.Track>} object, or None

		@raise ConnectionError: couldn't connect to server
		@raise RequestError: invalid ID or include tags
		@raise ResourceNotFoundError: track doesn't exist
		@raise ResponseError: server returned invalid data
		"""
		uuid = _extractUuid(id_, 'track')
		result = self._getFromWebService('track', uuid, include)
		track = result.getTrack()
		if track is not None:
			return track
		else:
			raise ResponseError("server didn't return track")


	def getTracks(self, filter):
		"""Returns tracks matching given criteria.

		@param filter: a L{TrackFilter} object

		@return: a list of L{musicbrainz2.model.Track} objects

		@raise ConnectionError: couldn't connect to server
		@raise RequestError: invalid ID or include tags
		@raise ResponseError: server returned invalid data
		"""
		result = self._getFromWebService('track', '', filter=filter)
		return result.getTrackList()


	def getUserByName(self, name):
		"""Returns information about a MusicBrainz user.

		You can only request user data if you know the user name and
		password for that account. If username and/or password are
		incorrect, an L{AuthenticationError} is raised.

		See the example in L{Query} on how to supply user name and
		password.

		@param name: a string containing the user's name

		@return: a L{User <musicbrainz2.model.User>} object

		@raise ConnectionError: couldn't connect to server
		@raise RequestError: invalid ID or include tags
		@raise AuthenticationError: invalid user name and/or password
		@raise ResourceNotFoundError: track doesn't exist
		@raise ResponseError: server returned invalid data
		"""
		filter = UserFilter(name=name)
		result = self._getFromWebService('user', '', ( ), filter)

		if len(result.getUserList()) > 0:
			return result.getUserList()[0]
		else:
			raise ResponseError("response didn't contain user data")


	def _getFromWebService(self, entity, id_, include=None, filter=None):
		if filter is None:
			filterParams = [ ]
		else:
			filterParams = filter.createParameters()

		if include is None:
			includeParams = [ ]
		else:
			includeParams = include.createIncludeTags()

		stream = self.ws.get(entity, id_, includeParams, filterParams)
		try:
			parser = MbXmlParser()
			return parser.parse(stream)
		except ParseError, e:
			raise ResponseError(str(e), e)


	def submitTrms(self, tracks2trms):
		"""Submit track to TRM Id mappings.

		The C{tracks2trms} parameter has to be a dictionary, with the
		keys being MusicBrainz track IDs (either as absolute URIs or
		in their 36 character ASCII representation) and the values
		being TRM IDs (ASCII, 36 characters).

		Note that this method only works if a valid user name and
		password have been set. See the example in L{Query} on how
		to supply authentication data.

		@param tracks2trms: a dictionary mapping track IDs to TRM IDs

		@raise ConnectionError: couldn't connect to server
		@raise RequestError: invalid track- or TRM IDs
		@raise AuthenticationError: invalid user name and/or password
		"""
		assert self.clientId is not None, 'Please supply a client ID'
		params = [ ]
		params.append( ('client', self.clientId) )

		for (trackId, trmId) in tracks2trms.iteritems():
			trackId = _extractUuid(trackId, 'track')
			params.append( ('trm', trackId + ' ' + trmId) )

		encodedStr = urllib.urlencode(params, True)

		self.ws.post('track', '', encodedStr)



def _extractUuid(uriStr, resType=None):
	if uriStr is None:
		return None

	(scheme, netloc, path) = urlparse.urlparse(uriStr)[:3]

	if scheme == '':
		return uriStr	# no URI, probably already the UUID

	m = re.match('^/(artist|release|track)/(.*)$', path)

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


def _extractFragment(uriStr):
	(scheme, netloc, path, params, query, frag) = urlparse.urlparse(uriStr)
	if scheme == '':
		return uriStr # this is no uri
	else:
		return frag


def _createIncludes(tagMap):
	selected = filter(lambda x: x[1] == True, tagMap.items())
	return map(lambda x: x[0], selected)

# EOF
