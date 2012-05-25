# vim: tabstop=4 shiftwidth=4 softtabstop=4
import os
import sys
import unittest

from fsa.releasetools.classes.versionvalidator import VersionValidator

ucode_versions = u'2012.7.2.B1\n2012.7.3.B1\n2012.7.4.B1\n2012.7.5.B1\n2012.7.5.B2\n2012.8.1.B1\n2012.8.2.B1\n \
                 2012.8.3.A1\n2012.8.3.A2\n2012.8.3.A3\n2012.8.3.A4\n2012.8.3.A5\n2012.8.3.A6'
str_versions = '2012.7.2.B1\n2012.7.3.B1\n2012.7.4.B1\n2012.7.5.B1\n2012.7.5.B2\n2012.8.1.B1\n2012.8.2.B1\n2012.8.3.A1\n \
               2012.8.3.A2\n2012.8.3.A3\n2012.8.3.A4\n2012.8.3.A5\n2012.8.3.A6'

versions_list = ['2012.7.2.B1', '2012.7.3.B1', '2012.7.4.B1', '2012.7.5.B1', '2012.7.5.B2', '2012.8.1.B1', '2012.8.2.B1', \
                 '2012.8.3.A1', '2012.8.3.A2', '2012.8.3.A3', '2012.8.3.A4', '2012.8.3.A5', '2012.8.3.A6']

def eq_diff(a, b):
    import json, difflib
    from datetime import datetime

    if a == b:
        return

    class DatetimeEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            else:
                # Fall back to string
                return str(o)

    a_json = json.dumps(a, indent=4, sort_keys=True, cls=DatetimeEncoder)
    b_json = json.dumps(b, indent=4, sort_keys=True, cls=DatetimeEncoder)
    diff = ''.join(difflib.unified_diff(
        a_json.splitlines(True),
        b_json.splitlines(True),
        fromfile='actual',
        tofile='expected',
    ))
    raise AssertionError('\n' + diff)

class VersionValidatorTest(unittest.TestCase):

    def setUp(self):
        print '\nTest Fixture setUp'
        self.V = VersionValidator()

    def tearDown(self):
        print '\nTest Fixture tearDown'
        del self.V

#
# Tests
#

    def test_01_uppercase(self):
        print '\n running tmp_dir_creation_deletion'
        self.failUnlessEqual(True, self.V.is_valid_version('2012.8.3.A1'))
        self.failUnlessEqual(True, self.V.is_valid_version('2012.8.3.B1'))
        self.failUnlessEqual(True, self.V.is_valid_version('2012.8.3.RC1'))

    def test_02_uppercase_doubledigit(self):
        self.failUnlessEqual(True, self.V.is_valid_version('2012.8.3.A10'))
        self.failUnlessEqual(True, self.V.is_valid_version('2012.8.3.B21'))
        self.failUnlessEqual(True, self.V.is_valid_version('2012.8.3.RC30'))

    def test_03_fail_lowercase(self):
        self.failUnlessEqual(False, self.V.is_valid_version('2012.8.3.a30'))
        self.failUnlessEqual(False, self.V.is_valid_version('2012.8.3.b30'))
        self.failUnlessEqual(False, self.V.is_valid_version('2012.8.3.rc30'))

    def test_04_fail_missingperiod(self):
        self.failUnlessEqual(False, self.V.is_valid_version('2012.8.3A30'))
        self.failUnlessEqual(False, self.V.is_valid_version('2012.8.3B30'))
        self.failUnlessEqual(False, self.V.is_valid_version('2012.8.3RC30'))

    def test_05_valid_unicode_version(self):
        self.failUnlessEqual(False, self.V.is_valid_version(u'2012.8.3A30'))
        self.failUnlessEqual(False, self.V.is_valid_version(u'2012.8.3B30'))
        self.failUnlessEqual(False, self.V.is_valid_version(u'2012.8.3RC30'))

    def test_06_uppercase(self):
        print '\n running tmp_dir_creation_deletion'
        self.failUnlessEqual(True, self.V.is_valid_version(u'2012.8.3.A1'))
        self.failUnlessEqual(True, self.V.is_valid_version(u'2012.8.3.B1'))
        self.failUnlessEqual(True, self.V.is_valid_version(u'2012.8.3.RC1'))

    def test_07_uppercase_doubledigit(self):
        self.failUnlessEqual(True, self.V.is_valid_version(u'2012.8.3.A10'))
        self.failUnlessEqual(True, self.V.is_valid_version(u'2012.8.3.B21'))
        self.failUnlessEqual(True, self.V.is_valid_version(u'2012.8.3.RC30'))

    def test_08_uppercase_doubledigit(self):
        self.failUnlessEqual(True, self.V.is_valid_version(u'2012.18.3.A10'))
        self.failUnlessEqual(True, self.V.is_valid_version(u'2012.18.3.B21'))
        self.failUnlessEqual(True, self.V.is_valid_version(u'2012.18.3.RC30'))

    def test_09_fail_lowercase(self):
        self.failUnlessEqual(False, self.V.is_valid_version(u'2012.8.3.a30'))
        self.failUnlessEqual(False, self.V.is_valid_version(u'2012.8.3.b30'))
        self.failUnlessEqual(False, self.V.is_valid_version(u'2012.8.3.rc30'))

    def test_10_fail_missingperiod(self):
        self.failUnlessEqual(False, self.V.is_valid_version(u'2012.8.3A30'))
        self.failUnlessEqual(False, self.V.is_valid_version(u'2012.8.3B30'))
        self.failUnlessEqual(False, self.V.is_valid_version(u'2012.8.3RC30'))

