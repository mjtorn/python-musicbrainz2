"""Tests for parsing artists using MbXmlParser."""
import unittest
from musicbrainz2.wsxml import MbXmlParser, ParseError
from musicbrainz2.model import NS_MMD_1
import StringIO
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

		self.failIf( label is None )
		self.assertEquals(label.id,
			makeId('50c384a2-0b44-401b-b893-8181173339c7'))
		self.assertEquals(label.name, 'Atlantic Records')
		self.assertEquals(label.beginDate, '1947')
		self.assertEquals(label.endDate, None)

		# TODO: label type, code, country


	def testSearchResults(self):
		f = os.path.join(VALID_LABEL_DIR, 'search_result_1.xml')
		md = MbXmlParser().parse(f)

		self.assertEquals(md.labelResultsOffset, 0)
		self.assertEquals(md.labelResultsCount, 2)
		self.assertEquals(md.getLabelResultsOffset(), 0)
		self.assertEquals(md.getLabelResultsCount(), 2)

		results = md.labelResults
		self.assertEquals(len(results), 2)

		self.assertEquals(results[0].score, 100)
		label1 = results[0].label
		self.assertEquals(label1.name, 'Atlantic Records')

		self.assertEquals(results[1].score, 46)
		label2 = results[1].label
		self.assertEquals(label2.name, 'DRO Atlantic')

# EOF
