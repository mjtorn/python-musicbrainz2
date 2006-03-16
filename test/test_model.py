"""Tests for various model classes."""
import unittest
from musicbrainz2.model import Artist, Release, Track, Relation

class MiscModelTest(unittest.TestCase):
	
	def __init__(self, name):
		unittest.TestCase.__init__(self, name)

	def testAddRelation(self):
		rel = Relation('Producer', Relation.TO_RELEASE, 'al_id')
		artist = Artist('ar_id', 'Tori Amos', 'Person')
		artist.addRelation(rel)

		rel2 = artist.getRelations(Relation.TO_RELEASE)[0]
		self.assertEquals(rel.getType(), rel2.getType())
		self.assertEquals(rel.getTargetType(), rel2.getTargetType())
		self.assertEquals(rel.getTargetId(), rel2.getTargetId())
		self.assertEquals(rel.getAttributes(), rel2.getAttributes())
		self.assertEquals(rel.getBeginDate(), rel2.getBeginDate())
		self.assertEquals(rel.getEndDate(), rel2.getEndDate())

		self.assertEquals(artist.getRelationTargetTypes(),
			[ Relation.TO_RELEASE ])

		# works because we only have one relation
		self.assertEquals(artist.getRelations(),
			artist.getRelations(Relation.TO_RELEASE))

	def testTrackDuration(self):
		t = Track()
		self.assert_( t.getDuration() is None )
		self.assert_( t.getDurationSplit() == (0, 0) )
		t.setDuration(0)
		self.assert_( t.getDurationSplit() == (0, 0) )
		t.setDuration(218666)
		self.assert_( t.getDurationSplit() == (3, 39) )

	def testReleaseIsSingleArtist(self):
		r = Release()
		r.setArtist(Artist(id_=1))
		r.addTrack(Track())
		r.addTrack(Track())
		self.assert_( r.isSingleArtistRelease() )

		r.getTracks()[0].setArtist(Artist(id_=7))
		r.getTracks()[1].setArtist(Artist(id_=8))
		self.assert_( r.isSingleArtistRelease() == False )

		r.getTracks()[0].setArtist(Artist(id_=1))
		r.getTracks()[1].setArtist(Artist(id_=1))
		self.assert_( r.isSingleArtistRelease() )

