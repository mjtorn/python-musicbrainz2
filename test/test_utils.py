"""Tests for the utils module."""
import unittest
import musicbrainz2.model as m
import musicbrainz2.utils as u

class UtilsTest(unittest.TestCase):
	
	def __init__(self, name):
		unittest.TestCase.__init__(self, name)


	def testExtractUuid(self):
		artistPrefix = 'http://musicbrainz.org/artist/'
		uuid = 'c0b2500e-0cef-4130-869d-732b23ed9df5'
		mbid = artistPrefix + uuid

		self.assertEqual(u.extractUuid(None), None)
		self.assertEqual(u.extractUuid(uuid), uuid)
		self.assertEqual(u.extractUuid(mbid), uuid)
		self.assertEqual(u.extractUuid(mbid, 'artist'), uuid)

		# not correct, but not enough data to catch this
		self.assertEqual(u.extractUuid(uuid, 'release'), uuid)

		self.assertRaises(ValueError, u.extractUuid, mbid, 'release')
		self.assertRaises(ValueError, u.extractUuid, mbid, 'track')
		self.assertRaises(ValueError, u.extractUuid, mbid+'/xy', 'artist')

		invalidId = 'http://example.invalid/' + uuid
		self.assertRaises(ValueError, u.extractUuid, invalidId)


	def testExtractFragment(self):
		fragment = 'Album'
		uri = m.NS_MMD_1 + fragment

		self.assertEqual(u.extractFragment(None), None)
		self.assertEqual(u.extractFragment(fragment), fragment)
		self.assertEqual(u.extractFragment(uri), fragment)
		self.assertEqual(u.extractFragment(uri, m.NS_MMD_1), fragment)

		prefix = 'http://example.invalid/'
		self.assertRaises(ValueError, u.extractFragment, uri, prefix)


	def testExtractEntityType(self):
		prefix = 'http://musicbrainz.org'
		uuid = 'c0b2500e-0cef-4130-869d-732b23ed9df5'

		mbid1 = prefix + '/artist/' + uuid
		self.assertEqual(u.extractEntityType(mbid1), 'artist')

		mbid2 = prefix + '/release/' + uuid
		self.assertEqual(u.extractEntityType(mbid2), 'release')

		mbid3 = prefix + '/track/' + uuid
		self.assertEqual(u.extractEntityType(mbid3), 'track')

		mbid4 = prefix + '/label/' + uuid
		self.assertEqual(u.extractEntityType(mbid4), 'label')

		mbid5 = prefix + '/invalid/' + uuid
		self.assertRaises(ValueError, u.extractEntityType, mbid5)

		self.assertRaises(ValueError, u.extractEntityType, None)
		self.assertRaises(ValueError, u.extractEntityType, uuid)

		invalidUri = 'http://example.invalid/foo'
		self.assertRaises(ValueError, u.extractEntityType, invalidUri)
		

	def testGetCountryName(self):
		self.assertEqual(u.getCountryName('DE'), 'Germany')
		self.assertEqual(u.getCountryName('FR'), 'France')

	def testGetLanguageName(self):
		self.assertEqual(u.getLanguageName('DEU'), 'German')
		self.assertEqual(u.getLanguageName('ENG'), 'English')

	def testGetScriptName(self):
		self.assertEqual(u.getScriptName('Latn'), 'Latin')
		self.assertEqual(u.getScriptName('Cyrl'), 'Cyrillic')

	def testGetReleaseTypeName(self):
		self.assertEqual(u.getReleaseTypeName(m.Release.TYPE_ALBUM),
			'Album')
		self.assertEqual(u.getReleaseTypeName(m.Release.TYPE_COMPILATION), 'Compilation')

# EOF
