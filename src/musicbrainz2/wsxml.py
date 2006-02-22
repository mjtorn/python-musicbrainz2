"""A parser for the Music Metadata XML Format (MMD).

This module contains L{MbXmlParser}, which parses the U{Music Metadata XML
Format (MMD) <http://musicbrainz.org/development/mmd/>} returned by the
MusicBrainz webservice. 

There are also DOM helper functions in this module used by the parser which
probably aren't useful to users.
"""
__revision__ = '$Id$'

import re
import logging
import urlparse
import xml.dom.minidom
from xml.parsers.expat import ExpatError
from xml.dom import DOMException
import musicbrainz2.model as model
from musicbrainz2.model import NS_MMD_1, NS_REL_1, NS_EXT_1


class DefaultFactory:
	"""A factory to instantiate classes from the domain model. 

	This factory may be used to create objects from L{musicbrainz2.model}.
	"""
	def newArtist(self): return model.Artist()
	def newRelease(self): return model.Release()
	def newTrack(self): return model.Track()
	def newRelation(self): return model.Relation()
	def newReleaseEvent(self): return model.ReleaseEvent()
	def newDisc(self): return model.Disc()
	def newArtistAlias(self): return model.ArtistAlias()
	def newUser(self): return model.User()


class ParseError(Exception):
	"""Exception to be thrown if a parse error occurs.

	The 'msg' attribute contains a printable error message, 'reason'
	is the lower level exception that was raised.
	"""

	def __init__(self, msg='Parse Error', reason=None):
		Exception.__init__(self)
		self.msg = msg
		self.reason = reason

	def __str__(self):
		return self.msg


class Metadata:
	"""Represents a parsed Music Metadata XML document."""

	def __init__(self):
		self.artist = None
		self.release = None
		self.track = None
		self.artistList = [ ]
		self.releaseList = [ ]
		self.trackList = [ ]
		self.userList = [ ]

	def getArtist(self):
		return self.artist

	def getRelease(self):
		return self.release

	def getTrack(self):
		return self.track

	def getArtistList(self):
		return self.artistList

	def getReleaseList(self):
		return self.releaseList

	def getTrackList(self):
		return self.trackList

	# MusicBrainz extension to the schema
	def getUserList(self):
		return self.userList


class MbXmlParser:
	"""A parser for the Music Metadata XML format.

	This parser supports all basic features and extensions defined by
	MusicBrainz, including unlimited document nesting. By default it
	reads an XML document from a file-like object (stream) and returns
	an object tree representing the document using classes from
	L{musicbrainz2.model}.

	The implementation tries to be as permissive as possible. Invalid
	contents are skipped, but documents have to be well-formed and using
	the correct namespace. In case of unrecoverable errors, a L{ParseError}
	exception is raised.

	@see: U{The Music Metadata XML Format
		<http://musicbrainz.org/development/mmd/>}
	"""

	def __init__(self, factory=DefaultFactory()):
		"""Constructor.

		The C{factory} parameter has be an instance of L{DefaultFactory}
		or a subclass of it. It is used by L{parse} to obtain objects
		from L{musicbrainz2.model} to build resulting object tree.
		If you supply your own factory, you have to make sure all
		returned objects have the same interface as their counterparts
		from L{musicbrainz2.model}.

		@param factory: an object factory 
		"""
		self.log = logging.getLogger(str(self.__class__))
		self.factory = factory

	def parse(self, inStream):
		"""Parses the MusicBrainz web service XML.

		Returns a L{Metadata} object representing the parsed XML or
		raises a L{ParseError} exception if the data was malformed.
		The parser tries to be liberal and skips invalid content if
		possible.

		Note that an L{IOError} may be raised if there is a problem
		reading C{inStream}.

		@param inStream: a file-like object
		@return: a L{Metadata} object (never None)
		@raise ParseError: if the document is not valid
		@raise IOError: if reading from the stream failed
		"""

		try:
			doc = xml.dom.minidom.parse(inStream)

			# Try to find the root element. If this isn't an mmd
			# XML file or the namespace is wrong, this will fail.
			elems = doc.getElementsByTagNameNS(NS_MMD_1, 'metadata')

			if len(elems) != 0:
				md = self._createMetadata(elems[0])
			else:
				msg = 'cannot find root element mmd:metadata'
				self.log.debug('ParseError: ' + msg)
				raise ParseError(msg)

			doc.unlink()

			return md
		except ExpatError, e:
			self.log.debug('ExpatError: ' + str(e))
			raise ParseError(msg=str(e), reason=e)
		except DOMException, e:
			self.log.debug('DOMException: ' + str(e))
			raise ParseError(msg=str(e), reason=e)
			

	def _createMetadata(self, metadata):
		res = Metadata()

		for node in getChildElements(metadata):
			if matches(node, 'artist'):
				res.artist = self._createArtist(node)	
			elif matches(node, 'release'):
				res.release = self._createRelease(node)	
			elif matches(node, 'track'):
				res.track = self._createTrack(node)	
			elif matches(node, 'artist-list'):
				self._addArtistToList(node, res.getArtistList())
			elif matches(node, 'release-list'):
				self._addReleasesToList(node, res.getReleaseList())
			elif matches(node, 'track-list'):
				self._addTrackToList(node, res.getTrackList())
			elif matches(node, 'user-list', NS_EXT_1):
				self._addUsersToList(node, res.getUserList())

		return res


	def _addArtistToList(self, listNode, resultList):
		self._addToList(listNode, resultList, self._createArtist)

	def _addReleasesToList(self, listNode, resultList):
		self._addToList(listNode, resultList, self._createRelease)

	def _addTracksToList(self, listNode, resultList):
		self._addToList(listNode, resultList, self._createTrack)

	def _addUsersToList(self, listNode, resultList):
		self._addToList(listNode, resultList, self._createUser)

	def _addToList(self, listNode, resultList, creator):
		for c in getChildElements(listNode):
			resultList.append(creator(c))

	def _createArtist(self, artistNode):
		artist = self.factory.newArtist()
		artist.setId(getIdAttr(artistNode, 'id', 'artist'))
		artist.setType(getUriAttr(artistNode, 'type'))
		
		for node in getChildElements(artistNode):
			if matches(node, 'name'):
				artist.setName(getText(node))
			elif matches(node, 'sort-name'):
				artist.setSortName(getText(node))
			elif matches(node, 'disambiguation'):
				artist.setDisambiguation(getText(node))
			elif matches(node, 'life-span'):
				artist.setBeginDate(getDateAttr(node, 'begin'))
				artist.setEndDate(getDateAttr(node, 'end'))
			elif matches(node, 'alias-list'):
				self._addArtistAliases(node, artist)
			elif matches(node, 'release-list'):
				self._addReleasesToList(node, artist.getReleases())
			elif matches(node, 'relation-list'):
				self._addRelationsToEntity(node, artist)

		return artist


	def _createRelease(self, releaseNode):
		release = self.factory.newRelease()
		release.setId(getIdAttr(releaseNode, 'id', 'release'))
		for t in getUriListAttr(releaseNode, 'type'):
			release.addType(t)

		for node in getChildElements(releaseNode):
			if matches(node, 'title'):
				release.setTitle(getText(node))
			elif matches(node, 'text-representation'):
				lang = getAttr(node, 'language', '^[A-Z]{3}$')
				release.setTextLanguage(lang)
				script = getAttr(node, 'script', '^[A-Z][a-z]{3}$')
				release.setTextScript(script)
			elif matches(node, 'asin'):
				release.setAsin(getText(node))
			elif matches(node, 'artist'):
				release.setArtist(self._createArtist(node))
			elif matches(node, 'release-event-list'):
				self._addReleaseEvents(node, release)
			elif matches(node, 'disc-list'):
				self._addDiscs(node, release)
			elif matches(node, 'track-list'):
				self._addTracksToList(node, release.getTracks())
			elif matches(node, 'relation-list'):
				self._addRelationsToEntity(node, release)

		return release


	def _addReleaseEvents(self, releaseListNode, release):
		for node in getChildElements(releaseListNode):
			if matches(node, 'event'):
				country = getAttr(node, 'country', '^[A-Z]{2}$')
				date = getDateAttr(node, 'date')
				if None not in (country, date):
					event = self.factory.newReleaseEvent()
					event.setCountryId(country)
					event.setDate(date)
					release.addReleaseEvent(event)


	def _addDiscs(self, discIdListNode, release):
		for node in getChildElements(discIdListNode):
			if matches(node, 'disc') and node.hasAttribute('id'):
				d = self.factory.newDisc()
				d.setId(node.getAttribute('id'))
				d.setSectors(getPositiveIntAttr(node, 'sectors'))
				release.addDisc(d)


	def _addArtistAliases(self, aliasListNode, artist):
		for node in getChildElements(aliasListNode):
			if matches(node, 'alias'):
				alias = self.factory.newArtistAlias()
				alias.setValue(getText(node))
				artist.addAlias(alias)


	def _createTrack(self, trackNode):
		track = self.factory.newTrack()
		track.setId(getIdAttr(trackNode, 'id', 'track'))

		for node in getChildElements(trackNode):
			if matches(node, 'title'):
				track.setTitle(getText(node))
			elif matches(node, 'artist'):
				track.setArtist(self._createArtist(node))
			elif matches(node, 'duration'):
				track.setDuration(getPositiveIntText(node))
			elif matches(node, 'release-list'):
				self._addReleasesToList(node, track.getReleases())
			elif matches(node, 'trmid-list'):
				self._addTrmIds(node, track)
			elif matches(node, 'relation-list'):
				self._addRelationsToEntity(node, track)

		return track

	# MusicBrainz extension
	def _createUser(self, userNode):
		user = self.factory.newUser()
		for t in getUriListAttr(userNode, 'type', NS_EXT_1):
			user.addType(t)

		for node in getChildElements(userNode):
			if matches(node, 'name'):
				user.setName(getText(node))
			elif matches(node, 'nag', NS_EXT_1):
				user.setShowNag(getBooleanAttr(node, 'show'))

		return user


	def _addTrmIds(self, trmIdListNode, track):
		for node in getChildElements(trmIdListNode):
			if matches(node, 'trmid') and node.hasAttribute('id'):
				track.addTrmId(node.getAttribute('id'))


	def _addRelationsToEntity(self, relationListNode, entity):
		targetType = getUriAttr(relationListNode, 'target-type', NS_REL_1)

		if targetType is None:
			return

		for node in getChildElements(relationListNode):
			if matches(node, 'relation'):
				rel = self._createRelation(node, targetType)
				if rel is not None:
					entity.addRelation(rel)


	def _createRelation(self, relationNode, targetType):
		relation = self.factory.newRelation()

		relation.setType(getUriAttr(relationNode, 'type', NS_REL_1))
		relation.setTargetType(targetType)
		resType = getResourceType(targetType)
		relation.setTargetId(getIdAttr(relationNode, 'target', resType))

		if relation.getType() is None \
				or relation.getTargetType() is None \
				or relation.getTargetId() is None:
			return None

		relation.setDirection(getDirectionAttr(relationNode, 'direction'))
		relation.setBeginDate(getDateAttr(relationNode, 'begin'))
		relation.setEndDate(getDateAttr(relationNode, 'end'))

		for a in getUriListAttr(relationNode, 'attributes', NS_REL_1):
			relation.addAttribute(a)

		target = None
		children = getChildElements(relationNode)
		if len(children) > 0:
			node = children[0]
			if matches(node, 'artist'):
				target = self._createArtist(node)	
			elif matches(node, 'release'):
				target = self._createRelease(node)	
			elif matches(node, 'track'):
				target = self._createTrack(node)	

		relation.setTarget(target)

		return relation


#
# DOM Utilities
#

def matches(node, name, namespace=NS_MMD_1):
	"""Checks if an xml.dom.Node and a given name and namespace match."""

	if node.localName == name and node.namespaceURI == namespace:
		return True
	else:
		return False


def getChildElements(parentNode):
	"""Returns all direct child elements of the given xml.dom.Node."""

	children = [ ]
	for node in parentNode.childNodes:
		if node.nodeType == node.ELEMENT_NODE:
			children.append(node)

	return children


def getText(element):
	"""Returns the text content of the given xml.dom.Element.

	This function simply fetches all contained text nodes, so the element
	should not contain child elements.
	"""
	res = ''
	for node in element.childNodes:
		if node.nodeType == node.TEXT_NODE:
			res += node.data

	return res


def getPositiveIntText(element):
	"""Returns the text content of the given xml.dom.Element as an int."""

	res = getText(element)

	if res is None:
		return None

	try:
		return int(res)
	except ValueError:
		return None


def getAttr(element, attrName, regex=None, default=None):
	"""Returns an attribute of the given element.

	If there is no attribute with that name or the attribute doesn't
	match the regular expression, default is returned.
	"""

	if element.hasAttribute(attrName):
		content = element.getAttribute(attrName)

		if regex is None or re.match(regex, content):
			return content
		else:
			return default
	else:
		return default


def getDateAttr(element, attrName):
	"""Gets an incomplete date from an attribute."""
	return getAttr(element, attrName, '^\d+(-\d\d)?-(\d\d)?$')


def getIdAttr(element, attrName, typeName):
	"""Gets an ID from an attribute and turns it into an absolute URI."""
	value = getAttr(element, attrName)

	return makeAbsoluteUri('http://musicbrainz.org/' + typeName + '/', value)

	

def getPositiveIntAttr(element, attrName):
	"""Gets a positive int from an attribute, or None."""
	try:
		val = int(getAttr(element, attrName))

		if val >= 0:
			return val
		else:
			return None
	except ValueError:
		return None # raised if conversion to int fails
	except TypeError:
		return None # raised if no such attribute exists


def getUriListAttr(element, attrName, prefix=NS_MMD_1):
	"""Gets a list of URIs from an attribute."""
	if not element.hasAttribute(attrName):
		return [ ]

	f = lambda x: x != ''
	uris = filter(f, re.split('\s+', element.getAttribute(attrName)))

	m = lambda x: makeAbsoluteUri(prefix, x)
	uris = map(m, uris)

	return uris


def getUriAttr(element, attrName, prefix=NS_MMD_1):
	"""Gets a URI from an attribute.

	This also works for space-separated URI lists. In this case, the
	first URI is returned.
	"""
	uris = getUriListAttr(element, attrName, prefix)
	if len(uris) > 0:
		return uris[0]
	else:
		return None


def getBooleanAttr(element, attrName):
	"""Gets a boolean value from an attribute."""
	value = getAttr(element, attrName)
	if value == 'true':
		return True
	elif value == 'false':	
		return False
	else:
		return None


def getDirectionAttr(element, attrName):
	"""Gets the Relation reading direction from an attribute."""
	regex = '^\s*(' + '|'.join((
				model.RELATION_DIR_BOTH,
				model.RELATION_DIR_FORWARD,
				model.RELATION_DIR_BACKWARD)) + ')\s*$'
	return getAttr(element, 'direction', regex, model.RELATION_DIR_BOTH)


def makeAbsoluteUri(prefix, uriStr):
	"""Creates an absolute URI adding prefix, if necessary."""
	if uriStr is None:
		return None

	(scheme, netloc, path, params, query, frag) = urlparse.urlparse(uriStr)

	if scheme == '' and netloc == '':
		return prefix + uriStr
	else:
		return uriStr
 
 
def getResourceType(uri):
	"""Gets the resource type from a URI.

	The resource type is the basename of the URI's path.
	"""
	m = re.match('^' + NS_REL_1 + '(.*)$', uri)
	
	if m:
		return m.group(1).lower()
	else:
		return None

# EOF
