"""Tests for parsing artists using MbXmlParser."""
import unittest
from musicbrainz2.wsxml import MbXmlParser, ParseError
from musicbrainz2.model import NS_MMD_1
import StringIO
import os.path

VALID_DATA_DIR = os.path.join('test-data', 'valid')
INVALID_DATA_DIR = os.path.join('test-data', 'invalid')

VALID_ARTIST_DIR = os.path.join(VALID_DATA_DIR, 'artist')

def makeId(relativeUri, resType='artist'):
	return 'http://musicbrainz.org/%s/%s' % (resType, relativeUri)

class ParseArtistTest(unittest.TestCase):

	def __init__(self, name):
		unittest.TestCase.__init__(self, name)


	def testArtistBasic(self):
		f = os.path.join(VALID_ARTIST_DIR, 'Tori_Amos_1.xml')
		md = MbXmlParser().parse(f)
		artist = md.getArtist()

		self.failIf( artist is None )
		self.assertEquals(artist.getName(), 'Tori Amos')
		self.assertEquals(artist.getSortName(), 'Amos, Tori')
		self.assertEquals(artist.getBeginDate(), '1963-08-22')
		self.assertEquals(len(artist.getReleases()), 0)


	def testArtistFull(self):
		f = os.path.join(VALID_ARTIST_DIR, 'Tori_Amos_2.xml')
		md = MbXmlParser().parse(f)
		artist = md.getArtist()

		self.failIf( artist is None )
		self.assertEquals(artist.getId(),
			makeId('c0b2500e-0cef-4130-869d-732b23ed9df5'))
		self.assertEquals(artist.getName(), 'Tori Amos')
		self.assertEquals(artist.getSortName(), 'Amos, Tori')
		self.assert_(artist.getDisambiguation() is None)
		self.assertEquals(artist.getUniqueName(), artist.getName())
		self.assertEquals(artist.getBeginDate(), '1963-08-22')
		self.assertEquals(len(artist.getReleases()), 3)
		self.assertEquals(len(artist.getReleaseGroups()), 3)

		release1 = artist.getReleases()[0]
		self.assertEquals(release1.getTitle(), 'Strange Little Girls')
		self.assertEquals(release1.getAsin(), 'B00005NKYQ')

		# Check last release in more detail.
		#
		release3 = artist.getReleases()[2]
		self.assertEquals(release3.getId(),
			makeId('290e10c5-7efc-4f60-ba2c-0dfc0208fbf5', 'release'))
		self.assertEquals(len(release3.getTypes()), 2)
		self.assert_(NS_MMD_1 + 'Album' in release3.getTypes())
		self.assert_(NS_MMD_1 + 'Official' in release3.getTypes())
		self.assertEquals(release3.getTitle(), 'Under the Pink')
		self.assertEquals(release3.getAsin(), 'B000002IXU')
		self.assertEquals(release3.getArtist().getId(),
			makeId('c0b2500e-0cef-4130-869d-732b23ed9df5'))
		self.failIf(release3.getReleaseGroup() is None)
		self.assertEquals(release3.getReleaseGroup().id[-36:],
			'ef2b891f-ca73-3e14-b38b-a68699dab8c4')

		events = release3.getReleaseEvents()
		self.assertEquals(len(events), 5)
		self.assertEquals(events[0].getCountry(), 'DE')
		self.assertEquals(events[0].getDate(), '1994-01-28')
		self.assertEquals(events[4].getCountry(), 'AU')
		self.assertEquals(events[4].getDate(), '1994-11')

		self.assertEquals(release3.getEarliestReleaseDate(), '1994-01-28')

		#self.assertEquals(release3.getDiscCount(), 4)


	def testAliases(self):
		f = os.path.join(VALID_ARTIST_DIR, 'Tori_Amos_4.xml')
		md = MbXmlParser().parse(f)
		artist = md.getArtist()
		
		self.failIf( artist is None )
		self.assertEquals(artist.getDisambiguation(), 'yes, that one')
		self.assertEquals(artist.getName(), 'Tori Amos')
		self.assertEquals(artist.getUniqueName(),
			'Tori Amos (yes, that one)')

		aliases = artist.getAliases()
		self.assertEquals(len(aliases), 3)
		self.assertEquals(aliases[0].getValue(), 'Myra Ellen Amos')
		self.assertEquals(aliases[0].getScript(), 'Latn')
		self.assertEquals(aliases[1].getValue(), 'Myra Amos')
		self.assertEquals(aliases[2].getValue(), 'Torie Amos')
		self.assertEquals(aliases[2].getType(), NS_MMD_1 + 'Misspelling')


	def testTags(self):
		f = os.path.join(VALID_ARTIST_DIR, 'Tchaikovsky-2.xml')
		md = MbXmlParser().parse(f)
		artist = md.getArtist()
		
		self.failIf( artist is None )
		self.assertEquals(artist.getTag('classical').count, 100)
		self.assertEquals(artist.getTag('russian').count, 60)
		self.assertEquals(artist.getTag('romantic era').count, 40)
		self.assertEquals(artist.getTag('composer').count, 120)
		
	
	def testReleaseGroups(self):
		f = os.path.join(VALID_ARTIST_DIR, 'Tori_Amos_2.xml')
		md = MbXmlParser().parse(f)
		artist = md.getArtist()

		self.failIf(artist is None)
		releaseGroups = artist.getReleaseGroups()
		self.failIf(releaseGroups is None)
		self.assertEquals(len(releaseGroups), 3)

		expectedEntries = {
			'ef2b891f-ca73-3e14-b38b-a68699dab8c4': 'Under the Pink',
			'1fd43909-8056-3805-b2f9-c663ce7e71e6': 'To Venus and Back',
			'a69a1574-dfe3-3e2a-b499-d26d5e916041': 'Strange Little Girls'}

		for releaseGroup in releaseGroups:
			self.assertEquals(releaseGroup.getType(), NS_MMD_1 + 'Album')
			releaseGroupId = releaseGroup.id[-36:]
			self.assert_(releaseGroupId in expectedEntries)
			self.assertEquals(releaseGroup.getTitle(), expectedEntries[releaseGroupId])
			del expectedEntries[releaseGroupId]


	def testSearchResults(self):
		f = os.path.join(VALID_ARTIST_DIR, 'search_result_1.xml')
		md = MbXmlParser().parse(f)

		self.assertEquals(md.artistResultsOffset, 0)
		self.assertEquals(md.artistResultsCount, 47)

		results = md.artistResults
		self.assertEquals(len(results), 3)

		self.assertEquals(results[0].score, 100)
		artist1 = results[0].artist
		self.assertEquals(artist1.name, 'Tori Amos')

# EOF
