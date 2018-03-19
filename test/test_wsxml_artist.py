"""Tests for parsing artists using MbXmlParser."""
import unittest
from musicbrainz2.wsxml import MbXmlParser, ParseError
from musicbrainz2.model import NS_MMD_1
import io
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

		self.assertFalse( artist is None )
		self.assertEqual(artist.getName(), 'Tori Amos')
		self.assertEqual(artist.getSortName(), 'Amos, Tori')
		self.assertEqual(artist.getBeginDate(), '1963-08-22')
		self.assertEqual(len(artist.getReleases()), 0)


	def testArtistFull(self):
		f = os.path.join(VALID_ARTIST_DIR, 'Tori_Amos_2.xml')
		md = MbXmlParser().parse(f)
		artist = md.getArtist()

		self.assertFalse( artist is None )
		self.assertEqual(artist.getId(),
			makeId('c0b2500e-0cef-4130-869d-732b23ed9df5'))
		self.assertEqual(artist.getName(), 'Tori Amos')
		self.assertEqual(artist.getSortName(), 'Amos, Tori')
		self.assertTrue(artist.getDisambiguation() is None)
		self.assertEqual(artist.getUniqueName(), artist.getName())
		self.assertEqual(artist.getBeginDate(), '1963-08-22')
		self.assertEqual(len(artist.getReleases()), 3)
		self.assertEqual(len(artist.getReleaseGroups()), 3)

		release1 = artist.getReleases()[0]
		self.assertEqual(release1.getTitle(), 'Strange Little Girls')
		self.assertEqual(release1.getAsin(), 'B00005NKYQ')

		# Check last release in more detail.
		#
		release3 = artist.getReleases()[2]
		self.assertEqual(release3.getId(),
			makeId('290e10c5-7efc-4f60-ba2c-0dfc0208fbf5', 'release'))
		self.assertEqual(len(release3.getTypes()), 2)
		self.assertTrue(NS_MMD_1 + 'Album' in release3.getTypes())
		self.assertTrue(NS_MMD_1 + 'Official' in release3.getTypes())
		self.assertEqual(release3.getTitle(), 'Under the Pink')
		self.assertEqual(release3.getAsin(), 'B000002IXU')
		self.assertEqual(release3.getArtist().getId(),
			makeId('c0b2500e-0cef-4130-869d-732b23ed9df5'))
		self.assertFalse(release3.getReleaseGroup() is None)
		self.assertEqual(release3.getReleaseGroup().id[-36:],
			'ef2b891f-ca73-3e14-b38b-a68699dab8c4')

		events = release3.getReleaseEvents()
		self.assertEqual(len(events), 5)
		self.assertEqual(events[0].getCountry(), 'DE')
		self.assertEqual(events[0].getDate(), '1994-01-28')
		self.assertEqual(events[4].getCountry(), 'AU')
		self.assertEqual(events[4].getDate(), '1994-11')

		self.assertEqual(release3.getEarliestReleaseDate(), '1994-01-28')

		#self.assertEquals(release3.getDiscCount(), 4)


	def testAliases(self):
		f = os.path.join(VALID_ARTIST_DIR, 'Tori_Amos_4.xml')
		md = MbXmlParser().parse(f)
		artist = md.getArtist()
		
		self.assertFalse( artist is None )
		self.assertEqual(artist.getDisambiguation(), 'yes, that one')
		self.assertEqual(artist.getName(), 'Tori Amos')
		self.assertEqual(artist.getUniqueName(),
			'Tori Amos (yes, that one)')

		aliases = artist.getAliases()
		self.assertEqual(len(aliases), 3)
		self.assertEqual(aliases[0].getValue(), 'Myra Ellen Amos')
		self.assertEqual(aliases[0].getScript(), 'Latn')
		self.assertEqual(aliases[1].getValue(), 'Myra Amos')
		self.assertEqual(aliases[2].getValue(), 'Torie Amos')
		self.assertEqual(aliases[2].getType(), NS_MMD_1 + 'Misspelling')


	def testTags(self):
		f = os.path.join(VALID_ARTIST_DIR, 'Tchaikovsky-2.xml')
		md = MbXmlParser().parse(f)
		artist = md.getArtist()
		
		self.assertFalse( artist is None )
		self.assertEqual(artist.getTag('classical').count, 100)
		self.assertEqual(artist.getTag('russian').count, 60)
		self.assertEqual(artist.getTag('romantic era').count, 40)
		self.assertEqual(artist.getTag('composer').count, 120)
		
	
	def testReleaseGroups(self):
		f = os.path.join(VALID_ARTIST_DIR, 'Tori_Amos_2.xml')
		md = MbXmlParser().parse(f)
		artist = md.getArtist()

		self.assertFalse(artist is None)
		releaseGroups = artist.getReleaseGroups()
		self.assertFalse(releaseGroups is None)
		self.assertEqual(len(releaseGroups), 3)

		expectedEntries = {
			'ef2b891f-ca73-3e14-b38b-a68699dab8c4': 'Under the Pink',
			'1fd43909-8056-3805-b2f9-c663ce7e71e6': 'To Venus and Back',
			'a69a1574-dfe3-3e2a-b499-d26d5e916041': 'Strange Little Girls'}

		for releaseGroup in releaseGroups:
			self.assertEqual(releaseGroup.getType(), NS_MMD_1 + 'Album')
			releaseGroupId = releaseGroup.id[-36:]
			self.assertTrue(releaseGroupId in expectedEntries)
			self.assertEqual(releaseGroup.getTitle(), expectedEntries[releaseGroupId])
			del expectedEntries[releaseGroupId]


	def testSearchResults(self):
		f = os.path.join(VALID_ARTIST_DIR, 'search_result_1.xml')
		md = MbXmlParser().parse(f)

		self.assertEqual(md.artistResultsOffset, 0)
		self.assertEqual(md.artistResultsCount, 47)

		results = md.artistResults
		self.assertEqual(len(results), 3)

		self.assertEqual(results[0].score, 100)
		artist1 = results[0].artist
		self.assertEqual(artist1.name, 'Tori Amos')

# EOF
