# vim: tabstop=4 shiftwidth=4 softtabstop=4
import os
import sys
import unittest

from fsa.releasetools.classes.configuration import Config

test_config_file = os.path.join(os.path.expanduser('~'), '.releasetools', 'releasetools.cfg')

class ConfigurationTest(unittest.TestCase):

#
# Fixture Framework
#

    def setUp(self):
        print '\nTest Fixture setUp'
        if os.path.isfile(test_config_file):
            os.remove(test_config_file)
        self.C = Config()
        self.C.validate_set_options()
        

    def tearDown(self):
        print '\nTest Fixture tearDown'
        if os.path.isfile(test_config_file):
            os.remove(test_config_file)
        del self.C

#
# Tests
#

    def test_01_get_username(self):
        print '\n running get_username'
        self.failUnlessEqual('releasetools', self.C.get_username())
        self.failIfEqual('donnald', self.C.get_username())

    def test_02_set_username(self):
        print '\n running set_username'
        self.C.set_username('mickey')
        self.failUnlessEqual('mickey', self.C.get_username())
        self.failIfEqual('donnald', self.C.get_username())
        
    def test_03_get_password(self):
        print '\n running get_password'
        self.failUnlessEqual('releasetools', self.C.get_password())
        self.failIfEqual('donnald', self.C.get_password())

    def test_04_set_password(self):
        print '\n running set_password'
        self.C.set_password('mouse')
        self.failUnlessEqual('mouse', self.C.get_password())
        self.failIfEqual('duck', self.C.get_password())

    def test_05_svn_host(self):
        print '\n running get_svn_host'
        self.failUnlessEqual('localhost', self.C.get_svn_host())
        self.failIfEqual('notarealhost.co.uk', self.C.get_svn_host())

    def test_06_set_svn_host(self):
        print '\n running set_svn_host'
        self.C.set_svn_host('sd1appsdl05.fsa.gov.uk')
        self.failUnlessEqual('sd1appsdl05.fsa.gov.uk', self.C.get_svn_host())
        self.failIfEqual('notarealhost.co.uk', self.C.get_svn_host())

    def test_07_svn_port(self):
        print '\n running get_svn_port'
        self.failUnlessEqual('80', self.C.get_svn_port())
        self.failIfEqual('5555', self.C.get_svn_port())

    def test_08_set_svn_port(self):
        print '\n running set_svn_port'
        self.C.set_svn_port('443')
        self.failUnlessEqual('443', self.C.get_svn_port())
        self.failIfEqual('555', self.C.get_svn_port())
        
    def test_09_nexus_host(self):
        print '\n running get_nexus_host'
        self.failUnlessEqual('localhost', self.C.get_nexus_host())
        self.failIfEqual('notarealhost.co.uk', self.C.get_nexus_host())

    def test_10_set_nexus_host(self):
        print '\n running set_nexus_host'
        self.C.set_nexus_host('sd1appsdl05.fsa.gov.uk')
        self.failUnlessEqual('sd1appsdl05.fsa.gov.uk', self.C.get_nexus_host())
        self.failIfEqual('notarealhost.co.uk', self.C.get_nexus_host())

    def test_11_nexus_port(self):
        print '\n running get_nexus_port'
        self.failUnlessEqual('8081', self.C.get_nexus_port())
        self.failIfEqual('5555', self.C.get_nexus_port())

    def test_12_set_nexus_port(self):
        print '\n running set_nexus_port'
        self.C.set_nexus_port('443')
        self.failUnlessEqual('443', self.C.get_nexus_port())
        self.failIfEqual('555', self.C.get_nexus_port())


if __name__ == '__main__':
    unittest.main()
