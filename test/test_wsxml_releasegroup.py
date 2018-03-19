"""Tests for parsing release groups using MbXmlParser."""
import unittest
from musicbrainz2.wsxml import MbXmlParser, MbXmlWriter, ParseError
from musicbrainz2.model import ReleaseGroup, NS_MMD_1
from io import StringIO
import os.path

VALID_DATA_DIR = os.path.join('test-data', 'valid')
# Only have tests for valid data, ATM.

RELEASEGROUP_DIR = os.path.join(VALID_DATA_DIR, 'release-group')

def makeId(relativeUri):
	return 'http://musicbrainz.org/release-group/' + relativeUri

class ParseReleaseGroupTest(unittest.TestCase):

	def testReleaseGroupBasic(self):
		f = os.path.join(RELEASEGROUP_DIR, 'The_Cure_1.xml')
		md = MbXmlParser().parse(f)
		releaseGroup = md.getReleaseGroup()
		
		self.assertFalse(releaseGroup is None)
		self.assertEqual(releaseGroup.getId(),
			makeId('c6a62b78-70f7-44f7-b159-064f6b7ba03a'))
		self.assertEqual(releaseGroup.getTitle(), 'The Cure')
		self.assertEqual(releaseGroup.getType(), NS_MMD_1 + 'Album')


	def testReleaseGroupFull(self):
		f = os.path.join(RELEASEGROUP_DIR, 'The_Cure_1.xml')
		md = MbXmlParser().parse(f)
		releaseGroup = md.getReleaseGroup()

		self.assertFalse(releaseGroup is None)

		releases = releaseGroup.getReleases()
		self.assertFalse(releases is None)
		self.assertEqual(len(releases), 4)

		# Check releases, which are in no particular order.
		expectedIds = [
			'd984e1a3-7281-46bb-ad8b-1478a00f2fbf',
			'c100a398-3132-48a8-a5fc-c3e908ac17dc',
			'24bec892-b21d-47d8-a288-dc6450152574',
			'61a4ec51-fa34-4757-85d7-83231776ed14']
		actualIds = [release.id[-36:] for release in releases]
		for expectedId in expectedIds:
			self.assertTrue(expectedId in actualIds)

		# Check artist
		self.assertEqual(releaseGroup.getArtist().getName(), 'The Cure')
		self.assertEqual(releaseGroup.getArtist().id[-36:],
			'69ee3720-a7cb-4402-b48d-a02c366f2bcf')


	def testSearchResults(self):
		f = os.path.join(RELEASEGROUP_DIR, 'search_result_1.xml')
		md = MbXmlParser().parse(f)
		releaseGroups = md.getReleaseGroupResults()

		self.assertFalse(releaseGroups is None)
		self.assertEqual(md.getReleaseGroupResultsOffset(), 0)
		self.assertEqual(md.getReleaseGroupResultsCount(), 3)

		expectedEntries = {
			'963eac15-e3da-3a92-aa5c-2ec23bfb6ec2': ['Signal Morning', 100],
			'0bd324a3-1c90-3bdb-8ca4-4101a580c62c': ['Circulatory System', 98],
			'ea7d8352-7751-30be-8490-bb6df737f47c': ['Inside Views', 90]}
		for result in releaseGroups:
			releaseGroup = result.releaseGroup
			self.assertFalse(releaseGroup is None)

			releaseGroupId = releaseGroup.id[-36:]
			self.assertTrue(releaseGroupId in expectedEntries)

			expectedTitle, expectedScore = expectedEntries[releaseGroupId]
			self.assertEqual(releaseGroup.title, expectedTitle)
			self.assertEqual(result.score, expectedScore)

			del expectedEntries[releaseGroupId]


	def testSerialize(self):
		# Get initial.
		f = os.path.join(RELEASEGROUP_DIR, 'The_Cure_1.xml')
		md1 = MbXmlParser().parse(f)

		# Serialize.
		outbuffer = StringIO()
		MbXmlWriter().write(outbuffer, md1)

		# Deserialize.
		inbuffer = StringIO(outbuffer.getvalue().encode('utf-8'))
		md2 = MbXmlParser().parse(inbuffer)

		# Check
		releaseGroup = md2.getReleaseGroup()

		self.assertFalse(releaseGroup is None)
		self.assertEqual(len(releaseGroup.getReleases()), 4)
		self.assertEqual(releaseGroup.getId(),
			makeId('c6a62b78-70f7-44f7-b159-064f6b7ba03a'))
		self.assertEqual(releaseGroup.getTitle(), 'The Cure')
		self.assertEqual(releaseGroup.getType(), NS_MMD_1 + 'Album')

	def testEmptyType(self):
		f = os.path.join(RELEASEGROUP_DIR, 'The_Cure_1.xml')
		md1 = MbXmlParser().parse(f)

		releaseGroup1 = md1.getReleaseGroup()
		releaseGroup1.setType(None)

		# Serialize.
		outbuffer = StringIO()
		MbXmlWriter().write(outbuffer, md1)

		inbuffer = StringIO(outbuffer.getvalue().encode('utf-8'))
		md2 = MbXmlParser().parse(inbuffer)

		# Check
		releaseGroup2 = md2.getReleaseGroup()

		self.assertFalse(releaseGroup2 is None)
		self.assertEqual(releaseGroup2.getType(), None)
