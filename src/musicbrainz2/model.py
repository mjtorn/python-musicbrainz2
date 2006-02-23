"""The MusicBrainz domain model.

These classes are part of the MusicBrainz domain model. They may be used
by other modules and don't contain any network or other I/O code. If you
want to request data from the web service, please have a look at
L{musicbrainz2.webservice}.

The most important classes, usually acting as entry points, are
L{Artist}, L{Release}, and L{Track}.

@var VARIOUS_ARTISTS_ID: The ID of the special 'Various Artists' artist.

@var NS_MMD_1: Default namespace prefix for all MusicBrainz metadata.
@var NS_REL_1: Namespace prefix for relations.
@var NS_EXT_1: Namespace prefix for MusicBrainz extensions.

@var RELATION_TO_ARTIST: Identifies relations linking to an artist.
@var RELATION_TO_RELEASE: Identifies relations linking to a release.
@var RELATION_TO_TRACK: Identifies relations linking to a track.
@var RELATION_TO_URL: Identifies relations linking to an URL.

@var RELATION_DIR_BOTH: Relation reading direction doesn't matter.
@var RELATION_DIR_FORWARD: Relation reading direction is from source to target.
@var RELATION_DIR_BACKWARD: Relation reading direction is from target to source.

@see: L{musicbrainz2.webservice}

@author: Matthias Friedrich <matt@mafr.de>
"""
__revision__ = '$Id$'

VARIOUS_ARTISTS_ID = 'http://musicbrainz.org/artist/89ad4ac3-39f7-470e-963a-56509c546377'

# Namespace URI prefixes
#
NS_MMD_1 = 'http://musicbrainz.org/ns/mmd-1.0#'
NS_REL_1 = 'http://musicbrainz.org/ns/rel-1.0#'
NS_EXT_1 = 'http://musicbrainz.org/ns/ext-1.0#'

# Relation target types
#
RELATION_TO_ARTIST = 'http://musicbrainz.org/ns/rel-1.0#Artist'
RELATION_TO_RELEASE = 'http://musicbrainz.org/ns/rel-1.0#Release'
RELATION_TO_TRACK = 'http://musicbrainz.org/ns/rel-1.0#Track'
RELATION_TO_URL = 'http://musicbrainz.org/ns/rel-1.0#Url'

# Relation reading directions
#
RELATION_DIR_BOTH = 'both'
RELATION_DIR_FORWARD = 'forward'
RELATION_DIR_BACKWARD = 'backward'


class Entity:
	"""A first-level MusicBrainz class.

	All entities in MusicBrainz have unique IDs (which are absolute URIs)
	and may have any number of L{relations <Relation>} to other entities.
	This class is abstract and should not be instantiated.

	Relations are differentiated by their I{target type}, that means,
	where they link to. MusicBrainz currently supports four target types
	(artists, releases, tracks, and URLs) each identified using a URI.
	To get all relations with a specific target type, you can use
	L{getRelations} and pass one of the following constants as the
	parameter:

	 - L{RELATION_TO_ARTIST}
	 - L{RELATION_TO_RELEASE}
	 - L{RELATION_TO_TRACK}
	 - L{RELATION_TO_URL}

	@see: L{Relation}
	"""

	def __init__(self, id_=None):
		"""Constructor.

		This should only used by derived classes.

		@param id_: a string containing an absolute URI
		"""
		self.id = id_
		self.relations = { }

	def getId(self):
		"""Returns a MusicBrainz ID.

		@return: a string containing a URI, or None
		"""
		return self.id

	def setId(self, value):
		"""Sets a MusicBrainz ID.

		@param value: a string containing an absolute URI 
		"""
		self.id = value


	def getRelations(self, targetType=None, relationType=None):
		"""Returns a list of relations.

		If C{targetType} is given, only relations of that target
		type are returned. For MusicBrainz, the following target
		types are defined:
		 - L{RELATION_TO_ARTIST}
		 - L{RELATION_TO_RELEASE}
		 - L{RELATION_TO_TRACK}
		 - L{RELATION_TO_URL}

		If C{targetType} is L{RELATION_TO_ARTIST}, for example,
		this method returns all relations between this Entity and
		artists.

		You may use the C{relationType} parameter to further restrict
		the selection. If it is set, only relations with the given
		relation type are returned.

		@param targetType: a string containing an absolute URI, or None
		@param relationType: a string containing an absolute URI, or None
		@return: a list of L{Relation} objects

		@see: L{Entity}
		"""
		allRels = [ ]
		if targetType is not None:
			allRels = self.relations.setdefault(targetType, [ ])
		else:
			for (k, relList) in self.relations.items():
				for rel in relList:
					allRels.append(rel)

		if relationType is None:
			return allRels
		else:
			return [r for r in allRels if r.getType() == relationType]


	def addRelation(self, relation):
		"""Adds a relation.

		This method adds C{relation} to the list of relations. The
		given relation has to be initialized, at least the target
		type has to be set.

		@param relation: the L{Relation} object to add

		@see: L{Entity}
		"""
		assert relation.getType is not None
		assert relation.getTargetType is not None
		assert relation.getTargetId is not None
		l = self.relations.setdefault(relation.targetType, [ ])
		l.append(relation)


	def getRelationTargetTypes(self):
		"""Returns a list of target types available for this entity.

		Use this to find out to which types of targets this entity
		has relations. If the entity only has relations to tracks and
		artists, for example, then a list containg the strings
		L{RELATION_TO_TRACK} and L{RELATION_TO_ARTIST} is returned.

		@return: a list of strings containing URIs

		@see: L{getRelations}
		"""
		return self.relations.keys()


class Artist(Entity):
	"""Represents an artist.

	Artists in MusicBrainz can have a type. Currently, this type can
	be either Person or Group for which the following URIs are assigned:

	 - C{http://musicbrainz.org/ns/mmd-1.0#Person}
	 - C{http://musicbrainz.org/ns/mmd-1.0#Group}
	"""
	def __init__(self, id_=None, type_=None, name=None, sortName=None):
		"""Constructor.

		@param id_: a string containing an absolute URI
		@param type_: a string containing an absolute URI
		@param name: a string containing the artist's name
		@param sortName: a string containing the artist's sort name
		"""
		Entity.__init__(self, id_)
		self.type = type_
		self.name = name
		self.sortName = sortName
		self.disambiguation = None
		self.beginDate = None
		self.endDate = None
		self.aliases = [ ]
		self.releases = [ ]

	def getType(self):
		"""Returns the artist's type.

		@return: a string containing an absolute URI, or None 
		"""
		return self.type

	def setType(self, typeUri):
		"""Sets the artist's type.

		@param typeUri: a string containing an absolute URI
		"""
		self.type = typeUri

	def getName(self):
		"""Returns the artist's name.

		@return: a string containing the artist's name, or None
		"""
		return self.name

	def setName(self, name):
		"""Sets the artist's name.

		@param name: a string containing the artist's name
		"""
		self.name = name

	def getSortName(self):
		"""Returns the artist's sort name.

		The sort name is the artist's name in a special format which
		is better suited for sorting. The MusicBrainz style guide 
		specifies this format.

		@see: U{The MusicBrainz Style Guidelines
			<http://musicbrainz.org/style.html>}
		"""
		return self.sortName

	def setSortName(self, sortName):
		"""Sets the artist's sort name.

		@param sortName: a string containing the artist's sort name

		@see: L{getSortName}
		"""
		self.sortName = sortName

	def getDisambiguation(self):
		"""Returns the disambiguation attribute.

		This attribute may be used if there is more than one artist
		with the same name. In this case, disambiguation attributes
		are added to the artists' names to keep them apart.

		For example, there are at least three bands named 'Vixen'.
		Each band has a different disambiguation in the MusicBrainz
		database, like 'Hip-hop' or 'all-female rock/glam band'.

		@return: a disambiguation string, or None

		@see: L{getUniqueName}
		"""
		return self.disambiguation

	def setDisambiguation(self, disambiguation):
		"""Sets the disambiguation attribute.

		@param disambiguation: a disambiguation string

		@see: L{getDisambiguation}, L{getUniqueName}
		"""
		self.disambiguation = disambiguation

	def getUniqueName(self):
		"""Returns a unique artist name (using disambiguation).

		This method returns the artist name together with the
		disambiguation attribute in parenthesis if it exists.
		Example: 'Vixen (Hip-hop)'.

		@return: a string containing the unique name

		@see: L{getDisambiguation}
		"""
		d = self.getDisambiguation() 
		if d is not None and d.strip() != '':
			return '%s (%s)' % (self.getName(), d)
		else: 
			return self.getName()

	def getBeginDate(self):
		"""Returns the birth/foundation date.

		The definition of the I{begin date} depends on the artist's
		type. For persons, this is the day of birth, for groups it
		is the day the group was founded.

		The returned date has the format 'YYYY', 'YYYY-MM', or 
		'YYYY-MM-DD', depending on how much detail is known.

		@return: a string containing the date, or None

		@see: L{getType}
		"""
		return self.beginDate

	def setBeginDate(self, dateStr):
		"""Sets the begin/foundation date.

		@param dateStr: a date string

		@see: L{getBeginDate}
		"""
		self.beginDate = dateStr

	def getEndDate(self):
		"""Get the death/dissolving date.

		The definition of the I{end date} depends on the artist's
		type. For persons, this is the day of death, for groups it
		is the day the group was dissolved.

		@return: a string containing a date, or None

		@see: L{getBeginDate}
		"""
		return self.endDate

	def setEndDate(self, dateStr):
		"""Sets the death/dissolving date.

		@param dateStr: a string containing a date

		@see: L{setEndDate}, L{getBeginDate}
		"""
		self.endDate = dateStr

	def getAliases(self):
		"""Returns the list of aliases for this artist.

		@return: a list of L{ArtistAlias} objects
		"""
		return self.aliases

	def addAlias(self, alias):
		"""Adds an alias for this artist.
		
		@param alias: an L{ArtistAlias} object
		"""
		self.aliases.append(alias)

	def getReleases(self):
		"""Returns a list of releases from this artist.

		This may also include releases where this artist isn't the
		I{main} artist but has just contributed one or more tracks
		(aka VA-Releases).

		@return: a list of L{Release} objects

		@note: The MusicBrainz web service currently doesn't return
		releases for an artist because of the huge amount of data
		that would be sent for some artists.
		"""
		return self.releases

	def addRelease(self, release):
		"""Adds a release to this artist's list of releases.

		@param release: a L{Release} object
		"""
		self.release.append(release)


class Release(Entity):
	"""Represents a Release.

	A release within MusicBrainz is an L{Entity} which contains L{Track}
	objects.  Releases may be of more than one type: There can be albums,
	singles, compilations, live recordings, official releases, bootlegs
	etc.

	@note: The current MusicBrainz server implementation supports only a
	limited set of types.
	"""
	def __init__(self, id_=None, title=None):
		"""Constructor.

		@param id_: a string containing an absolute URI
		@param title: a string containing the title
		"""
		Entity.__init__(self, id_)
		self.types = [ ]
		self.title = title
		self.textLanguage = None
		self.textScript = None
		self.asin = None
		self.artist = None
		self.releaseEvents = [ ]
		#self.releaseEventsCount = None
		self.discs = [ ]
		#self.discIdsCount = None
		self.tracks = [ ]
		self.tracksOffset = None


	def getTypes(self):
		"""Returns the types of this release.

		@return: a list of strings containing absolute URIs
		"""
		return self.types

	def addType(self, type_):
		"""Add a type to the list of types.

		@param type_: a string containing absolute URIs

		@see: L{getTypes}
		"""
		self.types.append(type_)

	def getTitle(self):
		"""Returns the release's title.

		@return: a string containing the release's title
		"""
		return self.title

	def setTitle(self, title):
		"""Sets the release's title.

		@param title: a string containing the release's title, or None
		"""
		self.title = title

	def getTextLanguage(self):
		"""Returns the language used in release and track titles.

		To represent the language, the ISO-639-2/T standard is used,
		which provides three-letter terminological language codes like
		'ENG', 'DEU', 'JPN', 'KOR', 'ZHO' or 'YID'.

		Note that this refers to release and track I{titles}, not
		lyrics.

		@return: a string containing the language code, or None
		"""
		return self.textLanguage

	def setTextLanguage(self, language):
		"""Sets the language used in releaes and track titles.

		@param language: a string containing a language code

		@see: L{getTextLanguage}
		"""
		self.textLanguage = language

	def getTextScript(self):
		"""Returns the script used in release and track titles.

		To represent the script, ISO-15924 script codes are used.
		Valid codes are, among others: 'Latn', 'Cyrl', 'Hans', 'Hebr'

		Note that this refers to release and track I{titles}, not
		lyrics.

		@return: a string containing the script code, or None
		"""
		return self.textScript

	def setTextScript(self, script):
		"""Sets the script used in releaes and track titles.

		@param script: a string containing a script code

		@see: L{getTextScript}
		"""
		self.textScript = script

	def getAsin(self):
		"""Returns the amazon shop identifier (ASIN).

		The ASIN is a 10-letter code (except for books) assigned
		by Amazon, which looks like 'B000002IT2' or 'B00006I4YD'.

		@return: a string containing the ASIN, or None
		"""
		return self.asin

	def setAsin(self, asin):
		"""Sets the amazon shop identifier (ASIN).

		@param asin: a string containing the ASIN

		@see: L{getAsin}
		"""
		self.asin = asin

	def getArtist(self):
		"""Returns the main artist of this release.

		@return: an L{Artist} object, or None
		"""
		return self.artist

	def setArtist(self, artist):
		"""Sets this release's main artist.

		@param artist: an L{Artist} object
		"""
		self.artist = artist

	def isSingleArtistRelease(self):
		"""Checks if this is a single artist's release.

		Returns C{True} if the release's main artist (L{getArtist}) is
		also the main artist for all of the tracks. This is checked by
		comparing the artist IDs.

		Note that the release's artist has to be set (see L{setArtist})
		for this. The track artists may be unset.

		@return: True, if this is a single artist's release
		"""
		releaseArtist = self.getArtist()
		assert releaseArtist is not None, 'Release Artist may not be None!'
		for track in self.getTracks():
			if track.getArtist() is None:
				continue
			if track.getArtist().getId() != releaseArtist.getId():
				return False

		return True

	def getTracks(self):
		"""Returns the tracks this release contains.

		@return: a list containing L{Track} objects

		@see: L{getTracksOffset}
		"""
		return self.tracks

	def addTrack(self, track):
		"""Adds a track to this release.

		This appends a track at the end of this release's track list.

		@param track: a L{Track} object
		"""
		self.tracks.append(track)

	def getTracksOffset(self):
		"""Returns the offset of the track list.

		This is used if the track list is incomplete (ie. the web
		service only returned part of the tracks on this release).
		Note that the offset value is zero-based, which means track
		C{0} is the first track.

		@return: an integer containing the offset, or None

		@see: L{getTracks}
		"""
		return self.tracksOffset

	def setTracksOffset(self, offset):
		"""Sets the offset of the track list.

		@param offset: an integer containing the offset, or None

		@see: L{getTracksOffset}
		"""
		self.tracksOffset = offset

	def getReleaseEvents(self):
		"""Returns the list of release events.

		A L{Release} may contain a list of so-called release events,
		each represented using a L{ReleaseEvent} object. Release
		evens specify where and when this release was, well, released.

		@return: a list of L{ReleaseEvent} objects

		@see: L{getReleaseEventsAsDict}
		"""
		return self.releaseEvents

	def addReleaseEvent(self, event):
		"""Adds a release event to this release.

		@param event: a L{ReleaseEvent} object

		@see: L{getReleaseEvents}
		"""
		self.releaseEvents.append(event)

	def getReleaseEventsAsDict(self):
		"""Returns the release events represented as a dict.

		Keys are ISO-3166 country codes like 'DE', 'UK', 'FR' etc.
		Values are dates in 'YYYY', 'YYYY-MM' or 'YYYY-MM-DD' format.

		@return: a dict containing (countryCode, date) entries

		@see: L{getReleaseEvents}
		"""
		d = { }
		for event in self.getReleaseEvents():
			d[event.getCountryId()] = event.getDate()
		return d

	def getEarliestReleaseDate(self):
		"""Returns the earliest release date.

		This favours complete dates. For example, '2006-09' is
		returned if there is '2000', too. If there is no release
		event assiciated with this release, None is returned.

		@return: a string containing the date, or None 

		@see: L{getReleaseEvents}, L{getReleaseEventsAsDict}
		"""
		dates = [ ]
		for event in self.getReleaseEvents():
			date = event.getDate()
			if len(date) == 10:    # 'YYYY-MM-DD'
				dates.append(date)
			elif len(date) == 7:   # 'YYYY-MM'
				dates.append(date + '-99')
			else:
				dates.append(date + '-99-99')

		dates.sort()

		if len(dates) > 0:
			return dates[0]
		else:
			return None

	#def getReleaseEventsCount(self):
	#	"""Returns the number of release events.
	#
	#	This may or may not match with the number of elements that
	#	getReleaseEvents() returns. If the count is higher than
	#	the list, it indicates that the list is incomplete.
	#	"""
	#	return self.releaseEventsCount

	#def setReleaseEventsCount(self, value):
	#	self.releaseEventsCount = value

	def getDiscs(self):
		"""Returns the discs associated with this release.

		Discs are currently containers for MusicBrainz DiscIDs.
		Note that under rare circumstances (identical TOCs), a
		DiscID could be associated with more than one release.

		@return: a list of L{Disc} objects
		"""
		return self.discs

	def addDisc(self, disc):
		"""Adds a disc to this release.

		@param disc: a L{Disc} object
		"""
		self.discs.append(disc)

	#def getDiscIdsCount(self):
	#	return self.discIdsCount

	#def setDiscIdsCount(self, value):
	#	self.discIdsCount = value


class Track(Entity):
	"""Represents a track.

	This class represents a track which may appear on one or more releases.
	A track may be associated with exactly one artist (the I{main} artist).

	Using L{getReleases}, you can find out on which releases this track
	appears. To get the track number, too, use the
	L{Release.getTracksOffset} method.

	@note: Currently, the MusicBrainz server doesn't support tracks to
	       be on more than one release.

	@see: L{Release}, L{Artist}
	"""
	def __init__(self, id_=None, title=None):
		"""Constructor.

		@param id_: a string containing an absolute URI
		@param title: a string containing the title
		"""
		Entity.__init__(self, id_)
		self.title = title
		self.artist = None
		self.duration = None
		self.trmIds = [ ]
		self.releases = [ ]

	def getTitle(self):
		"""Returns the track's title.

		The style and format of this attribute is specified by the
		style guide.

		@return: a string containing the title, or None

		@see: U{The MusicBrainz Style Guidelines
			<http://musicbrainz.org/style.html>}
		"""
		return self.title

	def setTitle(self, title):
		"""Sets the track's title.

		@param title: a string containing the title

		@see: L{getTitle}
		"""
		self.title = title

	def getArtist(self):
		"""Returns the main artist of this track.

		@return: an L{Artist} object, or None
		"""
		return self.artist

	def setArtist(self, artist):
		"""Sets this track's main artist.

		@param artist: an L{Artist} object
		"""
		self.artist = artist

	def getDuration(self):
		"""Returns the duration of this track in milliseconds.

		@return: an int containing the duration in milliseconds, or None
		"""
		return self.duration

	def setDuration(self, duration):
		"""Sets the duration of this track in milliseconds.

		@param duration: an int containing the duration in milliseconds
		"""
		self.duration = duration

	def getDurationSplit(self):
		"""Returns the duration as a (minutes, seconds) tuple.

		If no duration is set, (0, 0) is returned. Seconds are
		rounded towards the ceiling if at least 500 milliseconds
		are left.

		@return: a (minutes, seconds) tuple, both entries being ints
		"""
		duration = self.getDuration()
		if duration is None:
			return (0, 0)
		else:
			seconds = int( round(duration / 1000.0) )
			return (seconds / 60, seconds % 60)

	def getTrmIds(self):
		"""Returns the TRM IDs associated with this track.

		Please note that a TRM ID may be associated with more than one
		track.

		@return: a list of strings, each containing one TRM ID
		"""
		return self.trmIds

	def addTrmId(self, trmId):
		"""Add a TRM ID to this track.

		@param trmId: a string containing a TRM ID
		"""
		self.trmIds.append(trmId)

	def getReleases(self):
		"""Returns the list of releases this track appears on.

		@return: a list of L{Release} objects
		"""
		return self.releases

	def addRelease(self, release):
		"""Add a release on which this track appears.

		@param release: a L{Release} object
		"""
		self.releases.append(release)



class Relation:
	"""Represents a relation between two Entities.

	There may be an arbitrary number of relations between all first
	class objects in MusicBrainz. The Relation itself has multiple
	attributes, which may or may not be used for a given relation
	type.

	Note that a L{Relation} object only contains the target but not
	the source end of the relation.

	@todo: Add some examples.
	"""
	def __init__(self, relationType=None, targetType=None, targetId=None,
			direction=RELATION_DIR_BOTH, attributes=None,
			beginDate=None, endDate=None, target=None):
		"""Constructor.

		@param relationType: a string containing an absolute URI
		@param targetType: a string containing an absolute URI
		@param targetId: a string containing an absolute URI
		@param direction: one of C{RELATION_DIR_FORWARD},
		C{RELATION_DIR_BACKWARD}, or C{RELATION_DIR_BOTH}
		@param attributes: a list of strings containing absolute URIs
		@param beginDate: a string containing a date
		@param endDate: a string containing a date
		@param target: an instance of a subclass of L{Entity}
		"""
		self.relationType = relationType
		self.targetType = targetType
		self.targetId = targetId
		self.direction = direction
		self.beginDate = beginDate
		self.endDate = endDate
		self.target = target
		self.attributes = attributes
		if self.attributes is None:
			self.attributes = [ ]

	def getType(self):
		"""Returns this relation's type.

		@return: a string containing an absolute URI, or None 
		"""
		return self.relationType

	def setType(self, type_):
		"""Sets this relation's type.

		@param type_: a string containing an absolute URI
		"""
		self.relationType = type_

	def getTargetId(self):
		"""Returns the target's ID.

		This is the ID the relation points to. It is an absolute
		URI, and in case of an URL relation, it is a URL.

		@return: a string containing an absolute URI
		"""
		return self.targetId

	def setTargetId(self, targetId):
		"""Sets the target's ID.

		@param targetId: a string containing an absolute URI

		@see: L{getTargetId}
		"""
		self.targetId = targetId

	def getTargetType(self):
		"""Returns the target's type.

		For MusicBrainz data, the following target types are defined:
		 - artists: L{RELATION_TO_ARTIST}
		 - releases: L{RELATION_TO_RELEASE}
		 - tracks: L{RELATION_TO_TRACK}
		 - urls: L{RELATION_TO_URL}

		@return: a string containing an absolute URI
		"""
		return self.targetType

	def setTargetType(self, targetType):
		"""Sets the target's type.

		@param targetType: a string containing an absolute URI

		@see: L{getTargetType}
		"""
		self.targetType = targetType

	def getAttributes(self):
		"""Returns a list of attributes describing this relation.

		The attributes permitted depend on the relation type.

		@return: a list of strings containing absolute URIs
		"""
		return self.attributes

	def addAttribute(self, attribute):
		"""Adds an attribute to the list.

		@param attribute: a string containing an absolute URI
		"""
		self.attributes.append(attribute)

	def getBeginDate(self):
		"""Returns the begin date.

		The definition depends on the relation's type. It may for
		example be the day of a marriage or the year an artist
		joined a band. For other relation types this may be
		undefined.

		@return: a string containing a date
		"""
		return self.beginDate

	def setBeginDate(self, dateStr):
		"""Sets the begin date.

		@param dateStr: a string containing a date

		@see: L{getBeginDate}
		"""
		self.beginDate = dateStr

	def getEndDate(self):
		"""Returns the end date.

		As with the begin date, the definition depends on the
		relation's type. Depending on the relation type, this may
		or may not be defined.

		@return: a string containing a date

		@see: L{getBeginDate}
		"""
		return self.endDate

	def setEndDate(self, dateStr):
		"""Sets the end date.

		@param dateStr: a string containing a date

		@see: L{getBeginDate}
		"""
		self.endDate = dateStr

	def getDirection(self):
		"""Returns the reading direction.

		The direction may be one of L{RELATION_DIR_FORWARD},
		L{RELATION_DIR_BACKWARD}, or L{RELATION_DIR_BOTH},
		depending on how the relation should be read. For example,
		if direction is L{RELATION_DIR_FORWARD} for a cover relation,
		it is read as "X is a cover of Y". Some relations are
		bidirectional, like marriages. In these cases, the direction
		is L{RELATION_DIR_BOTH}.

		@return: L{RELATION_DIR_FORWARD}, L{RELATION_DIR_BACKWARD},
		or L{RELATION_DIR_BOTH}
		"""
		return self.direction

	def setDirection(self, direction):
		"""Sets the reading direction.

		@param direction: L{RELATION_DIR_FORWARD},
		L{RELATION_DIR_BACKWARD}, or L{RELATION_DIR_BOTH}

		@see: L{getDirection}
		"""
		self.direction = direction

	def getTarget(self):
		"""Returns this relation's target object.

		Note that URL relations never have a target object. Use the
		L{getTargetId} method to get the URL.

		@return: a subclass of L{Entity}, or None
		"""
		return self.target

	def setTarget(self, target):
		"""Sets this relation's target object.

		Note that URL relations never have a target object, they
		are set using L{setTargetId}.

		@param target: a subclass of L{Entity}
		"""
		self.target = target


class ReleaseEvent:
	"""A release event, indicating where and when a release took place.

	All country codes used must be valid ISO-3166 country codes (i.e. 'DE',
	'UK' or 'FR'). The dates are strings and must have the format 'YYYY',
	'YYYY-MM' or 'YYYY-MM-DD'.
	"""

	def __init__(self, countryId=None, dateStr=None):
		"""Constructor.

		@param countryId: a string containing an ISO-3166 country code
		@param dateStr: a string containing a date string
		"""
		self.countryId = countryId
		self.dateStr = dateStr

	def getCountryId(self):
		"""Returns the country a release took place.

		@return: a string containing an ISO-3166 country code
		"""
		return self.countryId

	def setCountryId(self, countryId):
		"""Sets the country a release took place.

		@param countryId: a string containing an ISO-3166 country code
		"""
		self.countryId = countryId

	def getDate(self):
		"""Returns the date a release took place.

		@return: a string containing a date
		"""
		return self.dateStr

	def setDate(self, dateStr):
		"""Sets the date a release took place.

		@param dateStr: a string containing a date
		"""
		self.dateStr = dateStr



class Disc:
	"""Represents an Audio CD.

	This class represents an Audio CD. A disc can have an ID (the
	MusicBrainz DiscID), which is calculated from the CD's table of
	contents (TOC). There may also be data from the TOC like the length
	of the disc in sectors, as well as position and length of the tracks.

	Note that different TOCs, maybe due to different pressings, lead to
	different DiscIDs. Conversely, if two different discs have the same
	TOC, they also have the same DiscID (which is unlikely but not
	impossible). DiscIDs are always 28 characters long and look like this:
	C{'J68I_CDcUFdCRCIbHSEbTBCbooA-'}. Sometimes they are also referred
	to as CDIndex IDs.

	The L{MusicBrainz web service <musicbrainz2.webservice>} only returns
	the DiscID and the number of sectors. The DiscID calculation function 
	L{musicbrainz2.disc.readDisc}, however, can retrieve the other
	attributes of L{Disc} from an Audio CD in the disc drive.
	"""
	def __init__(self, id_=None):
		"""Constructor.

		@param id_: a string containing a 28-character DiscID 
		"""
		self.id = id_
		self.sectors = None
		self.firstTrackNum = None
		self.lastTrackNum = None
		self.tracks = [ ]

	def getId(self):
		"""Returns the MusicBrainz DiscID.

		@return: a string containing a 28-character DiscID 
		"""
		return self.id

	def setId(self, id_):
		"""Sets the MusicBrainz DiscId.

		@param id_: a string containing a 28-character DiscID
		"""
		self.id = id_

	def getSectors(self):
		"""Returns the length of the disc in sectors.

		@return: the length in sectors as an integer, or None
		"""
		return self.sectors

	def setSectors(self, sectors):
		"""Sets the length of the disc in sectors.

		@param sectors: the length in sectors as an integer
		"""
		self.sectors = sectors

	def getFirstTrackNum(self):
		"""Returns the number of the first track on this disc.

		@return: an int containing the track number, or None
		"""
		return self.firstTrackNum

	def setFirstTrackNum(self, trackNum):
		"""Sets the number of the first track on this disc.

		@param trackNum: an int containing the track number, or None
		"""
		self.firstTrackNum = trackNum

	def getLastTrackNum(self):
		"""Returns the number of the last track on this disc.

		@return: an int containing the track number, or None
		"""
		return self.lastTrackNum

	def setLastTrackNum(self, trackNum):
		"""Sets the number of the last track on this disc.

		@param trackNum: an int containing the track number, or None
		"""
		self.lastTrackNum = trackNum

	def getTracks(self):
		"""Returns the sector offset and length of this disc.

		This method returns a list of tuples containing the track
		offset and length in sectors. The track offset is measured
		from the beginning of the disc, the length is relative to
		the track's offset. Note that the leadout track is I{not}
		included.

		@return: a list of (offset, length) tuples (values are ints)
		"""
		return self.tracks

	def addTrack(self, track):
		"""Adds a track to the list.
		
		This method adds an (offset, length) tuple to the list of
		tracks. The leadout track must I{not} be added. The total
		length of the disc can be set using L{setSectors}.

		@param track: an (offset, length) tuple (values are ints)

		@see: L{getTracks}
		"""
		self.tracks.append(track)


class ArtistAlias:
	"""Represents an artist alias.

	An alias is a different representation of an artist's name. This
	may be a common misspelling or a transliteration.
	"""
	def __init__(self, value=None):
		"""Constructor.

		@param value: a string containing the alias
		"""
		self.value = value

	def getValue(self):
		"""Returns the alias.

		@return: a string containing the alias
		"""
		return self.value

	def setValue(self, value):
		"""Sets the alias.

		@param value: a string containing the alias
		"""
		self.value = value


class User:
	"""Represents a MusicBrainz user."""

	def __init__(self):
		"""Constructor."""
		self.name = None
		self.types = [ ]
		self.showNag = None

	def getName(self):
		"""Returns the user name.

		@return: a string containing the user name
		"""
		return self.name

	def setName(self, name):
		"""Sets the user name.

		@param name: a string containing the user name
		"""
		self.name = name

	def getTypes(self):
		"""Returns the types of this user.

		Most users' type list is empty. Currently, the following types
		are defined:

		 - 'http://musicbrainz.org/ns/ext-1.0#AutoEditor'
		 - 'http://musicbrainz.org/ns/ext-1.0#RelationshipEditor'
		 - 'http://musicbrainz.org/ns/ext-1.0#Bot'
		 - 'http://musicbrainz.org/ns/ext-1.0#NotNaggable'

		@return: a list of strings containing absolute URIs
		"""
		return self.types

	def addType(self, type_):
		"""Add a type to the list of types.

		@param type_: a string containing absolute URIs

		@see: L{getTypes}
		"""
		self.types.append(type_)

	def getShowNag(self):
		"""Returns true if a nag screen should be displayed to the user.

		@return: C{True}, C{False}, or None
		"""
		return self.showNag

	def setShowNag(self, value):
		"""Sets the value of the nag screen flag.

		If set to C{True}, 

		@param value: C{True} or C{False}

		@see: L{getShowNag}
		"""
		self.showNag = value


# EOF
