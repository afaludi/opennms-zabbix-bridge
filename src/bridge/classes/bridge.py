import os
import urllib2
import pprint
import re
import shutil
import sys
import tempfile
from time import gmtime, strftime
from datetime import date
#from xml.dom.minidom import parse, parseString
import xml.dom.minidom

nms_url = "http://89.185.58.167:8980/opennms/rest/"
nms_user = 'vodafone'
nms_pass = 'enofadov'
class NodeReader(object):
    
    def __init__(self, base_url, username, password):
        self.list = []
        self.appt_list = []
        node_url = base_url + 'nodes'
        node_xml = self.download_xml(node_url, username, password)
        self.read_xml(node_xml)
    
    def download_xml(self, url, username, password):
        print 'inside method'
        print url
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        # this creates a password manager
        passman.add_password(None, url, username, password)
        # because we have put None at the start it will always
        # use this username/password combination for  urls
        # for which `url` is a super-url

        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        # create the AuthHandler

        opener = urllib2.build_opener(authhandler)

        urllib2.install_opener(opener)
        # All calls to urllib2.urlopen will now use our handler
        # Make sure not to include the protocol in with the URL, or
        # HTTPPasswordMgrWithDefaultRealm will be very confused.
        # You must (of course) use it when fetching the page though.

        usock = urllib2.urlopen(url)
        # authentication is now handled automatically for us
        xml_file = usock.read()
        usock.close()
        return xml_file

    def read_xml(self, xml_file):
        doc = xml.dom.minidom.parse(xml_file)
        node = doc.documentElement
        if node.nodeType == xml.dom.Node.ELEMENT_NODE:
            print 'Element name: %s' % node.nodeName
            for (name, value) in node.attributes.items():
                #print '    Attr -- Name: %s  Value: %s' % (name, value)
                if name == 'reminder':
                    self.rem_value = value
 
        return node
        #return self.nodes

if __name__ == '__main__':
    X = NodeReader(nms_url, nms_user, nms_pass)
    print