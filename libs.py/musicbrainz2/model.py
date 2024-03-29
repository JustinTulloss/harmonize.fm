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

@see: L{musicbrainz2.webservice}

@author: Matthias Friedrich <matt@mafr.de>
"""
from sets import Set

__revision__ = '$Id: model.py 9313 2007-08-10 09:44:50Z matt $'

__all__ = [
	'VARIOUS_ARTISTS_ID', 'NS_MMD_1', 'NS_REL_1', 'NS_EXT_1', 
	'Entity', 'Artist', 'Release', 'Track', 'User', 
	'Relation', 'Disc', 'ReleaseEvent', 'Label',
	'AbstractAlias', 'ArtistAlias', 'LabelAlias', 
]


VARIOUS_ARTISTS_ID = 'http://musicbrainz.org/artist/89ad4ac3-39f7-470e-963a-56509c546377'

# Namespace URI prefixes
#
NS_MMD_1 = 'http://musicbrainz.org/ns/mmd-1.0#'
NS_REL_1 = 'http://musicbrainz.org/ns/rel-1.0#'
NS_EXT_1 = 'http://musicbrainz.org/ns/ext-1.0#'


class Entity(object):
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

	 - L{Relation.TO_ARTIST}
	 - L{Relation.TO_RELEASE}
	 - L{Relation.TO_TRACK}
	 - L{Relation.TO_URL}

	@see: L{Relation}
	"""

	def __init__(self, id_=None):
		"""Constructor.

		This should only used by derived classes.

		@param id_: a string containing an absolute URI
		"""
		self._id = id_
		self._relations = { }

	def getId(self):
		"""Returns a MusicBrainz ID.

		@return: a string containing a URI, or None
		"""
		return self._id

	def setId(self, value):
		"""Sets a MusicBrainz ID.

		@param value: a string containing an absolute URI 
		"""
		self._id = value

	id = property(getId, setId, doc='The MusicBrainz ID.')

	def getRelations(self, targetType=None, relationType=None,
			requiredAttributes=(), direction=None):
		"""Returns a list of relations.

		If C{targetType} is given, only relations of that target
		type are returned. For MusicBrainz, the following target
		types are defined:
		 - L{Relation.TO_ARTIST}
		 - L{Relation.TO_RELEASE}
		 - L{Relation.TO_TRACK}
		 - L{Relation.TO_URL}

		If C{targetType} is L{Relation.TO_ARTIST}, for example,
		this method returns all relations between this Entity and
		artists.

		You may use the C{relationType} parameter to further restrict
		the selection. If it is set, only relations with the given
		relation type are returned. The C{requiredAttributes} sequence
		lists attributes that have to be part of all returned relations.

		If C{direction} is set, only relations with the given reading
		direction are returned. You can use the L{Relation.DIR_FORWARD},
		L{Relation.DIR_BACKWARD}, and L{Relation.DIR_BOTH} constants
		for this.

		@param targetType: a string containing an absolute URI, or None
		@param relationType: a string containing an absolute URI, or None
		@param requiredAttributes: a sequence containing absolute URIs
		@param direction: one of L{Relation}'s direction constants
		@return: a list of L{Relation} objects

		@see: L{Entity}
		"""
		allRels = [ ]
		if targetType is not None:
			allRels = self._relations.setdefault(targetType, [ ])
		else:
			for (k, relList) in self._relations.items():
				for rel in relList:
					allRels.append(rel)

		# Filter for direction.
		#
		if direction is not None:
			allRels = [r for r in allRels if r.getDirection() == direction]

		# Filter for relation type.
		#
		if relationType is None:
			return allRels
		else:
			allRels = [r for r in allRels if r.getType() == relationType]

		# Now filer for attribute type.
		#
		tmp = []
		required = Set(iter(requiredAttributes))

		for r in allRels:
			attrs = Set(iter(r.getAttributes()))
			if required.issubset(attrs):
				tmp.append(r)
		return tmp


	def getRelationTargets(self, targetType=None, relationType=None,
			requiredAttributes=(), direction=None):
		"""Returns a list of relation targets.

		The arguments work exactly like in L{getRelations}, but
		instead of L{Relation} objects, the matching relation
		targets are returned. This can be L{Artist}, L{Release},
		or L{Track} objects, depending on the relations.

		As a special case, URL strings are returned if the target
		is an URL.

		@param targetType: a string containing an absolute URI, or None
		@param relationType: a string containing an absolute URI, or None
		@param requiredAttributes: a sequence containing absolute URIs
		@param direction: one of L{Relation}'s direction constants
		@return: a list of objects, depending on the relation

		@see: L{getRelations}
		"""
		ret = [ ]
		rels =  self.getRelations(targetType, relationType,
			requiredAttributes, direction)

		for r in rels:
			if r.getTargetType() == Relation.TO_URL:
				ret.append(r.getTargetId())
			else:
				ret.append(r.getTarget())

		return ret


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
		l = self._relations.setdefault(relation.getTargetType(), [ ])
		l.append(relation)


	def getRelationTargetTypes(self):
		"""Returns a list of target types available for this entity.

		Use this to find out to which types of targets this entity
		has relations. If the entity only has relations to tracks and
		artists, for example, then a list containg the strings
		L{Relation.TO_TRACK} and L{Relation.TO_ARTIST} is returned.

		@return: a list of strings containing URIs

		@see: L{getRelations}
		"""
		return self._relations.keys()


class Artist(Entity):
	"""Represents an artist.

	Artists in MusicBrainz can have a type. Currently, this type can
	be either Person or Group for which the following URIs are assigned:

	 - C{http://musicbrainz.org/ns/mmd-1.0#Person}
	 - C{http://musicbrainz.org/ns/mmd-1.0#Group}

	Use the L{TYPE_PERSON} and L{TYPE_GROUP} constants for comparison.
	"""
	TYPE_PERSON = NS_MMD_1 + 'Person'
	TYPE_GROUP = NS_MMD_1 + 'Group'

	def __init__(self, id_=None, type_=None, name=None, sortName=None):
		"""Constructor.

		@param id_: a string containing an absolute URI
		@param type_: a string containing an absolute URI
		@param name: a string containing the artist's name
		@param sortName: a string containing the artist's sort name
		"""
		Entity.__init__(self, id_)
		self._type = type_
		self._name = name
		self._sortName = sortName
		self._disambiguation = None
		self._beginDate = None
		self._endDate = None
		self._aliases = [ ]
		self._releases = [ ]
		self._releasesCount = None
		self._releasesOffset = None

	def getType(self):
		"""Returns the artist's type.

		@return: a string containing an absolute URI, or None 
		"""
		return self._type

	def setType(self, type_):
		"""Sets the artist's type.

		@param type_: a string containing an absolute URI
		"""
		self._type = type_

	type = property(getType, setType, doc="The artist's type.")

	def getName(self):
		"""Returns the artist's name.

		@return: a string containing the artist's name, or None
		"""
		return self._name

	def setName(self, name):
		"""Sets the artist's name.

		@param name: a string containing the artist's name
		"""
		self._name = name

	name = property(getName, setName, doc="The artist's name.")

	def getSortName(self):
		"""Returns the artist's sort name.

		The sort name is the artist's name in a special format which
		is better suited for lexicographic sorting. The MusicBrainz
		style guide specifies this format.

		@see: U{The MusicBrainz Style Guidelines
			<http://musicbrainz.org/style.html>}
		"""
		return self._sortName

	def setSortName(self, sortName):
		"""Sets the artist's sort name.

		@param sortName: a string containing the artist's sort name

		@see: L{getSortName}
		"""
		self._sortName = sortName

	sortName = property(getSortName, setSortName,
		doc="The artist's sort name.")

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
		return self._disambiguation

	def setDisambiguation(self, disambiguation):
		"""Sets the disambiguation attribute.

		@param disambiguation: a disambiguation string

		@see: L{getDisambiguation}, L{getUniqueName}
		"""
		self._disambiguation = disambiguation

	disambiguation = property(getDisambiguation, setDisambiguation,
		doc="The disambiguation comment.")

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
		return self._beginDate

	def setBeginDate(self, dateStr):
		"""Sets the begin/foundation date.

		@param dateStr: a date string

		@see: L{getBeginDate}
		"""
		self._beginDate = dateStr

	beginDate = property(getBeginDate, setBeginDate,
		doc="The begin/foundation date.")

	def getEndDate(self):
		"""Returns the death/dissolving date.

		The definition of the I{end date} depends on the artist's
		type. For persons, this is the day of death, for groups it
		is the day the group was dissolved.

		@return: a string containing a date, or None

		@see: L{getBeginDate}
		"""
		return self._endDate

	def setEndDate(self, dateStr):
		"""Sets the death/dissolving date.

		@param dateStr: a string containing a date

		@see: L{setEndDate}, L{getBeginDate}
		"""
		self._endDate = dateStr

	endDate = property(getEndDate, setEndDate,
		doc="The death/dissolving date.")

	def getAliases(self):
		"""Returns the list of aliases for this artist.

		@return: a list of L{ArtistAlias} objects
		"""
		return self._aliases

	aliases = property(getAliases, doc='The list of aliases.')

	def addAlias(self, alias):
		"""Adds an alias for this artist.
		
		@param alias: an L{ArtistAlias} object
		"""
		self._aliases.append(alias)

	def getReleases(self):
		"""Returns a list of releases from this artist.

		This may also include releases where this artist isn't the
		I{main} artist but has just contributed one or more tracks
		(aka VA-Releases).

		@return: a list of L{Release} objects
		"""
		return self._releases

	releases = property(getReleases, doc='The list of releases')

	def addRelease(self, release):
		"""Adds a release to this artist's list of releases.

		@param release: a L{Release} object
		"""
		self._release.append(release)

	def getReleasesOffset(self):
		"""Returns the offset of the release list.

		This is used if the release list is incomplete (ie. the web
		service only returned part of the release for this artist).
		Note that the offset value is zero-based, which means release
		C{0} is the first release.

		@return: an integer containing the offset, or None

		@see: L{getReleases}, L{getReleasesCount}
		"""
		return self._releasesOffset

	def setReleasesOffset(self, offset):
		"""Sets the offset of the release list.

		@param offset: an integer containing the offset, or None

		@see: L{getReleasesOffset}
		"""
		self._releasesOffset = offset

	releasesOffset = property(getReleasesOffset, setReleasesOffset,
		doc='The offset of the release list.')

	def getReleasesCount(self):
		"""Returns the number of existing releases.
	
		This may or may not match with the number of elements that
		L{getReleases} returns. If the count is higher than
		the list, it indicates that the list is incomplete.

		@return: an integer containing the count, or None

		@see: L{setReleasesCount}, L{getReleasesOffset}
		"""
		return self._releasesCount

	def setReleasesCount(self, value):
		"""Sets the number of existing releases.

		@param value: an integer containing the count, or None

		@see: L{getReleasesCount}, L{setReleasesOffset}
		"""
		self._releasesCount = value

	releasesCount = property(getReleasesCount, setReleasesCount,
		doc='The total number of releases')


class Label(Entity):
	"""Represents a record label.
	
	A label within MusicBrainz is an L{Entity}. It contains information
	about the label like when it was established, its name, label code and
	other relationships. All release events may be assigned a label.
	"""
	TYPE_UNKNOWN = NS_MMD_1 + 'Unknown'
	
	TYPE_DISTRIBUTOR = NS_MMD_1 + 'Distributor'
	TYPE_HOLDING = NS_MMD_1 + 'Holding'
	TYPE_PRODUCTION = NS_MMD_1 + 'Production'
	
	TYPE_ORIGINAL = NS_MMD_1 + 'OriginalProduction'
	TYPE_BOOTLEG = NS_MMD_1 + 'BootlegProduction'
	TYPE_REISSUE = NS_MMD_1 + 'ReissueProduction'
	
	def __init__(self, id_=None):
		"""Constructor.

		@param id_: a string containing an absolute URI
		"""
		Entity.__init__(self, id_)
		self._type = None
		self._name = None
		self._sortName = None
		self._disambiguation = None
		self._countryId = None
		self._code = None
		self._beginDate = None
		self._endDate = None
		self._aliases = [ ]
	
	def getType(self):
		"""Returns the type of this label.

		@return: a string containing an absolute URI
		"""
		return self._type
	
	def setType(self, type_):
		"""Sets the type of this label.
		
		@param type_: A string containing the absolute URI of the type of label.
		"""
		self._type = type_
	
	type = property(getType, setType, doc='The type of label')
	
	def getName(self):
		"""Returns a string with the name of the label.

		@return: a string containing the label's name, or None
		"""
		return self._name
	
	def setName(self, name):
		"""Sets the name of this label.
		
		@param name: A string containing the name of the label
		"""
		self._name = name
		
	name = property(getName, setName, doc='The name of the label.')
	
	def getSortName(self):
		"""Returns the label's sort name.

		The sort name is the label's name in a special format which
		is better suited for lexicographic sorting. The MusicBrainz
		style guide specifies this format.

		@see: U{The MusicBrainz Style Guidelines
			<http://musicbrainz.org/style.html>}
		"""
		return self._sortName

	def setSortName(self, sortName):
		"""Sets the label's sort name.

		@param sortName: a string containing the label's sort name

		@see: L{getSortName}
		"""
		self._sortName = sortName

	sortName = property(getSortName, setSortName,
		doc="The label's sort name.")

	def getDisambiguation(self):
		"""Returns the disambiguation attribute.

		This attribute may be used if there is more than one label
		with the same name. In this case, disambiguation attributes
		are added to the labels' names to keep them apart.

		@return: a disambiguation string, or None

		@see: L{getUniqueName}
		"""
		return self._disambiguation

	def setDisambiguation(self, disambiguation):
		"""Sets the disambiguation attribute.

		@param disambiguation: a disambiguation string

		@see: L{getDisambiguation}, L{getUniqueName}
		"""
		self._disambiguation = disambiguation

	disambiguation = property(getDisambiguation, setDisambiguation,
		doc="The disambiguation comment.")

	def getUniqueName(self):
		"""Returns a unique label name (using disambiguation).

		This method returns the label's name together with the
		disambiguation attribute in parenthesis if it exists.

		@return: a string containing the unique name

		@see: L{getDisambiguation}
		"""
		d = self.getDisambiguation() 
		if d is not None and d.strip() != '':
			return '%s (%s)' % (self.getName(), d)
		else: 
			return self.getName()

	def getBeginDate(self):
		"""Returns the date this label was established.
		
		@return: A string contained the start date, or None
		"""
		return self._beginDate
	
	def setBeginDate(self, date):
		"""Set the date this label was established.
		
		@param date: A string in the format of YYYY-MM-DD
		"""
		self._beginDate = date
	
	beginDate = property(getBeginDate, setBeginDate,
		doc='The date this label was established.')

	def getEndDate(self):
		"""Returns the date this label closed.

		The returned date has the format 'YYYY', 'YYYY-MM', or 
		'YYYY-MM-DD', depending on how much detail is known.
		
		@return: A string containing the date, or None
		"""
		return self._endDate
	
	def setEndDate(self, date):
		"""Set the date this label closed.

		The date may have the format 'YYYY', 'YYYY-MM', or 
		'YYYY-MM-DD', depending on how much detail is known.
		
		@param date: A string containing the date, or None
		"""
		self._endDate = date
	
	endDate = property(getEndDate, setEndDate,
		doc='The date this label closed.')
		
	def getCountry(self):
		"""Returns the country the label is located.

		@return: a string containing an ISO-3166 country code, or None

		@see: L{musicbrainz2.utils.getCountryName}
		"""
		return self._countryId

	def setCountry(self, country):
		"""Sets the country the label is located.

		@param country: a string containing an ISO-3166 country code
		"""
		self._countryId = country

	country = property(getCountry, setCountry,
		doc='The country the label is located.')

	def getCode(self):
		"""Returns the label code.

		Label codes have been introduced by the IFPI (International
		Federation of Phonogram and Videogram Industries) to uniquely
		identify record labels. The label code consists of 'LC-' and 4
		figures (currently being extended to 5 figures).

		@return: a string containing the label code, or None
		"""
		return self._code

	def setCode(self, code):
		"""Sets the label code.

		@param code: a string containing the label code
		"""
		self._code = code

	code = property(getCode, setCode,
		doc='The label code.')

	def getAliases(self):
		"""Returns the list of aliases for this label.

		@return: a list of L{LabelAlias} objects
		"""
		return self._aliases

	aliases = property(getAliases, doc='The list of aliases.')

	def addAlias(self, alias):
		"""Adds an alias for this label.
		
		@param alias: a L{LabelAlias} object
		"""
		self._aliases.append(alias)


class Release(Entity):
	"""Represents a Release.

	A release within MusicBrainz is an L{Entity} which contains L{Track}
	objects.  Releases may be of more than one type: There can be albums,
	singles, compilations, live recordings, official releases, bootlegs
	etc.

	@note: The current MusicBrainz server implementation supports only a
	limited set of types.
	"""
	# TODO: we need a type for NATs
	TYPE_NONE = NS_MMD_1 + 'None'

	TYPE_ALBUM = NS_MMD_1 + 'Album'
	TYPE_SINGLE = NS_MMD_1 + 'Single'
	TYPE_EP = NS_MMD_1 + 'EP'
	TYPE_COMPILATION = NS_MMD_1 + 'Compilation'
	TYPE_SOUNDTRACK = NS_MMD_1 + 'Soundtrack'
	TYPE_SPOKENWORD = NS_MMD_1 + 'Spokenword'
	TYPE_INTERVIEW = NS_MMD_1 + 'Interview'
	TYPE_AUDIOBOOK = NS_MMD_1 + 'Audiobook'
	TYPE_LIVE = NS_MMD_1 + 'Live'
	TYPE_REMIX = NS_MMD_1 + 'Remix'
	TYPE_OTHER = NS_MMD_1 + 'Other'

	TYPE_OFFICIAL = NS_MMD_1 + 'Official'
	TYPE_PROMOTION = NS_MMD_1 + 'Promotion'
	TYPE_BOOTLEG = NS_MMD_1 + 'Bootleg'
	TYPE_PSEUDO_RELEASE = NS_MMD_1 + 'Pseudo-Release'

	def __init__(self, id_=None, title=None):
		"""Constructor.

		@param id_: a string containing an absolute URI
		@param title: a string containing the title
		"""
		Entity.__init__(self, id_)
		self._types = [ ]
		self._title = title
		self._textLanguage = None
		self._textScript = None
		self._asin = None
		self._artist = None
		self._releaseEvents = [ ]
		#self._releaseEventsCount = None
		self._discs = [ ]
		#self._discIdsCount = None
		self._tracks = [ ]
		self._tracksOffset = None
		self._tracksCount = None


	def getTypes(self):
		"""Returns the types of this release.

		To test for release types, you can use the constants
		L{TYPE_ALBUM}, L{TYPE_SINGLE}, etc.

		@return: a list of strings containing absolute URIs

		@see: L{musicbrainz2.utils.getReleaseTypeName}
		"""
		return self._types

	types = property(getTypes, doc='The list of types for this release.')

	def addType(self, type_):
		"""Add a type to the list of types.

		@param type_: a string containing absolute URIs

		@see: L{getTypes}
		"""
		self._types.append(type_)

	def getTitle(self):
		"""Returns the release's title.

		@return: a string containing the release's title
		"""
		return self._title

	def setTitle(self, title):
		"""Sets the release's title.

		@param title: a string containing the release's title, or None
		"""
		self._title = title

	title = property(getTitle, setTitle, doc='The title of this release.')

	def getTextLanguage(self):
		"""Returns the language used in release and track titles.

		To represent the language, the ISO-639-2/T standard is used,
		which provides three-letter terminological language codes like
		'ENG', 'DEU', 'JPN', 'KOR', 'ZHO' or 'YID'.

		Note that this refers to release and track I{titles}, not
		lyrics.

		@return: a string containing the language code, or None

		@see: L{musicbrainz2.utils.getLanguageName}
		"""
		return self._textLanguage

	def setTextLanguage(self, language):
		"""Sets the language used in releaes and track titles.

		@param language: a string containing a language code

		@see: L{getTextLanguage}
		"""
		self._textLanguage = language

	textLanguage = property(getTextLanguage, setTextLanguage,
		doc='The language used in release and track titles.')

	def getTextScript(self):
		"""Returns the script used in release and track titles.

		To represent the script, ISO-15924 script codes are used.
		Valid codes are, among others: 'Latn', 'Cyrl', 'Hans', 'Hebr'

		Note that this refers to release and track I{titles}, not
		lyrics.

		@return: a string containing the script code, or None

		@see: L{musicbrainz2.utils.getScriptName}
		"""
		return self._textScript

	def setTextScript(self, script):
		"""Sets the script used in releaes and track titles.

		@param script: a string containing a script code

		@see: L{getTextScript}
		"""
		self._textScript = script

	textScript = property(getTextScript, setTextScript,
		doc='The script used in release and track titles.')

	def getAsin(self):
		"""Returns the amazon shop identifier (ASIN).

		The ASIN is a 10-letter code (except for books) assigned
		by Amazon, which looks like 'B000002IT2' or 'B00006I4YD'.

		@return: a string containing the ASIN, or None
		"""
		return self._asin

	def setAsin(self, asin):
		"""Sets the amazon shop identifier (ASIN).

		@param asin: a string containing the ASIN

		@see: L{getAsin}
		"""
		self._asin = asin

	asin = property(getAsin, setAsin, doc='The amazon shop identifier.')

	def getArtist(self):
		"""Returns the main artist of this release.

		@return: an L{Artist} object, or None
		"""
		return self._artist

	def setArtist(self, artist):
		"""Sets this release's main artist.

		@param artist: an L{Artist} object
		"""
		self._artist = artist

	artist = property(getArtist, setArtist,
		doc='The main artist of this release.')

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

		@see: L{getTracksOffset}, L{getTracksCount}
		"""
		return self._tracks

	tracks = property(getTracks, doc='The list of tracks.')

	def addTrack(self, track):
		"""Adds a track to this release.

		This appends a track at the end of this release's track list.

		@param track: a L{Track} object
		"""
		self._tracks.append(track)

	def getTracksOffset(self):
		"""Returns the offset of the track list.

		This is used if the track list is incomplete (ie. the web
		service only returned part of the tracks on this release).
		Note that the offset value is zero-based, which means track
		C{0} is the first track.

		@return: an integer containing the offset, or None

		@see: L{getTracks}, L{getTracksCount}
		"""
		return self._tracksOffset

	def setTracksOffset(self, offset):
		"""Sets the offset of the track list.

		@param offset: an integer containing the offset, or None

		@see: L{getTracksOffset}, L{setTracksCount}
		"""
		self._tracksOffset = offset

	tracksOffset = property(getTracksOffset, setTracksOffset,
		doc='The offset of the track list.')

	def getTracksCount(self):
		"""Returns the number of tracks on this release.
	
		This may or may not match with the number of elements that
		L{getTracks} returns. If the count is higher than
		the list, it indicates that the list is incomplete.

		@return: an integer containing the count, or None

		@see: L{setTracksCount}, L{getTracks}, L{getTracksOffset}
		"""
		return self._tracksCount

	def setTracksCount(self, value):
		"""Sets the number of tracks on this release.

		@param value: an integer containing the count, or None

		@see: L{getTracksCount}, L{setTracksOffset}
		"""
		self._tracksCount = value

	tracksCount = property(getTracksCount, setTracksCount,
		doc='The total number of releases')


	def getReleaseEvents(self):
		"""Returns the list of release events.

		A L{Release} may contain a list of so-called release events,
		each represented using a L{ReleaseEvent} object. Release
		evens specify where and when this release was, well, released.

		@return: a list of L{ReleaseEvent} objects

		@see: L{getReleaseEventsAsDict}
		"""
		return self._releaseEvents

	releaseEvents = property(getReleaseEvents,
		doc='The list of release events.')

	def addReleaseEvent(self, event):
		"""Adds a release event to this release.

		@param event: a L{ReleaseEvent} object

		@see: L{getReleaseEvents}
		"""
		self._releaseEvents.append(event)

	def getReleaseEventsAsDict(self):
		"""Returns the release events represented as a dict.

		Keys are ISO-3166 country codes like 'DE', 'UK', 'FR' etc.
		Values are dates in 'YYYY', 'YYYY-MM' or 'YYYY-MM-DD' format.

		@return: a dict containing (countryCode, date) entries

		@see: L{getReleaseEvents}, L{musicbrainz2.utils.getCountryName}
		"""
		d = { }
		for event in self.getReleaseEvents():
			d[event.getCountry()] = event.getDate()
		return d

	def getEarliestReleaseDate(self):
		"""Returns the earliest release date.

		This favours complete dates. For example, '2006-09' is
		returned if there is '2000', too. If there is no release
		event associated with this release, None is returned.

		@return: a string containing the date, or None 

		@see: L{getReleaseEvents}, L{getReleaseEventsAsDict}
		"""
		event = self.getEarliestReleaseEvent()

		if event is None:
			return None
		else:
			return event.getDate()

	def getEarliestReleaseEvent(self):
		"""Returns the earliest release event.

		This works like L{getEarliestReleaseDate}, but instead of
		just the date, this returns a L{ReleaseEvent} object.

		@return: a L{ReleaseEvent} object, or None 

		@see: L{getReleaseEvents}, L{getEarliestReleaseDate}
		"""
		dates = [ ]
		for event in self.getReleaseEvents():
			date = event.getDate()
			if len(date) == 10:    # 'YYYY-MM-DD'
				dates.append( (date, event) )
			elif len(date) == 7:   # 'YYYY-MM'
				dates.append( (date + '-99', event) )
			else:
				dates.append( (date + '-99-99', event) )

		dates.sort(lambda x, y: cmp(x[0], y[0]))

		if len(dates) > 0:
			return dates[0][1]
		else:
			return None


	#def getReleaseEventsCount(self):
	#	"""Returns the number of release events.
	#
	#	This may or may not match with the number of elements that
	#	getReleaseEvents() returns. If the count is higher than
	#	the list, it indicates that the list is incomplete.
	#	"""
	#	return self._releaseEventsCount

	#def setReleaseEventsCount(self, value):
	#	self._releaseEventsCount = value

	def getDiscs(self):
		"""Returns the discs associated with this release.

		Discs are currently containers for MusicBrainz DiscIDs.
		Note that under rare circumstances (identical TOCs), a
		DiscID could be associated with more than one release.

		@return: a list of L{Disc} objects
		"""
		return self._discs

	discs = property(getDiscs, doc='The list of associated discs.')

	def addDisc(self, disc):
		"""Adds a disc to this release.

		@param disc: a L{Disc} object
		"""
		self._discs.append(disc)

	#def getDiscIdsCount(self):
	#	return self._discIdsCount

	#def setDiscIdsCount(self, value):
	#	self._discIdsCount = value


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
		self._title = title
		self._artist = None
		self._duration = None
		self._puids = [ ]
		self._releases = [ ]

	def getTitle(self):
		"""Returns the track's title.

		The style and format of this attribute is specified by the
		style guide.

		@return: a string containing the title, or None

		@see: U{The MusicBrainz Style Guidelines
			<http://musicbrainz.org/style.html>}
		"""
		return self._title

	def setTitle(self, title):
		"""Sets the track's title.

		@param title: a string containing the title

		@see: L{getTitle}
		"""
		self._title = title

	title = property(getTitle, setTitle, doc="The track's title.")

	def getArtist(self):
		"""Returns the main artist of this track.

		@return: an L{Artist} object, or None
		"""
		return self._artist

	def setArtist(self, artist):
		"""Sets this track's main artist.

		@param artist: an L{Artist} object
		"""
		self._artist = artist

	artist = property(getArtist, setArtist, doc="The track's main artist.")

	def getDuration(self):
		"""Returns the duration of this track in milliseconds.

		@return: an int containing the duration in milliseconds, or None
		"""
		return self._duration

	def setDuration(self, duration):
		"""Sets the duration of this track in milliseconds.

		@param duration: an int containing the duration in milliseconds
		"""
		self._duration = duration

	duration = property(getDuration, setDuration,
		doc='The duration in milliseconds.')

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

	def getPuids(self):
		"""Returns the PUIDs associated with this track.

		Please note that a PUID may be associated with more than one
		track.

		@return: a list of strings, each containing one PUID
		"""
		return self._puids

	puids = property(getPuids, doc='The list of associated PUIDs.')

	def addPuid(self, puid):
		"""Add a PUID to this track.

		@param puid: a string containing a PUID
		"""
		self._puids.append(puid)

	def getReleases(self):
		"""Returns the list of releases this track appears on.

		@return: a list of L{Release} objects
		"""
		return self._releases

	releases = property(getReleases,
		doc='The releases on which this track appears.')

	def addRelease(self, release):
		"""Add a release on which this track appears.

		@param release: a L{Release} object
		"""
		self._releases.append(release)


class Relation(object):
	"""Represents a relation between two Entities.

	There may be an arbitrary number of relations between all first
	class objects in MusicBrainz. The Relation itself has multiple
	attributes, which may or may not be used for a given relation
	type.

	Note that a L{Relation} object only contains the target but not
	the source end of the relation.

	@todo: Add some examples.

	@cvar TO_ARTIST: Identifies relations linking to an artist.
	@cvar TO_RELEASE: Identifies relations linking to a release.
	@cvar TO_TRACK: Identifies relations linking to a track.
	@cvar TO_URL: Identifies relations linking to an URL.

	@cvar DIR_BOTH: Relation reading direction doesn't matter.
	@cvar DIR_FORWARD: Relation reading direction is from source to target.
	@cvar DIR_BACKWARD: Relation reading direction is from target to source.
	"""
	# Relation target types
	#
	TO_ARTIST = NS_REL_1 + 'Artist'
	TO_RELEASE = NS_REL_1 + 'Release'
	TO_TRACK = NS_REL_1 + 'Track'
	TO_URL = NS_REL_1 + 'Url'

	# Relation reading directions
	#
	DIR_BOTH = 'both'
	DIR_FORWARD = 'forward'
	DIR_BACKWARD = 'backward'

	def __init__(self, relationType=None, targetType=None, targetId=None,
			direction=DIR_BOTH, attributes=None,
			beginDate=None, endDate=None, target=None):
		"""Constructor.

		@param relationType: a string containing an absolute URI
		@param targetType: a string containing an absolute URI
		@param targetId: a string containing an absolute URI
		@param direction: one of C{Relation.DIR_FORWARD},
		C{Relation.DIR_BACKWARD}, or C{Relation.DIR_BOTH}
		@param attributes: a list of strings containing absolute URIs
		@param beginDate: a string containing a date
		@param endDate: a string containing a date
		@param target: an instance of a subclass of L{Entity}
		"""
		self._relationType = relationType
		self._targetType = targetType
		self._targetId = targetId
		self._direction = direction
		self._beginDate = beginDate
		self._endDate = endDate
		self._target = target
		self._attributes = attributes
		if self._attributes is None:
			self._attributes = [ ]

	def getType(self):
		"""Returns this relation's type.

		@return: a string containing an absolute URI, or None 
		"""
		return self._relationType

	def setType(self, type_):
		"""Sets this relation's type.

		@param type_: a string containing an absolute URI
		"""
		self._relationType = type_

	type = property(getType, setType, doc="The relation's type.")

	def getTargetId(self):
		"""Returns the target's ID.

		This is the ID the relation points to. It is an absolute
		URI, and in case of an URL relation, it is a URL.

		@return: a string containing an absolute URI
		"""
		return self._targetId

	def setTargetId(self, targetId):
		"""Sets the target's ID.

		@param targetId: a string containing an absolute URI

		@see: L{getTargetId}
		"""
		self._targetId = targetId

	targetId = property(getTargetId, setTargetId, doc="The target's ID.")

	def getTargetType(self):
		"""Returns the target's type.

		For MusicBrainz data, the following target types are defined:
		 - artists: L{Relation.TO_ARTIST}
		 - releases: L{Relation.TO_RELEASE}
		 - tracks: L{Relation.TO_TRACK}
		 - urls: L{Relation.TO_URL}

		@return: a string containing an absolute URI
		"""
		return self._targetType

	def setTargetType(self, targetType):
		"""Sets the target's type.

		@param targetType: a string containing an absolute URI

		@see: L{getTargetType}
		"""
		self._targetType = targetType

	targetId = property(getTargetId, setTargetId,
		doc="The type of target this relation points to.")

	def getAttributes(self):
		"""Returns a list of attributes describing this relation.

		The attributes permitted depend on the relation type.

		@return: a list of strings containing absolute URIs
		"""
		return self._attributes

	attributes = property(getAttributes,
		doc='The list of attributes describing this relation.')

	def addAttribute(self, attribute):
		"""Adds an attribute to the list.

		@param attribute: a string containing an absolute URI
		"""
		self._attributes.append(attribute)

	def getBeginDate(self):
		"""Returns the begin date.

		The definition depends on the relation's type. It may for
		example be the day of a marriage or the year an artist
		joined a band. For other relation types this may be
		undefined.

		@return: a string containing a date
		"""
		return self._beginDate

	def setBeginDate(self, dateStr):
		"""Sets the begin date.

		@param dateStr: a string containing a date

		@see: L{getBeginDate}
		"""
		self._beginDate = dateStr

	beginDate = property(getBeginDate, setBeginDate, doc="The begin date.")

	def getEndDate(self):
		"""Returns the end date.

		As with the begin date, the definition depends on the
		relation's type. Depending on the relation type, this may
		or may not be defined.

		@return: a string containing a date

		@see: L{getBeginDate}
		"""
		return self._endDate

	def setEndDate(self, dateStr):
		"""Sets the end date.

		@param dateStr: a string containing a date

		@see: L{getBeginDate}
		"""
		self._endDate = dateStr

	endDate = property(getEndDate, setEndDate, doc="The end date.")

	def getDirection(self):
		"""Returns the reading direction.

		The direction may be one of L{Relation.DIR_FORWARD},
		L{Relation.DIR_BACKWARD}, or L{Relation.DIR_BOTH},
		depending on how the relation should be read. For example,
		if direction is L{Relation.DIR_FORWARD} for a cover relation,
		it is read as "X is a cover of Y". Some relations are
		bidirectional, like marriages. In these cases, the direction
		is L{Relation.DIR_BOTH}.

		@return: L{Relation.DIR_FORWARD}, L{Relation.DIR_BACKWARD},
		or L{Relation.DIR_BOTH}
		"""
		return self._direction

	def setDirection(self, direction):
		"""Sets the reading direction.

		@param direction: L{Relation.DIR_FORWARD},
		L{Relation.DIR_BACKWARD}, or L{Relation.DIR_BOTH}

		@see: L{getDirection}
		"""
		self._direction = direction

	direction = property(getDirection, setDirection,
		doc="The reading direction.")

	def getTarget(self):
		"""Returns this relation's target object.

		Note that URL relations never have a target object. Use the
		L{getTargetId} method to get the URL.

		@return: a subclass of L{Entity}, or None
		"""
		return self._target

	def setTarget(self, target):
		"""Sets this relation's target object.

		Note that URL relations never have a target object, they
		are set using L{setTargetId}.

		@param target: a subclass of L{Entity}
		"""
		self._target = target

	target = property(getTarget, setTarget,
		doc="The relation's target object.")


class ReleaseEvent(object):
	"""A release event, indicating where and when a release took place.

	All country codes used must be valid ISO-3166 country codes (i.e. 'DE',
	'UK' or 'FR'). The dates are strings and must have the format 'YYYY',
	'YYYY-MM' or 'YYYY-MM-DD'.
	"""

	def __init__(self, country=None, dateStr=None):
		"""Constructor.

		@param country: a string containing an ISO-3166 country code
		@param dateStr: a string containing a date string
		"""
		self._countryId = country
		self._dateStr = dateStr
		self._catalogNumber = None
		self._barcode = None
		self._label = None

	def getCountry(self):
		"""Returns the country a release took place.

		@note: Due to a server limitation, the web service does not
		return country IDs for release collection queries. This only
		affects the L{musicbrainz2.webservice.Query.getReleases} query.

		@return: a string containing an ISO-3166 country code, or None

		@see: L{musicbrainz2.utils.getCountryName}
		"""
		return self._countryId

	def setCountry(self, country):
		"""Sets the country a release took place.

		@param country: a string containing an ISO-3166 country code
		"""
		self._countryId = country

	country = property(getCountry, setCountry,
		doc='The country a release took place.')

	def getCatalogNumber(self):
		"""Returns the catalog number of this release event.

		@return: A string containing the catalog number, or None
		"""
		return self._catalogNumber
	
	def setCatalogNumber(self, catalogNumber):
		"""Sets the catalog number of this release event.
		
		@param catalogNumber: A string containing the catalog number
		"""
		self._catalogNumber = catalogNumber
	
	catalogNumber = property(getCatalogNumber, setCatalogNumber,
		doc='The catalog number of the release event')
		
	def getBarcode(self):
		"""Returns the barcode of this release event.

		@return: A string containing the barcode, or None
		"""
		return self._barcode
	
	def setBarcode(self, barcode):
		"""Sets the barcode of this release event.
		
		@param barcode: A string containing the barcode
		"""
		self._barcode = barcode
	
	barcode = property(getBarcode, setBarcode,
		doc='The barcode of the release event')
		
	def getLabel(self):
		"""Returns a L{Label} object for the label associated with this release.
		
		@return: a L{Label} object, or None
		"""
		return self._label

	def setLabel(self, label):
		"""Sets the label of this release event.
		
		@param label: A L{Label} object
		"""
		self._label = label

	label = property(getLabel, setLabel, doc='The label of the release')

	def getDate(self):
		"""Returns the date a release took place.

		@return: a string containing a date
		"""
		return self._dateStr

	def setDate(self, dateStr):
		"""Sets the date a release took place.

		@param dateStr: a string containing a date
		"""
		self._dateStr = dateStr

	date = property(getDate, setDate, doc='The date a release took place.')



class Disc(object):
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
		self._id = id_
		self._sectors = None
		self._firstTrackNum = None
		self._lastTrackNum = None
		self._tracks = [ ]

	def getId(self):
		"""Returns the MusicBrainz DiscID.

		@return: a string containing a 28-character DiscID 
		"""
		return self._id

	def setId(self, id_):
		"""Sets the MusicBrainz DiscId.

		@param id_: a string containing a 28-character DiscID
		"""
		self._id = id_

	id = property(getId, setId, doc="The MusicBrainz DiscID.")

	def getSectors(self):
		"""Returns the length of the disc in sectors.

		@return: the length in sectors as an integer, or None
		"""
		return self._sectors

	def setSectors(self, sectors):
		"""Sets the length of the disc in sectors.

		@param sectors: the length in sectors as an integer
		"""
		self._sectors = sectors

	sectors = property(getSectors, setSectors,
		doc="The length of the disc in sectors.")

	def getFirstTrackNum(self):
		"""Returns the number of the first track on this disc.

		@return: an int containing the track number, or None
		"""
		return self._firstTrackNum

	def setFirstTrackNum(self, trackNum):
		"""Sets the number of the first track on this disc.

		@param trackNum: an int containing the track number, or None
		"""
		self._firstTrackNum = trackNum

	firstTrackNum = property(getFirstTrackNum, setFirstTrackNum,
		doc="The number of the first track on this disc.")

	def getLastTrackNum(self):
		"""Returns the number of the last track on this disc.

		@return: an int containing the track number, or None
		"""
		return self._lastTrackNum

	def setLastTrackNum(self, trackNum):
		"""Sets the number of the last track on this disc.

		@param trackNum: an int containing the track number, or None
		"""
		self._lastTrackNum = trackNum

	lastTrackNum = property(getLastTrackNum, setLastTrackNum,
		doc="The number of the last track on this disc.")

	def getTracks(self):
		"""Returns the sector offset and length of this disc.

		This method returns a list of tuples containing the track
		offset and length in sectors for all tracks on this disc.
		The track offset is measured from the beginning of the disc,
		the length is relative to the track's offset. Note that the
		leadout track is I{not} included.

		@return: a list of (offset, length) tuples (values are ints)
		"""
		return self._tracks

	tracks = property(getTracks,
		doc='Sector offset and length of all tracks.')

	def addTrack(self, track):
		"""Adds a track to the list.
		
		This method adds an (offset, length) tuple to the list of
		tracks. The leadout track must I{not} be added. The total
		length of the disc can be set using L{setSectors}.

		@param track: an (offset, length) tuple (values are ints)

		@see: L{getTracks}
		"""
		self._tracks.append(track)


class AbstractAlias(object):
	"""An abstract super class for all alias classes."""
	def __init__(self, value=None, type_=None, script=None):
		"""Constructor.

		@param value: a string containing the alias
		@param type_: a string containing an absolute URI
		@param script: a string containing an ISO-15924 script code
		"""
		self._value = value
		self._type = type_
		self._script = script

	def getValue(self):
		"""Returns the alias.

		@return: a string containing the alias
		"""
		return self._value

	def setValue(self, value):
		"""Sets the alias.

		@param value: a string containing the alias
		"""
		self._value = value

	value = property(getValue, setValue, doc='The alias value.')

	def getType(self):
		"""Returns the alias type.

		@return: a string containing an absolute URI, or None 
		"""
		return self._type

	def setType(self, type_):
		"""Sets the alias type.

		@param type_: a string containing an absolute URI, or None
		"""
		self._type = type_

	type = property(getType, setType, doc='The alias type.')

	def getScript(self):
		"""Returns the alias script.

		@return: a string containing an ISO-15924 script code
		"""
		return self._script

	def setScript(self, script):
		"""Sets the alias script.

		@param script: a string containing an ISO-15924 script code
		"""
		self._script = script

	script = property(getScript, setScript, doc='The alias script.')


class ArtistAlias(AbstractAlias):
	"""Represents an artist alias.

	An alias (the I{alias value}) is a different representation of an
	artist's name. This may be a common misspelling or a transliteration
	(the I{alias type}).

	The I{alias script} is interesting mostly for transliterations and
	indicates which script is used for the alias value. To represent the
	script, ISO-15924 script codes like 'Latn', 'Cyrl', or 'Hebr' are used.
	"""
	pass


class LabelAlias(AbstractAlias):
	"""Represents a label alias.

	An alias (the I{alias value}) is a different representation of a
	label's name. This may be a common misspelling or a transliteration
	(the I{alias type}).

	The I{alias script} is interesting mostly for transliterations and
	indicates which script is used for the alias value. To represent the
	script, ISO-15924 script codes like 'Latn', 'Cyrl', or 'Hebr' are used.
	"""
	pass


class User(object):
	"""Represents a MusicBrainz user."""

	def __init__(self):
		"""Constructor."""
		self._name = None
		self._types = [ ]
		self._showNag = None

	def getName(self):
		"""Returns the user name.

		@return: a string containing the user name
		"""
		return self._name

	def setName(self, name):
		"""Sets the user name.

		@param name: a string containing the user name
		"""
		self._name = name

	name = property(getName, setName, doc='The MusicBrainz user name.')

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
		return self._types

	types = property(getTypes, doc="The user's types.")

	def addType(self, type_):
		"""Add a type to the list of types.

		@param type_: a string containing absolute URIs

		@see: L{getTypes}
		"""
		self._types.append(type_)

	def getShowNag(self):
		"""Returns true if a nag screen should be displayed to the user.

		@return: C{True}, C{False}, or None
		"""
		return self._showNag

	def setShowNag(self, value):
		"""Sets the value of the nag screen flag.

		If set to C{True}, 

		@param value: C{True} or C{False}

		@see: L{getShowNag}
		"""
		self._showNag = value

	showNag = property(getShowNag, setShowNag,
		doc='The value of the nag screen flag.')

# EOF
