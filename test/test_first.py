import unittest

class First(unittest.TestCase):
	def testRun(self):
		self.assertTrue( True )


def suite():
	suite = unittest.makeSuite(First)
	return suite
