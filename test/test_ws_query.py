"""Tests for webservice.Query."""
import unittest
from musicbrainz2.model import Tag
from musicbrainz2.model import Rating
from musicbrainz2.model import Release
from musicbrainz2.webservice import Query, IWebService, AuthenticationError, RequestError


class FakeWebService(IWebService):

	def __init__(self):
		self.data = []

	def post(self, entity, id_, data, version='1'):
		self.data.append((entity, id_, data, version))
		
class FakeBadAuthWebService(IWebService):
	def post(self, entity, id_, data, version='1'):
		raise AuthenticationError()

class FakeBadRequestWebService(IWebService):
	def post(self, entity, id_, data, version='1'):
		raise RequestError()

class QueryTest(unittest.TestCase):

	def testAddToUserCollection(self):
		ws = FakeWebService()
		q = Query(ws)

		r1 = "9e186398-9ae2-45bf-a9f6-d26bc350221e"
		r2 = "http://musicbrainz.org/release/6b050dcf-7ab1-456d-9e1b-c3c41c18eed2"
		r3 = Release("d3cc336e-1010-4252-9091-7923f0429824")

		q.addToUserCollection([r1, r2, r3])
		self.assertEquals(len(ws.data), 1)
		res = ws.data[0]
		self.assertEquals(res[0], "collection")
		self.assertEquals(res[2], "add=9e186398-9ae2-45bf-a9f6-d26bc350221e%2C6b050dcf-7ab1-456d-9e1b-c3c41c18eed2%2Cd3cc336e-1010-4252-9091-7923f0429824")

	def testRemoveFromUserCollection(self):
		ws = FakeWebService()
		q = Query(ws)

		r1 = "9e186398-9ae2-45bf-a9f6-d26bc350221e"
		r2 = "http://musicbrainz.org/release/6b050dcf-7ab1-456d-9e1b-c3c41c18eed2"
		r3 = Release("d3cc336e-1010-4252-9091-7923f0429824")

		q.removeFromUserCollection([r1, r2, r3])
		self.assertEquals(len(ws.data), 1)
		res = ws.data[0]
		self.assertEquals(res[0], "collection")
		self.assertEquals(res[2], "remove=9e186398-9ae2-45bf-a9f6-d26bc350221e%2C6b050dcf-7ab1-456d-9e1b-c3c41c18eed2%2Cd3cc336e-1010-4252-9091-7923f0429824")

	def testSubmitUserTags(self):
		ws = FakeWebService()
		q = Query(ws)
		t1 = [u"foo", u"bar", u"f\u014do"]
		t2 = [Tag(u"foo"), Tag(u"bar"), Tag(u"f\u014do")]

		prefix = 'http://musicbrainz.org/artist/'
		uri = prefix + 'c0b2500e-0cef-4130-869d-732b23ed9df5'

		q.submitUserTags(uri, t1)
		q.submitUserTags(uri, t2)

		self.assertEquals(len(ws.data), 2)
		self.assertEquals(ws.data[0], ws.data[1])

		q.submitUserRating(uri, Rating(5))
		q.submitUserRating(uri, 5)

		self.assertEquals(len(ws.data), 4)
		self.assertEquals(ws.data[2], ws.data[3])
		
	def testSubmitIsrc(self):
		tracks2isrcs = {
					    '6a47088b-d9e0-4088-868a-394ee3c6cd33':'NZABC0800001', 
					    'b547acbc-58c6-4a31-9806-e2348db3a167':'NZABC0800002'
		}
		ws = FakeWebService()
		q = Query(ws)
		
		q.submitISRCs(tracks2isrcs)
		
		self.assertEquals(len(ws.data), 1)
		req = ws.data[0]
		qstring = 'isrc=6a47088b-d9e0-4088-868a-394ee3c6cd33+NZABC0800001&isrc=b547acbc-58c6-4a31-9806-e2348db3a167+NZABC0800002'
		self.assertEquals(req[0], 'track')
		self.assertEquals(req[2], qstring)
		
	def testSubmitIsrcBadUser(self):
		ws = FakeBadAuthWebService()
		q = Query(ws)
		
		self.assertRaises(AuthenticationError, q.submitISRCs, {})
	
	def testSubmitIsrcBadTrack(self):
		ws = FakeBadRequestWebService()
		q = Query(ws)
		
		self.assertRaises(RequestError, q.submitISRCs, {})
		
	def testSubmitPuid(self):
		tracks2puids = {
					    '6a47088b-d9e0-4088-868a-394ee3c6cd33':'c2a2cee5-a8ca-4f89-a092-c3e1e65ab7e6', 
					    'b547acbc-58c6-4a31-9806-e2348db3a167':'c2a2cee5-a8ca-4f89-a092-c3e1e65ab7e6'
		}
		ws = FakeWebService()
		q = Query(ws, clientId='test-1')
		
		q.submitPuids(tracks2puids)
		
		self.assertEquals(len(ws.data), 1)
		req = ws.data[0]
		qstring = 'client=test-1&puid=6a47088b-d9e0-4088-868a-394ee3c6cd33+c2a2cee5-a8ca-4f89-a092-c3e1e65ab7e6&puid=b547acbc-58c6-4a31-9806-e2348db3a167+c2a2cee5-a8ca-4f89-a092-c3e1e65ab7e6'
		self.assertEquals(req[0], 'track')
		self.assertEquals(req[2], qstring)
		
	def testSubmitPuidBadUser(self):
		ws = FakeBadAuthWebService()
		q = Query(ws, clientId='test-1')
		
		self.assertRaises(AuthenticationError, q.submitPuids, {})

	def testSubmitPuidBadTrack(self):
		ws = FakeBadRequestWebService()
		q = Query(ws, clientId='test-1')
		
		self.assertRaises(RequestError, q.submitPuids, {})
		
	def testSubmitPuidNoClient(self):
		ws = FakeWebService()
		q = Query(ws)
		
		self.assertRaises(AssertionError, q.submitPuids, None)

	def testSubmitCDStubNoClient(self):
		ws = FakeWebService()
		q = Query(ws)
		
		self.assertRaises(AssertionError, q.submitCDStub, None)

	def testSubmitCdStub(self):
		from musicbrainz2.model import Disc, CDStub

		ws = FakeWebService()
		q = Query(ws, clientId='test-1')

		discid = "6EmGGSLhuDYz2lNXtqrCiCCqO0o-"
		disc = Disc(discid)
		disc.firstTrackNum = 1
		disc.lastTrackNum = 4
		disc.sectors = 89150
		disc.addTrack( (150, 20551) )
		disc.addTrack( (20701, 26074) )
		disc.addTrack( (46775, 19438) )
		disc.addTrack( (66213, 22937) )

		cdstub = CDStub(disc)
		cdstub.artist = "artist"
		cdstub.title = "title"
		cdstub.addTrack("trackname1")
		cdstub.addTrack("trackname2")
		cdstub.addTrack("trackname3")
		cdstub.addTrack("trackname4")
		q.submitCDStub(cdstub)

		cdstub.barcode = "12345"
		cdstub.comment = "acomment"
		q.submitCDStub(cdstub)

		self.assertEquals(len(ws.data), 2)
		req = ws.data[0]
		qstring = 'client=test-1&discid=6EmGGSLhuDYz2lNXtqrCiCCqO0o-&title=title&artist=artist&track0=trackname1&track1=trackname2&track2=trackname3&track3=trackname4&toc=1+4+89150+150+20701+46775+66213'
		self.assertEquals(req[0], 'release')
		self.assertEquals(req[2], qstring)

		req = ws.data[1]
		qstring = 'client=test-1&discid=6EmGGSLhuDYz2lNXtqrCiCCqO0o-&title=title&artist=artist&barcode=12345&comment=acomment&track0=trackname1&track1=trackname2&track2=trackname3&track3=trackname4&toc=1+4+89150+150+20701+46775+66213'
		self.assertEquals(req[2], qstring)

		cdstub._tracks = []
		cdstub.addTrack("tname1", "artist1")
		cdstub.addTrack("tname2", "artist2")
		cdstub.addTrack("tname3", "artist3")
		cdstub.addTrack("tname4", "artist4")
		q.submitCDStub(cdstub)
		self.assertEquals(len(ws.data), 3)
		req = ws.data[2]
		qstring = 'client=test-1&discid=6EmGGSLhuDYz2lNXtqrCiCCqO0o-&title=title&artist=artist&barcode=12345&comment=acomment&track0=tname1&artist0=artist1&track1=tname2&artist1=artist2&track2=tname3&artist2=artist3&track3=tname4&artist3=artist4&toc=1+4+89150+150+20701+46775+66213'
		self.assertEquals(req[2], qstring)




# EOF
