#! /usr/bin/env python
__revision__ = '$Id'

import os
import sys
import os.path
import unittest
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


setup(
	name		= 'python-musicbrainz2',
	version		= musicbrainz2.__version__,
	description	= 'An interface to the MusicBrainz XML web service',
	author		= 'Matthias Friedrich',
	author_email	= 'matt@mafr.de',
	url		= 'http://www.musicbrainz.org',
	license		= 'BSD',
	packages	= [ 'musicbrainz2' ],
	package_dir	= { 'musicbrainz2': 'src/musicbrainz2' },
	cmdclass	= { 'test': TestCommand, 'docs': GenerateDocsCommand }
)

# EOF
