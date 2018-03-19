"""Tests for parsing artists using MbXmlParser."""
import unittest
from musicbrainz2.wsxml import MbXmlParser, ParseError
from musicbrainz2.model import NS_MMD_1
import io
import os.path

VALID_DATA_DIR = os.path.join('test-data', 'valid')
INVALID_DATA_DIR = os.path.join('test-data', 'invalid')

VALID_LABEL_DIR = os.path.join(VALID_DATA_DIR, 'label')

def makeId(relativeUri, resType='label'):
	return 'http://musicbrainz.org/%s/%s' % (resType, relativeUri)


class ParseLabelTest(unittest.TestCase):

	def __init__(self, name):
		unittest.TestCase.__init__(self, name)


	def testLabelBasic(self):
		f = os.path.join(VALID_LABEL_DIR, 'Atlantic_Records_1.xml')
		md = MbXmlParser().parse(f)
		label = md.getLabel()

		self.assertFalse( label is None )
		self.assertEqual(label.id,
			makeId('50c384a2-0b44-401b-b893-8181173339c7'))
		self.assertEqual(label.type, NS_MMD_1 + 'OriginalProduction')
		self.assertEqual(label.name, 'Atlantic Records')
		self.assertEqual(label.beginDate, '1947')
		self.assertEqual(label.endDate, None)
		self.assertEqual(label.country, 'US')
		self.assertEqual(label.code, '121')


	def testIncomplete(self):
		f = os.path.join(VALID_LABEL_DIR, 'Atlantic_Records_3.xml')
		md = MbXmlParser().parse(f)
		label = md.getLabel()

		self.assertFalse( label is None )
		self.assertEqual(label.id,
			makeId('50c384a2-0b44-401b-b893-8181173339c7'))
		self.assertEqual(label.code, None)


	def testLabelSubElements(self):
		f = os.path.join(VALID_LABEL_DIR, 'Atlantic_Records_2.xml')
		md = MbXmlParser().parse(f)
		label = md.getLabel()

		self.assertFalse( label is None )
		self.assertEqual(label.type, NS_MMD_1 + 'Distributor')
		self.assertEqual(label.name, 'Atlantic Records')
		self.assertEqual(label.sortName, 'AR SortName')
		self.assertEqual(label.disambiguation, 'fake')
		self.assertEqual(label.beginDate, '1947')
		self.assertEqual(label.endDate, '2047')
		self.assertEqual(label.country, 'US')
		self.assertEqual(label.code, '121')
		self.assertEqual(len(label.aliases), 1)

		alias = label.aliases[0]
		self.assertEqual(alias.value, 'Atlantic Rec.')

		self.assertEqual(label.getUniqueName(),
			'Atlantic Records (fake)')


	def testTags(self):
		f = os.path.join(VALID_LABEL_DIR, 'Atlantic_Records_3.xml')
		md = MbXmlParser().parse(f)
		label = md.getLabel()
		
		self.assertFalse( label is None )
		self.assertEqual(label.getTag('american').count, None)
		self.assertEqual(label.getTag('jazz').count, None)
		self.assertEqual(label.getTag('blues').count, None)


	def testSearchResults(self):
		f = os.path.join(VALID_LABEL_DIR, 'search_result_1.xml')
		md = MbXmlParser().parse(f)

		self.assertEqual(md.labelResultsOffset, 0)
		self.assertEqual(md.labelResultsCount, 2)
		self.assertEqual(md.getLabelResultsOffset(), 0)
		self.assertEqual(md.getLabelResultsCount(), 2)

		results = md.labelResults
		self.assertEqual(len(results), 2)

		self.assertEqual(results[0].score, 100)
		label1 = results[0].label
		self.assertEqual(label1.name, 'Atlantic Records')

		self.assertEqual(results[1].score, 46)
		label2 = results[1].label
		self.assertEqual(label2.name, 'DRO Atlantic')

# EOF
