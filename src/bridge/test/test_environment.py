# vim: tabstop=4 shiftwidth=4 softtabstop=4
import sys
import StringIO
from unittest import TestCase
#from fsa.releasetools.environment.setuputil import ThirdPartyApp

class AcceptanceTests(TestCase):
    def setUp(self):
        self.old_value_of_stdout = sys.stdout
        sys.stdout = StringIO.StringIO()
        self.old_value_of_argv = sys.argv

    def tearDown(self):
        sys.stdout = self.old_value_of_stdout
        sys.argv = self.old_value_of_argv

    def test_no_urls_should_print_nothing(self):
        sys.argv = ["unused_prog_name"]
        #main()
        #self.assertEquals("ok!\n", sys.stdout.getvalue())
