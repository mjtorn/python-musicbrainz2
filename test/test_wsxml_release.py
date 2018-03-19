"""Tests for parsing releases using MbXmlParser."""
import unittest
from musicbrainz2.wsxml import MbXmlParser, ParseError
from musicbrainz2.model import VARIOUS_ARTISTS_ID, NS_MMD_1, \
	Relation, ReleaseEvent
import io
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

		self.assertFalse( release is None )
		self.assertEqual(release.getId(),
			makeId('02232360-337e-4a3f-ad20-6cdd4c34288c'))
		self.assertEqual(release.getTitle(), 'Little Earthquakes')
		self.assertEqual(release.getTextLanguage(), 'ENG')
		self.assertEqual(release.getTextScript(), 'Latn')

		self.assertEqual(len(release.getTypes()), 2)
		self.assertTrue(NS_MMD_1 + 'Album' in release.getTypes())
		self.assertTrue(NS_MMD_1 + 'Official' in release.getTypes())


	def testReleaseFull(self):
		f = os.path.join(VALID_RELEASE_DIR, 'Little_Earthquakes_2.xml')
		md = MbXmlParser().parse(f)
		release = md.getRelease()

		self.assertFalse( release is None )
		self.assertEqual(release.getId(),
			makeId('02232360-337e-4a3f-ad20-6cdd4c34288c'))

		self.assertEqual(release.getArtist().getName(), 'Tori Amos')

		events = release.getReleaseEventsAsDict()
		self.assertEqual(len(events), 3)
		self.assertEqual(events['GB'], '1992-01-13')
		self.assertEqual(events['DE'], '1992-01-17')
		self.assertEqual(events['US'], '1992-02-25')

		date = release.getEarliestReleaseDate()
		self.assertEqual(date, '1992-01-13')
		event = release.getEarliestReleaseEvent()
		self.assertEqual(event.date, date)
		self.assertEqual(event.country, 'GB')

		discs = release.getDiscs()
		self.assertEqual(len(discs), 3)
		self.assertEqual(discs[0].getId(), 'ILKp3.bZmvoMO7wSrq1cw7WatfA-')
		self.assertEqual(discs[1].getId(), 'ejdrdtX1ZyvCb0g6vfJejVaLIK8-')
		self.assertEqual(discs[2].getId(), 'Y96eDQZbF4Z26Y5.Sxdbh3wGypo-')

		tracks = release.getTracks()
		self.assertEqual(len(tracks), 12)
		self.assertEqual(tracks[0].getTitle(), 'Crucify')
		self.assertEqual(tracks[4].getTitle(), 'Winter')


	def testReleaseRelations(self):
		f = os.path.join(VALID_RELEASE_DIR, 'Highway_61_Revisited_1.xml')
		md = MbXmlParser().parse(f)
		release = md.getRelease()

		self.assertFalse( release is None )
		self.assertEqual(release.getId(),
			makeId('d61a2bd9-81ac-4023-bd22-1c884d4a176c'))

		(rel1, rel2) = release.getRelations(Relation.TO_URL)

		self.assertEqual(rel1.getTargetId(),
			'http://en.wikipedia.org/wiki/Highway_61_Revisited')
		self.assertEqual(rel1.getDirection(), Relation.DIR_NONE)
		self.assertEqual(rel2.getTargetId(),
			'http://www.amazon.com/gp/product/B0000024SI')


	def testVariousArtistsRelease(self):
		f = os.path.join(VALID_RELEASE_DIR, 'Mission_Impossible_2.xml')
		md = MbXmlParser().parse(f)
		release = md.getRelease()

		self.assertFalse( release is None )

		artistId = release.getArtist().getId()
		self.assertEqual(artistId, VARIOUS_ARTISTS_ID)

		events = release.getReleaseEventsAsDict()
		self.assertEqual(len(events), 1)
		self.assertEqual(events['EU'], '2000')

		track14 = release.getTracks()[14]
		self.assertEqual(track14.getTitle(), 'Carnival')
		self.assertEqual(track14.getArtist().getName(), 'Tori Amos')


	def testIncompleteReleaseEvent(self):
		f = os.path.join(VALID_RELEASE_DIR, 'Under_the_Pink_1.xml')
		md = MbXmlParser().parse(f)
		release = md.getRelease()

		self.assertFalse( release is None )
		self.assertEqual(release.getTitle(), 'Under the Pink')

		events = release.getReleaseEvents()
		self.assertEqual(len(events), 1)
		self.assertEqual(events[0].getDate(), '1994-01-28')


	def testReleaseEvents(self):
		f = os.path.join(VALID_RELEASE_DIR, 'Under_the_Pink_3.xml')
		md = MbXmlParser().parse(f)
		release = md.getRelease()

		self.assertFalse( release is None )
		self.assertEqual(release.getTitle(), 'Under the Pink')

		events = release.getReleaseEvents()
		self.assertEqual(len(events), 1)
		e1 = events[0]
		self.assertEqual(e1.date, '1994-01-31')
		self.assertEqual(e1.catalogNumber, '82567-2')
		self.assertEqual(e1.barcode, '07567825672')
		self.assertEqual(e1.format, ReleaseEvent.FORMAT_CD)

		self.assertFalse( e1.label is None )
		self.assertEqual(e1.label.name, 'Atlantic Records')

	def testReleaseGroup(self):
		f = os.path.join(VALID_RELEASE_DIR, 'Under_the_Pink_2.xml')
		md = MbXmlParser().parse(f)
		release = md.getRelease()

		self.assertFalse(release is None)
		self.assertEqual(release.getTitle(), 'Under the Pink')

		releaseGroup = release.getReleaseGroup()
		self.assertFalse(releaseGroup is None)
		self.assertEqual(releaseGroup.id[-36:],
			'ef2b891f-ca73-3e14-b38b-a68699dab8c4')
		self.assertEqual(releaseGroup.getTitle(), 'Under the Pink')
		self.assertEqual(releaseGroup.getType(), NS_MMD_1 + 'Album')


	def testTags(self):
		f = os.path.join(VALID_RELEASE_DIR, 'Highway_61_Revisited_2.xml')
		md = MbXmlParser().parse(f)
		release = md.getRelease()
		
		self.assertFalse( release is None )
		self.assertEqual(release.getTag('rock').count, 100)
		self.assertEqual(release.getTag('blues rock').count, 40)
		self.assertEqual(release.getTag('folk rock').count, 40)
		self.assertEqual(release.getTag('dylan').count, 4)
		

	def testResultAttributes(self):
		f = os.path.join(VALID_RELEASE_DIR, 'search_result_1.xml')
		md = MbXmlParser().parse(f)

		self.assertEqual(md.releaseResultsOffset, 0)
		self.assertEqual(md.releaseResultsCount, 234)


# EOF
