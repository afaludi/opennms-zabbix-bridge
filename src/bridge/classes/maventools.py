# vim: tabstop=4 shiftwidth=4 softtabstop=4
import ConfigParser
import os
import urllib2
import pprint
import re
import shutil
import sys
import re
import tempfile
from time import gmtime, strftime
from datetime import date
from BeautifulSoup import BeautifulSoup
from xml.dom.minidom import parse, parseString

from fsa.releasetools.classes.utils import execute
from fsa.releasetools.classes.utils import executePoll
from fsa.releasetools.classes.utils import locate
from fsa.releasetools.classes.utils import fileFinder
from fsa.releasetools.classes.configuration import Config
from fsa.releasetools.classes.svntools import SvnTools
from fsa.releasetools.classes.versionvalidator import VersionValidator

from fsa.releasetools.classes.renderengine import Renderer

from fsa.releasetools.classes.mailer import Message
from fsa.releasetools.classes.mailer import Mailer

envars = ['MAVEN_HOME', 'JAVA_HOME', 'HTTP_PROXY_PORT', 'HTTP_PROXY_HOST',
          'MAVEN_REPOSITORY']
for envar in envars:
    if os.getenv(envar) == None:
        sys.exit(1)
    else:
        print "Environment Variable: {0} set to : {1}".format(envar, os.getenv(envar)) 
        
mvn = os.path.join(os.getenv('MAVEN_HOME'), 'bin', 'mvn')



class MavenTools(object):

    def __init__(self, project, branch=None, revision=None, suppress_email=False, skip_tests=False):
        self.project = project
        if branch == None:
            self.branch = 'trunk'
        else:
            self.branch = branch

        if revision == None:
            self.revision = 'HEAD'
        else:
            self.revision = revision
        self.suppress_email = suppress_email
        self.tmpdir = None
        self.skip_tests = skip_tests
        self.S = SvnTools()
        self.C = Config()
        self.C.validate_set_options()
        self.V = VersionValidator()
        self.version = None
        self.pom = None
        self.buildtime = None
        self.svn_location = None
        self.svn_revision = None
        self.data = None

    def get_temp_dir(self):
        if self.tmpdir == None:
            try:
                tmpdir = tempfile.mkdtemp(prefix='releasetools-')
                self.tmpdir = tmpdir
                return tmpdir
            except Exception as e:
                print "Error Detected: {0}".format(e)
        else:
            try:
                os.path.isdir(self.tmpdir)
                return self.tmpdir
            except Exception as e:
                print "Error Detected: {0}".format(e)

    def cleanup_temp_dir(self):
        if self.tmpdir != '':
            try:
                shutil.rmtree(self.tmpdir)
            except Exception as e:
                print "Error Detected: {0}".format(e)

    def checkout_project(self, url, dest):
        try:
            self.S.checkout(url, dest, self.revision)
        except Exception as e:
            print "Error Detected: {0}".format(e)
            print """check your password, try resetting the .subversion password file if
            your password has changed
            """
            sys.exit(1)

    def build(self, project_dir):
        if os.path.curdir != project_dir:
            os.chdir(project_dir)
        if self.skip_tests == True:
            command_list = [mvn, '-e', 'clean', 'package', '-DskipTests', self.get_property_file()]
        else:
            command_list = [mvn, '-e', 'clean', 'package', self.get_property_file()]
        executePoll(command_list)
        self.update_build_info()

    def deploy(self, project_dir):
        if os.path.curdir != project_dir:
            os.chdir(project_dir)
        if self.skip_tests == True:
            command_list = [mvn, '-e', 'clean', 'deploy', '-DskipTests', self.get_property_file()]
        else:
            command_list = [mvn, '-e', 'clean', 'deploy', self.get_property_file()]
        executePoll(command_list)
        self.update_build_info()
    
    def cleanup_build(self, project_dir):
        if os.path.curdir != project_dir:
            os.chdir(project_dir)
        command_list = [mvn, '-e', 'clean']
        executePoll(command_list)    

    def release(self, version=None, drop=None):
        if version != None:
            assert self.V.is_valid_version(version)
            self.version = version
        
        self.get_temp_dir()
        base_url = self.C.get_svn_baseurl()
        url = '/'.join([base_url, self.project, self.branch])
        dest = os.path.join(self.get_temp_dir(), self.branch)
        self.checkout_project(url, dest)
        
        #must sort this out and make it smarter in order to use drops as branches.
        if drop == None:
            this_drop = 0
        
        if version == None:
            version = self.get_generated_version_number(drop=this_drop)
            self.version = version
            
        if self.is_mvn_project(dest):
            self.set_pom_version(self.version)
            self.deploy(dest)
            self.cleanup_build(dest)
            print "Attempting to Tag release", self.version
            tag_url = '/'.join([base_url, self.project, 'tags', 'a', '-'.join([self.project, self.version])])
            print tag_url
            ticket = '#1646'
            self.S.tag(dest, tag_url, 'refs {0} : {1} Release {2}'.format(ticket, self.project, self.version))
        self.email_release_notification()

    def package(self, version=None, drop=None):
        if version != None:
            assert self.V.is_valid_version(version)
            self.version = version
            
        self.get_temp_dir()
        base_url = self.C.get_svn_baseurl()
        url = '/'.join([base_url, self.project, self.branch])
        print "Checking out: {0} to {1}".format(url, self.get_temp_dir())
        dest = os.path.join(self.get_temp_dir(), self.branch)
        self.checkout_project(url, dest)
        
        #must sort this out and make it smarter in order to use drops as branches.
        if drop == None:
            this_drop = 0
        
        if version == None:
            version = self.get_generated_version_number(drop=this_drop)
            self.version = version        
        
        if self.is_mvn_project(dest):
            self.set_pom_version(self.version)
            self.build(dest)

    def is_mvn_project(self, dest):
        if os.path.exists(os.path.join(dest, 'pom.xml')):
            return True
        else:
            print "Error: Maven pom.xml file not found, possible problem with checkout"
            sys.exit(1)

    def get_poms(self):
        return fileFinder(os.path.join(self.get_temp_dir(), self.branch), "pom.xml")

    def update_build_info(self):
        if self.buildtime == None:
            self.buildtime = gmtime()
        if self.svn_location == None:
            self.svn_location = self.branch
        if self.svn_revision == None:
            self.svn_revision = self.S.get_wcopy_revision(os.path.join(self.get_temp_dir(), self.branch))

    def get_buildtime(self):
        return self.buildtime

    def get_svn_location(self):
        return self.svn_location

    def get_svn_revision(self):
        return self.svn_revision

    def get_version_built(self):
        return self.version

    def get_property_file(self):
        return '-D{0}_ENV_PROPERTIES=file:src/test/resources/{1}-unittest.properties'.format(self.project.upper(), self.project.lower())

    def read_pom(self, pom_file):
        if os.path.isfile(pom_file):
            f = open(pom_file, 'r')
            raw_pom = f.read()
            f.close()
            self.pom = parseString(raw_pom)
        return self.pom

    def write_pom(self, dom, pom_file):
        if os.path.isfile(pom_file):
            f = open(pom_file, 'w')
            f.write(dom.toxml())
            f.close()
        self.pom = dom

    def get_pom_groupid(self):
        dom = self.read_pom(os.path.join(self.get_temp_dir(), self.branch, "pom.xml"))
        return dom.getElementsByTagName('groupId')[0].childNodes[0].nodeValue

    def get_package_name(self):
        dom = self.read_pom(os.path.join(self.get_temp_dir(), self.branch, "pom.xml"))
        return dom.getElementsByTagName('name')[0].childNodes[0].nodeValue

    def get_pom_artifactid(self):
        dom = self.read_pom(os.path.join(self.get_temp_dir(), self.branch, "pom.xml"))
        return dom.getElementsByTagName('artifactId')[0].childNodes[0].nodeValue

    def get_pom_version(self):
        dom = self.read_pom(os.path.join(self.get_temp_dir(), self.branch, "pom.xml"))
        return dom.getElementsByTagName('version')[0].childNodes[0].nodeValue

    def get_module_packaging(self, module):
        dom = self.read_pom(os.path.join(self.get_temp_dir(), self.branch, module, "pom.xml"))
        try:
            packaging = dom.getElementsByTagName('packaging')[0].childNodes[0].nodeValue
        except Exception as e:
            packaging = 'zip'
        return packaging

    def is_multimodule_project(self):
        dom = self.read_pom(os.path.join(self.get_temp_dir(), self.branch, "pom.xml"))
        if dom.getElementsByTagName('modules').length != 0 :
            return True
        else:
            return False

    def get_multimodule_children(self):
        dom = self.read_pom(os.path.join(self.get_temp_dir(), self.branch, "pom.xml"))
        try:    
            total_modules = dom.getElementsByTagName('modules').length
        except Exception as e:
            print "Error Detected: {0}".format(e)
        if total_modules == 0 :
            return dom.getElementsByTagName('artifactId')[0].childNodes[0].nodeValue
        else:
            counter = 0
            module_list = []
            while counter <= total_modules:
                module_list.append(dom.getElementsByTagName('modules')[0].getElementsByTagName('module')[counter].childNodes[0].nodeValue)
                counter += 1
        return module_list

    def get_module_nexus_url(self, module):
        nexus_host_url = 'http://{0}:{1}'.format(self.C.get_nexus_host(), self.C.get_nexus_port())
        nexus_service_base = 'nexus/service/local/repositories/releases/content'
        groupid = self.get_pom_groupid()
        version = self.version
        packaging = self.get_module_packaging(module)
        artifact = '{0}-{1}.{2}'.format(module, version, packaging)
        return '{0}/{1}/{2}/{3}'.format(nexus_host_url, nexus_service_base, groupid, artifact)

    def get_module_url_dict(self):
        module_dict = {}
        modules = self.get_multimodule_children()
        for module in modules:
            module_dict[module] = self.get_module_nexus_url(module)
        return module_dict

    def set_pom_version(self, version):
        pom_files = self.get_poms()
        for pom_file in pom_files:
            dom = self.read_pom(pom_file)
            dom.getElementsByTagName('version')[0].childNodes[0].nodeValue = version
            self.write_pom(dom, pom_file)

    def read_releases_url(self):
        groupid = '/'.join(self.get_pom_groupid().split('.'))
        artifactid = self.get_pom_artifactid()
        url = 'http://{0}:{1}/nexus/content/repositories/releases/{2}/{3}/maven-metadata.xml'.format(self.C.get_nexus_host(),
                                                                                                     self.C.get_nexus_port(),
                                                                                                     groupid,
                                                                                                     artifactid)
        try:
            raw_releases_list = urllib2.urlopen(url)
            release_lines = ''
            for line in raw_releases_list.readlines():
                release_lines = release_lines + ' ' + line
            return release_lines.lstrip()
        except Exception as e:
            print "Error Detected: {0}".format(e)
            return False

    def get_previous_releases(self):
        """
        This mess is due to how the Scenario Manager modules are named, and must be reorganised at some point.
        This code will cleanly handle new multimodule projects that have been created with lessons learned from
        having to relese scenariomanager.
        MUST FIX ScenarioManager modules and merge all non Webapp modules into a single module.
        """
        version_list = []
        modules_list = []
        artifactid = self.get_pom_artifactid()
        if self.is_multimodule_project():    
            if artifactid == 'ScenarioManager':
                for module in self.get_multimodule_children():
                    if module != 'ScenarioManager-webapp':
                        if module == 'sql':
                            modules_list.append('-'.join([artifactid, 'ddl']))
                        else:
                            modules_list.append('-'.join([artifactid, module]))
            else:
                modules_list = self.get_multimodule_children()
            modules_list.append(artifactid)
        else:
            modules_list = [artifactid]
        for module in modules_list:
            url = 'http://{0}:{1}/nexus/content/repositories/releases/{2}/{3}/maven-metadata.xml'.format(self.C.get_nexus_host(),
                                                                                               self.C.get_nexus_port(),
                                                                                               '/'.join(self.get_pom_groupid().split('.')),
                                                                                               module)
            print url
            try:
                raw_releases_list = urllib2.urlopen(url)
                release_lines = ''
                for line in raw_releases_list.readlines():
                    release_lines = release_lines + ' ' + line
                xml = release_lines.lstrip()
            except Exception as e:
                print "Error Detected: {0}".format(e)          
            
            dom = parseString(xml)
            length = dom.getElementsByTagName('version').length
            count = 0
            while count != (length):
                version = dom.getElementsByTagName('version')[count].childNodes[0].nodeValue
                if self.V.is_valid_version(version):
                    if isinstance(version, unicode):
                        version_list.append(version)
                    elif isinstance(version, str):
                        version_list.append(version)
                count += 1
        print set(version_list)
        #sys.exit(1)
        return list(set(version_list))

    def get_releases_dict(self):
        release_alphas = []
        release_betas = []
        release_candidates = []
        release_dict = {}
        for version in self.get_previous_releases():
            if isinstance(version, unicode):
                if self.V.is_valid_version(version.encode('utf-8')):
                    if version.encode('utf-8').find('A') != -1:
                        release_alphas.append(version.encode('utf-8'))
                    elif version.encode('utf-8').find('B') != -1:
                        release_betas.append(version.encode('utf-8'))
                    elif version.encode('utf-8').find('R') != -1:
                        release_candidates.append(version.encode('utf-8'))
            elif isinstance(version, str):
                if self.V.is_valid_version(version):
                    if version.find('A') != -1:
                        release_alphas.append(version)
                    elif version.find('B') != -1:
                        release_betas.append(version)
                    elif version.find('R') != -1:
                        release_candidates.append(version)
        release_dict['release_alphas'] = self.V.validate_version_list(release_alphas)[-5:]
        release_dict['release_betas'] = self.V.validate_version_list(release_betas)[-5:]
        release_dict['release_candidates'] = self.V.validate_version_list(release_candidates)[-5:]
        return release_dict

    def get_email_addresses(self, version):
        return self.C.get_mail_string(version)

    def get_year(self):
        return int(strftime("%Y", gmtime()))

    def get_week_of_the_year(self):
        return int(date.today().strftime("%W"))
    
    def get_end_digit(self, version):
        regex = re.compile("(?P<RELEASE>[A,B,RC,GA]?)(?P<NUMBER>[0-9]{0,3})")
        m = regex.match(version)
        version_dict = m.groupdict()
        return version_dict['NUMBER']    

    def get_next_unique_number(self):
        numbers = []
        version_list = self.get_previous_releases()
        for version in version_list:
            if version.split('.')[1] == str(self.get_week_of_the_year()):
                end_digit = self.get_end_digit(version.split('.')[3])
                if len(end_digit) == 1:
                    numbers.append(''.join(['0', end_digit]))
                else:
                    numbers.append(end_digit)
        numbers.sort()
        print numbers
        if len(numbers) == 0:
            return int(1)
        elif len(numbers) == None:
            return int(1)
        elif len(numbers) >= 1:
            nextversion = int(numbers[-1]) + 1
            return nextversion 
        else:
            nextversion = int(numbers[0]) + 1
            return nextversion 
    
    def get_generated_version_number(self, drop):
        release_state = 'A'
        return '{0}.{1}.{2}.{3}{4}'.format(self.get_year(), self.get_week_of_the_year(), drop, release_state, self.get_next_unique_number())

    # Beware dog vommit below, should be using renderengine but has issues when imported.
    def serve_template(self, template_name, **kwargs):
        from mako.template import Template
        from mako.lookup import TemplateLookup
        from mako import exceptions
        try:
            render_template = Template(filename=os.path.join(os.path.join(os.path.expanduser('~'), 'versions/canvas/release-tools/trunk/src/fsa/releasetools/classes'), 'templates', template_name))
            return render_template.render(**kwargs)
        except:
            print exceptions.text_error_template().render()
    # End of dog vommit
    
    def email_release_notification(self):
        self.read_pom(os.path.join(self.get_temp_dir(), self.branch, "pom.xml"))
        self.data = self.get_releases_dict()
        self.data['author'] = self.C.get_release_author()
        self.data['email_recipients'] = self.get_email_addresses(self.version)
        self.data['title'] = self.get_package_name()
        self.data['version'] = self.get_version_built()
        self.data['release_time'] = strftime("%H:%M", self.get_buildtime())
        self.data['release_date'] = strftime("%d/%b/%Y", self.get_buildtime())
        self.data['release_day'] = strftime("%a", self.get_buildtime())
        self.data['svn_location'] = self.get_svn_location()
        self.data['svn_revision'] = self.get_svn_revision()
        self.data['modules'] = self.get_module_url_dict()
        pprint.pprint(self.data)
        print self.serve_template('release-email.html', C=self.data)
        print
        print self.serve_template('release-email.txt', C=self.data)
        if self.suppress_email == False:
            self.notify_release(self.serve_template('release-email.html', C=self.data), self.serve_template('release-email.txt', C=self.data))

    def notify_release(self, message_html, message_text):
        print "Sending notification emails to the following: "
        for recipient in self.data['email_recipients']:
            print "\t{0}".format(recipient)
        print
        message = Message()
        message.From = 'charles.sibbald@fsa.gov.uk'
        message.To = self.data['email_recipients']
        message.Subject = "{0} version {1} released".format(self.data['title'], self.data['version'])
        message.Body = message_text
        message.Html = message_html
        print self.C.get_smtp_host()
        mailer = Mailer(self.C.get_smtp_host())
        mailer.send(message)

if __name__ == '__main__':
    M = MavenTools('ScenarioManager', revision='HEAD', notify=True)
    drop = 0
    release_state = 'A'
    M.package()
    print M.get_previous_releases()
    number = M.get_next_unique_number()
    print number