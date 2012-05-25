# vim: tabstop=4 shiftwidth=4 softtabstop=4
import os
import sys
import shutil
import unittest
import urllib2
import time
import types

from fsa.releasetools.classes.svntools import SvnTools
from fsa.releasetools.classes.configuration import Config
from fsa.releasetools.classes.utils import ReWalker

test_config_file = os.path.join(os.path.expanduser('~'), '.releasetools', 'releasetools.cfg')

class SvnToolsTest(unittest.TestCase):

#
# Fixture Framework
#

    def setUp(self):
        print '\nTest Fixture setUp'
        self.S = SvnTools()
        self.C = Config()
        self.C.validate_set_options()
        self.C.set_svn_host('sd1appsdl05.fsa.gov.uk')
        #self.C.set_svn_port('80')
        self.svn_url = self.C.get_svn_baseurl()


    def tearDown(self):
        print '\nTest Fixture tearDown'
        del self.S
        del self.C
        del self.svn_url

#
# Tests
#

    def test_01_findpoms(self):
        print '\n running checkout'
        base_url = self.svn_url + '/' + 'mock-project'
        print base_url
        if os.path.isdir(os.path.join(os.path.expanduser('~'), 'tmp', 'svntest', 'testcheckout')):
            shutil.rmtree(os.path.join(os.path.expanduser('~'), 'tmp', 'svntest', 'testcheckout'))
        self.S.checkout(base_url, os.path.join(os.path.expanduser('~'), 'tmp', 'svntest', 'testcheckout', 'mock-project'))
        self.failUnlessEqual(True, os.path.isfile(os.path.join(os.path.expanduser('~'), 'tmp', 'svntest', 'testcheckout', 'mock-project', 'trunk', 'text.txt')))
        base_dir = os.path.join(os.path.expanduser('~'), 'tmp', 'svntest', 'testcheckout', 'mock-project')
        walker = ReWalker(base_dir, r"*\.pom$", [".svn"]).execute()
