#! /usr/bin/env python
__revision__ = '$Id$'

import os
import sys
import os.path
import unittest
import glob
from distutils.core import setup, Command

sys.path.insert(0, 'src')
import musicbrainz2

class TestCommand(Command):
	description = 'run all test cases'
	user_options = [ ]
	
	def initialize_options(self): pass

	def finalize_options(self): pass

	def run(self):
		files = [ ]
		for f in os.listdir('test'):
			elems = os.path.splitext(f)
			if f != '__init__.py' and elems[1] == '.py':
				files.append('test.' + elems[0])

		tests = unittest.defaultTestLoader.loadTestsFromNames(files)
		t = unittest.TextTestRunner()
		t.run(tests)


class GenerateDocsCommand(Command):
	description = 'generate the API documentation'
	user_options = [ ]

	def initialize_options(self): pass

	def finalize_options(self): pass

	def run(self):
		from distutils.spawn import find_executable, spawn
		bin = find_executable('epydoc')
		noPrivate = '--no-private'
		cmd = (bin, noPrivate, os.path.join('src', 'musicbrainz2'))

		spawn(cmd)

setup_args = {
	'name':		'python-musicbrainz2',
	'version':	musicbrainz2.__version__,
	'description':	'An interface to the MusicBrainz XML web service',
	'author':	'Matthias Friedrich',
	'author_email':	'matt@mafr.de',
	'url':		'http://www.musicbrainz.org',
	'license':	'BSD',
	'packages':	[ 'musicbrainz2' ],
	'package_dir':	{ 'musicbrainz2': 'src/musicbrainz2' },
	'cmdclass':	{ 'test': TestCommand, 'docs': GenerateDocsCommand }
}

(ver_major, ver_minor) = sys.version_info[0:2]

# package_data is only available on python >= 2.4
if ver_major >= 2 and ver_minor >= 4:
	setup_args['package_data'] = {
		'musicbrainz2': ['data/*.csv']
	}
else:
	data_files = glob.glob('src/musicbrainz2/data/*.csv')
	setup_args['data_files'] = [
		('lib/python2.4/site-packages/musicbrainz2/data', data_files),
	]

setup(**setup_args)

# EOF
