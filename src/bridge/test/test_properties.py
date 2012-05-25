#!/usr/bin/env python
import codecs, unittest, StringIO
from fsa.releasetools.classes.Properties import Properties

#
# todo:
# * test writing property files
# * test writing unicode property files

class PropertiesTest(unittest.TestCase):

    def setUp(self):
         pass

    def testPropertiesOneLine(self):
        propertiesFile = StringIO.StringIO("foo.bar=baz")
        properties = Properties.Properties()
        properties.load(propertiesFile)
        self.assertEqual("baz", properties["foo.bar"])

    def testComments(self):
        input = """
#key1=value1
!key1=value1
        """
        properties = self.getPropertiesAndLoad(input)
        self.assertFalse(properties.has_key("key1"))
        self.assertFalse(properties.has_key("#key1"))
        self.assertFalse(properties.has_key("!key1"))

    def testSeparators(self):
        input = """
key2 value2
key3=value3
key4:value4
key5\tvalueA,valueB,valueC
        """
        properties = self.getPropertiesAndLoad(input)
        self.assertEqual("value2", properties["key2"])
        self.assertEqual("value3", properties["key3"])
        self.assertEqual("value4", properties["key4"])
        self.assertEqual("valueA,valueB,valueC", properties["key5"])

    def testMultilineProperty(self):
        input = """
key6      valueD,valueE,valueF, \\
            valueG, valueH
        """
        properties = self.getPropertiesAndLoad(input)
        self.assertEqual("valueD,valueE,valueF, valueG, valueH", properties["key6"])

    def testKeyOnly(self):
        input = """
key7
        """
        properties = self.getPropertiesAndLoad(input)
        self.assertEqual("", properties["key7"])

    def testSpacesInValue(self):
        input = """
key8 = valueX valueY valueZ
        """
        properties = self.getPropertiesAndLoad(input)
        self.assertEqual("valueX valueY valueZ", properties["key8"])

    def testSpacesInKey(self):
        input = """
This\\ key= this value
a\\ b\\ c = def
        """
        properties = self.getPropertiesAndLoad(input)
        self.assertEqual("this value", properties["This key"])
        self.assertEqual("def", properties["a b c"])

    def testPropertiesSeveralLines(self):
        input = """
#key1=value1
!key1=value1
key2 value2
key3=value3
key4:value4
key5\tvalueA,valueB,valueC
key6      valueD,valueE,valueF, \\
            valueG, valueH
key7
key8 = valueX valueY valueZ
This\\ key= this value
        """
        properties = self.getPropertiesAndLoad(input)
        self.assertFalse(properties.has_key("key1"))
        self.assertFalse(properties.has_key("#key1"))
        self.assertFalse(properties.has_key("!key1"))
        self.assertEqual("value2", properties["key2"])
        self.assertEqual("value3", properties["key3"])
        self.assertEqual("value4", properties["key4"])
        self.assertEqual("valueA,valueB,valueC", properties["key5"])
        self.assertEqual("valueD,valueE,valueF, valueG, valueH", properties["key6"])
        self.assertEqual("", properties["key7"])
        self.assertEqual("valueX valueY valueZ", properties["key8"])
        self.assertEqual("this value", properties["This key"])

    def testUnicodeValue(self):
        expectedValue = u"b\u0061r".encode("latin_1")
        key = u"blah.bling".encode("latin_1")
        input = key + "=".encode("latin_1") + expectedValue
        properties = self.getPropertiesAndLoad(input)
        self.assertEqual(expectedValue, properties[key])

    def testUnicodeReadFromFile(self):
        expectedValue = u"M\u00f6tley Cr\u00fce".encode("latin_1")
        key = u"\u0062\u00e2\u00f1\u0064".encode("latin_1")
        input = key + "=".encode("latin_1") + expectedValue
        file = StringIO.StringIO(input)
        properties = Properties.Properties()
        properties.load(file)
        self.assertEqual(expectedValue, properties[key])

    def testUnicodeKeyValue(self):
        expectedValue = u"M\u00f6tley Cr\u00fce".encode("latin_1")
        key = u"\u0062\u00e2\u00f1\u0064".encode("latin_1")
        input = key + "=".encode("latin_1") + expectedValue
        properties = self.getPropertiesAndLoad(input)
        self.assertEqual(expectedValue, properties[key])

    def testUnicode(self):
        key = u"\u0061".decode("latin_1")
        self.assertTrue("a", key)

    def testPropertiesEntry(self):
        propertiesEntry = Properties.PropertyEntry()
        propertiesEntry["foo"] = "bar"
        propertiesEntry["blah"] = "abc"
        self.assertEqual("bar", propertiesEntry["foo"])
        self.assertEqual("abc", propertiesEntry["blah"])
        self.assertEqual("{'blah': 'abc', 'foo': 'bar'}", "%s" % propertiesEntry)

    def testPropertiesEntryKeywordInit(self):
        propertiesEntry = Properties.PropertyEntry(foo="bar", baz="bling")
        self.assertEqual("bar", propertiesEntry["foo"])
        self.assertEqual("bling", propertiesEntry["baz"])

    def testNewPropsExists(self):
        input = """
key3=value3
        """
        properties = self.getPropertiesAndLoad(input)
        self.assertEqual("value3", properties["key3"])

    def testGetAsString(self):
        input = """key1=value1
# comment
key2=value2

key3=value3"""
        properties = self.getPropertiesAndLoad(input)
        expectedValue = "key1=value1\n# comment\nkey2=value2\n\nkey3=value3\n"
        actualValue = properties.getAsString()
        self.assertEqual(expectedValue, actualValue)

    def testStore(self):
        input = """key1=value1
# comment
key2=value2

key3=value3"""
        properties = self.getPropertiesAndLoad(input)
        expectedValue = "key1=value1\n# comment\nkey2=value2\n\nkey3=value3\n"
        outputFile = StringIO.StringIO(u"")
        self.assertEqual("", outputFile.getvalue())
        properties._store(outputFile)
        self.assertEqual(expectedValue, outputFile.getvalue())

    def testGetPropertyDict(self):
        input = """key1=value1
key2=value2
key3=value3"""
        properties = self.getPropertiesAndLoad(input)
        expectedValue = {"key1" : "value1", "key2" : "value2", "key3" : "value3"}
        self.assertEqual(expectedValue, properties.getPropertyDict())

    def getPropertiesAndLoad(self, input):
        properties = Properties.Properties()
        properties.loadFromString(input)
        return properties

if __name__ == '__main__':
     unittest.main()
