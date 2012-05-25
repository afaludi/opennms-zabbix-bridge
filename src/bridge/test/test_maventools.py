# vim: tabstop=4 shiftwidth=4 softtabstop=4
import os
import sys
import unittest

from fsa.releasetools.classes.configuration import Config
from fsa.releasetools.classes.maventools import MavenTools

test_config_file = os.path.join(os.path.expanduser('~'), '.releasetools', 'releasetools.cfg')

class MavenToolsTest(unittest.TestCase):

#
# Fixture Framework
#
#       gen                     const                      gen         const                    gen                
#http://nexus.art:8081 /nexus/service/local/repositories/ snapshots /content/ uk/gov/fsa/rsd/scenariomanager/ScenarioManager-webapp/ 1.0-SNAPSHOT /ScenarioManager-webapp-1.0-20110916.103149-102.war
#http://nexus.art:8081 /nexus/service/local/repositories/ releases  /content/ uk/gov/fsa/rsd/scenariomanager/ScenarioManager-webapp/  0.8.2.B1    /ScenarioManager-webapp-0.8.2.B1.war

    def setUp(self):
        print '\nTest Fixture setUp'
        self.C = Config()
        self.C.validate_set_options()
        self.M = MavenTools('scenariomanager-webapp')    

    def tearDown(self):
        print '\nTest Fixture tearDown'
        del self.C
        del self.M

#
# Tests
#

    def test_01_tmp_dir_creation_deletion(self):
        print '\n running tmp_dir_creation_deletion'
        tmpdir = self.M.get_temp_dir()
        self.failUnlessEqual(True, os.path.isdir(tmpdir))
        self.M.cleanup_temp_dir()
        self.failUnlessEqual(False, os.path.isdir(tmpdir))
    

