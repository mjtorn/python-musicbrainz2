"""Utilities for working with Audio CDs.

This module contains utilities for working with Audio CDs.

The functions in this module need both an installed libmusicbrainz and a
working ctypes package. If you don't have libmusicbrainz, it can't be
loaded, or your platform isn't supported by either ctypes or this module,
a C{NotImplementedError} is raised.

@author: Matthias Friedrich <matt@mafr.de>
"""
__revision__ = '$Id$'

import sys
import urllib
import urlparse
import ctypes
from musicbrainz2.model import Disc


# Define some magic strings from libmusicbrainz' queries.h.
#
_MB_CDINDEX_ID_LEN = 28
_MBQ_GetCDTOC = '@LOCALCDINFO@'
_MBE_TOCGetCDIndexId = 'http://musicbrainz.org/mm/mm-2.1#cdindexid'
_MBE_TOCGetFirstTrack = 'http://musicbrainz.org/mm/mm-2.1#firstTrack'
_MBE_TOCGetLastTrack = 'http://musicbrainz.org/mm/mm-2.1#lastTrack'
_MBE_MBE_TOCGetTrackSectorOffset = 'http://musicbrainz.org/mm/mm-2.1#toc [] ' \
	+ 'http://musicbrainz.org/mm/mm-2.1#sectorOffset'
_MBE_MBE_TOCGetTrackNumSectors = 'http://musicbrainz.org/mm/mm-2.1#toc [] ' \
	+ 'http://musicbrainz.org/mm/mm-2.1#numSectors'


class DiscError(IOError):
	"""The Audio CD could not be read.

	This may be simply because no disc was in the drive, the device name
	was wrong or the disc can't be read. Reading errors can occur in case
	of a damaged disc or a copy protection mechanism, for example.
	"""
	pass


def _openLibrary():
	"""Tries to open libmusicbrainz.

	@return: a C{ctypes.CDLL} object, representing the opened library

	@raise NotImplementedError: if the library can't be opened
	"""
	if sys.platform == 'linux2':
		libName = 'libmusicbrainz.so.4'
	elif sys.platform == 'darwin':
		libName = 'libmusicbrainz.4.dylib'
	elif sys.platform == 'win32':
		libName = 'libmusicbrainz.dll'
	else:
		raise NotImplementedError('Unknown platform: ' + sys.platform)

	try:
		libMb = ctypes.cdll.LoadLibrary(libName)
	except OSError, e:
		raise NotImplementedError('Error opening library: ' + str(e))

	_setPrototypes(libMb)

	return libMb


def _setPrototypes(libMb):
	ct = ctypes
	libMb.mb_New.argtypes = ( )
	libMb.mb_Delete.argtypes = (ct.c_int, )
	libMb.mb_SetDevice.argtypes = (ct.c_int, ct.c_char_p)
	libMb.mb_Query.argtypes = (ct.c_int, ct.c_char_p)
	libMb.mb_GetQueryError.argtypes = (ct.c_int, ct.c_char_p, ct.c_int)
	libMb.mb_GetResultData.argtypes = (ct.c_int, ct.c_char_p,
		ct.c_char_p, ct.c_int)
	libMb.mb_GetResultData1.argtypes = (ct.c_int, ct.c_char_p,
		ct.c_char_p, ct.c_int, ct.c_int)


def _getQueryError(libMb, mb):
	maxLen = 256
	buf = ctypes.c_buffer(maxLen)
	libMb.mb_GetQueryError(mb, buf, maxLen)
	return buf.value


def readDisc(deviceName=None):
	"""Reads an Audio CD in the disc drive.

	This reads a CD's table of contents (TOC) and calculates the MusicBrainz
	DiscID, which is a 28 character ASCII string. This DiscID can be used
	to retrieve a list of matching releases from the web service (see
	L{musicbrainz2.webservice.Query}).

	Note that an Audio CD has to be in drive for this to work. The
	C{deviceName} argument may be used to set the device. The default
	depends on the operating system (on linux, it's C{'/dev/cdrom'}).
	No network connection is needed for this function.

	If the device doesn't exist or there's no valid Audio CD in the drive,
	a L{DiscError} exception is raised.

	@param deviceName: a string containing the CD drive's device name

	@return: a L{musicbrainz2.model.Disc} object

	@raise DiscError: if there was a problem reading the disc
	@raise NotImplementedError: if DiscID generation isn't supported
	"""
	libMb = _openLibrary()

	mb = libMb.mb_New()
	assert mb != 0, "libmusicbrainz: mb_New() returned NULL"

	if deviceName is not None:
		res = libMb.mb_SetDevice(mb, deviceName)
		assert res != 0, "libmusicbrainz: mb_SetDevice() returned false"

	# Access the CD drive.
	res = libMb.mb_Query(mb, _MBQ_GetCDTOC)
	if res == 0:
		raise DiscError(_getQueryError(libMb, mb))

	# Now extract the data from the result.
	disc = Disc()

	# extract the DiscID
	maxLen = 256
	buf = ctypes.c_buffer(maxLen+1)
	res = libMb.mb_GetResultData(mb, _MBE_TOCGetCDIndexId, buf, maxLen)
	assert res != 0
	disc.setId(buf.value)

	res = libMb.mb_GetResultData(mb, _MBE_TOCGetFirstTrack, buf, maxLen)
	assert res != 0
	firstTrackNum = int(buf.value)

	res = libMb.mb_GetResultData(mb, _MBE_TOCGetLastTrack, buf, maxLen)
	assert res != 0
	lastTrackNum = int(buf.value)

	res = libMb.mb_GetResultData1(mb,
		_MBE_MBE_TOCGetTrackSectorOffset, buf, maxLen, firstTrackNum)
	assert res != 0
	disc.setSectors(int(buf.value))

	for i in range(firstTrackNum+1, lastTrackNum+2):
		res = libMb.mb_GetResultData1(mb,
			_MBE_MBE_TOCGetTrackSectorOffset, buf, maxLen, i)
		trackOffset = int(buf.value)

		res = libMb.mb_GetResultData1(mb,
			_MBE_MBE_TOCGetTrackNumSectors, buf, maxLen, i)
		trackSectors = int(buf.value)

		disc.addTrack( (trackOffset, trackSectors) )

	disc.setFirstTrackNum(firstTrackNum)
	disc.setLastTrackNum(lastTrackNum)

	libMb.mb_Delete(mb)

	return disc


def getSubmissionUrl(disc):
	"""Returns a URL for adding a disc to the MusicBrainz database.

	A fully initialized L{musicbrainz2.model.Disc} object is needed, as
	returned by L{readDisc}. A disc object returned by the web service
	doesn't provide the necessary information.

	Note that the created URL is intended for interactive use and points
	to the MusicBrainz disc submission wizard. This method just returns a
	URL, no network connection is needed. The disc drive isn't used.

	@param disc: a fully initialized L{musicbrainz2.model.Disc} object

	@return: a string containing the submission URL

	@see: L{readDisc}
	"""
	assert isinstance(disc, Disc), 'musicbrainz2.model.Disc expected'
	discid = disc.getId()
	first = disc.getFirstTrackNum()
	last = disc.getLastTrackNum()
	sectors = disc.getSectors()
	assert None not in (discid, first, last, sectors)

	tracks = last - first + 1
	toc = "%d %d %d " % (first, last, sectors)
	toc = toc + ' '.join( map(lambda x: str(x[0]), disc.getTracks()) )

	query = urllib.urlencode({ 'id': discid, 'toc': toc, 'tracks': tracks })

	url = ('http', 'musicbrainz.org', '/bare/cdlookup.html', '', query, '')
		
	return urlparse.urlunparse(url)

# EOF
