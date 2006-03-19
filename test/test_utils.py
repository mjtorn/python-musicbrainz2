"""Tests for the utils module."""
import unittest
from musicbrainz2.model import NS_MMD_1
from musicbrainz2.utils import extractUuid, extractFragment

class UtilsTest(unittest.TestCase):
	
	def __init__(self, name):
		unittest.TestCase.__init__(self, name)


	def testExtractUuid(self):
		artistPrefix = 'http://musicbrainz.org/artist/'
		uuid = 'c0b2500e-0cef-4130-869d-732b23ed9df5'
		mbid = artistPrefix + uuid

		self.assertEquals(extractUuid(None), None)
		self.assertEquals(extractUuid(uuid), uuid)
		self.assertEquals(extractUuid(mbid), uuid)
		self.assertEquals(extractUuid(mbid, 'artist'), uuid)

		# not correct, but not enough data to catch this
		self.assertEquals(extractUuid(uuid, 'release'), uuid)

		self.assertRaises(ValueError, extractUuid, mbid, 'release')
		self.assertRaises(ValueError, extractUuid, mbid, 'track')
		self.assertRaises(ValueError, extractUuid, mbid+'/xy', 'artist')

		invalidId = 'http://example.invalid/' + uuid
		self.assertRaises(ValueError, extractUuid, invalidId)


	def testExtractFragment(self):
		fragment = 'Album'
		uri = NS_MMD_1 + fragment

		self.assertEquals(extractFragment(None), None)
		self.assertEquals(extractFragment(fragment), fragment)
		self.assertEquals(extractFragment(uri), fragment)
		self.assertEquals(extractFragment(uri, NS_MMD_1), fragment)

		prefix = 'http://example.invalid/'
		self.assertRaises(ValueError, extractFragment, uri, prefix)

# EOF
