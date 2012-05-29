import os
import urllib2
import pprint
import re
import shutil
import sys
import tempfile
from time import gmtime, strftime
from datetime import date
from xml.dom.minidom import parse, parseString
import xml.dom.minidom
from zabbix_api import ZabbixAPI

nms_url = "http://89.185.58.167:8980/opennms/rest/"
nms_user = 'vodafone'
nms_pass = 'enofadov'


def download_xml(url, username, password):
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
    raw_xml_file = usock.read()
    usock.close()
    xml_file = parseString(raw_xml_file)
    return xml_file


def get_xml_text(xmltag):
    for elem in xmltag.childNodes:
        if elem.nodeType == elem.TEXT_NODE:
            return elem.data

class NodeReader(object):
    
    def __init__(self, base_url, username, password):
        self.nodes = {}
        node_url = base_url + 'nodes'
        node_xml = download_xml(node_url, username, password)
        self.read_nodes_xml(node_xml)
    
    def read_nodes_xml(self, xml_file):
        node = xml_file.documentElement
        nrOfHosts = int(node.getAttribute('count'))
        #print nrOfHosts
        #nrOfHosts = nrOfHosts - 1
        for hostNr in range(nrOfHosts):
            host_name = node.childNodes[hostNr].getAttribute('label')
            host_id = node.childNodes[hostNr].getAttribute('id')
            self.nodes[host_id] = host_name
            #print 'Host name: %s host id: %s' % (host_name,host_id)
        return self.nodes

class Node(object):
    def __init__(self, base_url, username, password, hostid, name ):
        self.id=hostid
        get_url = base_url + 'nodes' + '/' + self.id + '/ipinterfaces'
        self.name=name
        self.ipAddress=self.get_ip_address(get_url, username, password)
        
    def get_ip_address(self, get_url, username, password):
        xml = download_xml(get_url, username, password)
        node = xml.documentElement
        self.ipaddress = get_xml_text(node.getElementsByTagName('ipAddress')[0])
        print 'Host name: %s ipaddress: %s' % (self.name,self.ipaddress)
        
    def read_alarms(self):
        if int(alarms_xml.childNodes[0].getAttribute('count')) != 0:
            print 'there are alarms'
        else:
            print 'there are NO alarms'
        alarms = alarms_xml.getElementsByTagName('alarm')
        for alarm in alarms:
            alarm_id=alarm.getAttribute('id')
            alarm_severity=alarm.getAttribute('severity')
            alarm_host=get_xml_text(alarm.getElementsByTagName('host')[0])
            alarm_description=get_xml_text(alarm.getElementsByTagName('description')[0])
            if alarm_host == self.name:
                print 'Host name: %s alarm id: %s severity: %s' % (self.name,alarm_id, alarm_severity)
        
        
        
    
if __name__ == '__main__':
    hosts={}
    #alarm_url = nms_url + 'alarms'
    #alarms_xml = download_xml(alarm_url, nms_user, nms_pass)
    # open file
    f = open ("/Volumes/home/banjo/opennms_alarms.xml","r")
    #Read whole file into data
    alarms_xml_file = f.read()
    # Close the file
    f.close()
    alarms_xml = parseString(alarms_xml_file)
    X = NodeReader(nms_url, nms_user, nms_pass)
    for hostId in X.nodes.keys():
        hosts[hostId] = Node(nms_url, nms_user, nms_pass, hostId,X.nodes[hostId])
        hosts[hostId].read_alarms()
    print