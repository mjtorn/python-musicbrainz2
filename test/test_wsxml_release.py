"""Tests for parsing releases using MbXmlParser."""
import unittest
from musicbrainz2.wsxml import MbXmlParser, ParseError
from musicbrainz2.model import VARIOUS_ARTISTS_ID, NS_MMD_1, RELATION_TO_URL
import StringIO
import os.path

VALID_DATA_DIR = os.path.join('test-data', 'valid')
INVALID_DATA_DIR = os.path.join('test-data', 'invalid')

VALID_RELEASE_DIR = os.path.join(VALID_DATA_DIR, 'release')

def makeId(relativeUri):
	return 'http://musicbrainz.org/release/' + relativeUri

class ParseReleaseTest(unittest.TestCase):

	def __init__(self, name):
		unittest.TestCase.__init__(self, name)


	def testReleaseBasic(self):
		f = os.path.join(VALID_RELEASE_DIR, 'Little_Earthquakes_1.xml')
		md = MbXmlParser().parse(f)
		release = md.getRelease()

		self.failIf( release is None )
		self.assertEquals(release.getId(),
			makeId('02232360-337e-4a3f-ad20-6cdd4c34288c'))
		self.assertEquals(release.getTitle(), 'Little Earthquakes')
		self.assertEquals(release.getTextLanguage(), 'ENG')
		self.assertEquals(release.getTextScript(), 'Latn')

		self.assertEquals(len(release.getTypes()), 2)
		self.assert_(NS_MMD_1 + 'Album' in release.getTypes())
		self.assert_(NS_MMD_1 + 'Official' in release.getTypes())


	def testReleaseFull(self):
		f = os.path.join(VALID_RELEASE_DIR, 'Little_Earthquakes_2.xml')
		md = MbXmlParser().parse(f)
		release = md.getRelease()

		self.failIf( release is None )
		self.assertEquals(release.getId(),
			makeId('02232360-337e-4a3f-ad20-6cdd4c34288c'))

		self.assertEquals(release.getArtist().getName(), 'Tori Amos')

		events = release.getReleaseEventsAsDict()
		self.assertEquals(len(events), 3)
		self.assertEquals(events['GB'], '1992-01-13')
		self.assertEquals(events['DE'], '1992-01-17')
		self.assertEquals(events['US'], '1992-02-25')

		discs = release.getDiscs()
		self.assertEquals(len(discs), 3)
		self.assertEquals(discs[0].getId(), 'ILKp3.bZmvoMO7wSrq1cw7WatfA-')
		self.assertEquals(discs[1].getId(), 'ejdrdtX1ZyvCb0g6vfJejVaLIK8-')
		self.assertEquals(discs[2].getId(), 'Y96eDQZbF4Z26Y5.Sxdbh3wGypo-')

		tracks = release.getTracks()
		self.assertEquals(len(tracks), 12)
		self.assertEquals(tracks[0].getTitle(), 'Crucify')
		self.assertEquals(tracks[4].getTitle(), 'Winter')


	def testReleaseRelations(self):
		f = os.path.join(VALID_RELEASE_DIR, 'Highway_61_Revisited_1.xml')
		md = MbXmlParser().parse(f)
		release = md.getRelease()

		self.failIf( release is None )
		self.assertEquals(release.getId(),
			makeId('d61a2bd9-81ac-4023-bd22-1c884d4a176c'))

		(rel1, rel2) = release.getRelations(RELATION_TO_URL)

		self.assertEquals(rel1.getTargetId(),
			'http://en.wikipedia.org/wiki/Highway_61_Revisited')
		self.assertEquals(rel2.getTargetId(),
			'http://www.amazon.com/gp/product/B0000024SI')


	def testVariousArtistsRelease(self):
		f = os.path.join(VALID_RELEASE_DIR, 'Mission_Impossible_2.xml')
		md = MbXmlParser().parse(f)
		release = md.getRelease()

		self.failIf( release is None )

		artistId = release.getArtist().getId()
		self.assertEquals(artistId, VARIOUS_ARTISTS_ID)

		track14 = release.getTracks()[14]
		self.assertEquals(track14.getTitle(), 'Carnival')
		self.assertEquals(track14.getArtist().getName(), 'Tori Amos')


# EOF
