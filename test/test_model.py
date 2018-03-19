"""Tests for various model classes."""
import unittest
from musicbrainz2.model import Artist, Release, Track, Relation, Tag, NS_REL_1

class MiscModelTest(unittest.TestCase):
	
	def __init__(self, name):
		unittest.TestCase.__init__(self, name)

	def testAddRelation(self):
		rel = Relation(NS_REL_1+'Producer', Relation.TO_RELEASE, 'a_id',			attributes=[NS_REL_1+'Co'])
		artist = Artist('ar_id', 'Tori Amos', 'Person')
		artist.addRelation(rel)

		rel2 = artist.getRelations(Relation.TO_RELEASE)[0]
		self.assertEqual(rel.getType(), rel2.getType())
		self.assertEqual(rel.getTargetType(), rel2.getTargetType())
		self.assertEqual(rel.getTargetId(), rel2.getTargetId())
		self.assertEqual(rel.getAttributes(), rel2.getAttributes())
		self.assertEqual(rel.getBeginDate(), rel2.getBeginDate())
		self.assertEqual(rel.getEndDate(), rel2.getEndDate())

		self.assertEqual(artist.getRelationTargetTypes(),
			[ Relation.TO_RELEASE ])

		# works because we only have one relation
		self.assertEqual(artist.getRelations(),
			artist.getRelations(Relation.TO_RELEASE))

		rel3 = artist.getRelations(Relation.TO_RELEASE,
			NS_REL_1 + 'Producer')
		self.assertEqual(len(rel3), 1)

		rel4 = artist.getRelations(Relation.TO_RELEASE,
			NS_REL_1 + 'Producer', [NS_REL_1 + 'Co'])
		self.assertEqual(len(rel4), 1)

		rel5 = artist.getRelations(Relation.TO_RELEASE,
			NS_REL_1 + 'Producer', [NS_REL_1 + 'NotThere'])
		self.assertEqual(len(rel5), 0)

		rel6 = artist.getRelations(Relation.TO_RELEASE,
			NS_REL_1 + 'Producer', [NS_REL_1 + 'Co'], 'none')
		self.assertEqual(len(rel6), 1)

		rel6 = artist.getRelations(Relation.TO_RELEASE,
			NS_REL_1 + 'Producer', [NS_REL_1 + 'Co'], 'forward')
		self.assertEqual(len(rel6), 0)


	def testTrackDuration(self):
		t = Track()
		self.assertTrue( t.getDuration() is None )
		self.assertTrue( t.getDurationSplit() == (0, 0) )
		t.setDuration(0)
		self.assertTrue( t.getDurationSplit() == (0, 0) )
		t.setDuration(218666)
		self.assertTrue( t.getDurationSplit() == (3, 39) )

	def testReleaseIsSingleArtist(self):
		r = Release()
		r.setArtist(Artist(id_=1))
		r.addTrack(Track())
		r.addTrack(Track())
		self.assertTrue( r.isSingleArtistRelease() )

		r.getTracks()[0].setArtist(Artist(id_=7))
		r.getTracks()[1].setArtist(Artist(id_=8))
		self.assertTrue( r.isSingleArtistRelease() == False )

		r.getTracks()[0].setArtist(Artist(id_=1))
		r.getTracks()[1].setArtist(Artist(id_=1))
		self.assertTrue( r.isSingleArtistRelease() )

	def testTags(self):
		a = Artist()
		a.addTag(Tag('foo', 1))
		a.addTag(Tag('bar', 2))
		a.addTag(Tag('bar', 5))

		self.assertEqual(len(a.tags), 2)
		self.assertEqual(a.getTag('foo').count, 1)
		self.assertEqual(a.getTag('bar').count, 7)


class TagTest(unittest.TestCase):
	
	def test__str__(self):
		self.assertEqual("foo", str(Tag("foo")))
		self.assertRaises(UnicodeEncodeError, str, Tag("f\\u014do"))
	
	def test__unicode__(self):
		self.assertEqual("foo", str(Tag("foo")))
		self.assertEqual("f\\u014do", str(Tag("f\\u014do")))

class ArtistTest(unittest.TestCase):

    def testAddRelease(self):
        release = Release()
        artist = Artist()
        artist.addRelease(release)
        self.assertEqual(artist.releases, [release])

# EOF
