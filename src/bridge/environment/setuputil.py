# vim: tabstop=4 shiftwidth=4 softtabstop=4
import os, site, errno;
import sys
import tarfile
import shutil

try:
    from fsa.releasetools.classes import downloader
except ImportError:
    try :
        from src.fsa.releasetools.classes import downloader
    except ImportError:
        raise

python_version = sys.version[:3]

userhome = os.path.expanduser("~")

def checkenvpaths(path):
    currentpath = os.environ.get('PATH')
    if currentpath.find(path) == 0 :
        print "Python Path has been set to : {0}".format(path)
        return True
    elif currentpath.find(path) == -1:
        print "Python Path has NOT been set.................!"
        return False

def detect_environment():
    environment = {}
    environment['os_detected'] = sys.platform
    python_version = sys.version[:3]
    currentpath = os.environ.get('PATH')
    if environment['os_detected'] == 'darwin' :
        environment['userprofile'] = os.path.join(userhome, ".bash_profile")
        environment['fileName'] = os.path.join(userhome, '.pydistutils.cfg')
        environment['bin_dir'] = os.path.join(userhome, "bin")
        environment['install_dir'] = os.path.join(userhome, "Library", "python", python_version, "site-packages")
        environment['python_dir'] =os.path.join("/Library", "Frameworks", "Python.framework", "Versions", python_version, "bin")
        environment['ssh_dir'] = os.path.join(userhome, '.ssh')
    elif environment['os_detected'] == 'linux' or 'linux2' :
        environment['userprofile'] = os.path.join(userhome, ".bashrc")
        environment['fileName'] = os.path.join(userhome, '.pydistutils.cfg')
        environment['bin_dir'] = os.path.join(userhome, "bin")
        environment['install_dir'] = os.path.join(userhome, "Library", "python", python_version, "site-packages")
        environment['python_dir'] = os.path.join(userhome, "Library", "Frameworks", "Python.framework", "Versions", python_version, "bin")
        environment['ssh_dir'] = os.path.join(userhome, '.ssh')
    elif environment['os_detected'] == 'sunos5' :
        environment['userprofile'] = os.path.join(userhome, ".profile")
        environment['fileName'] = os.path.join(userhome, '.pydistutils.cfg')
        environment['bin_dir'] = os.path.join(userhome, "bin")
        environment['install_dir'] = os.path.join(userhome, "Library", "python", python_version, "site-packages")
        environment['python_dir'] = os.path.join(userhome, "Library", "Frameworks", "Python.framework", "Versions", python_version, "bin")
        environment['ssh_dir'] = os.path.join('/etc', 'ssh', 'keys')
    elif environment['os_detected'] == 'windows' or 'win32' :
        environment['fileName'] = os.path.join(userhome, '.pydistutils.cfg')
        environment['bin_dir'] = os.path.join(userhome, "bin")
        environment['install_dir'] = os.path.join(userhome, "Library", "python", python_version, "site-packages")
        environment['python_dir'] = os.path.join(userhome, "Library", "Frameworks", "Python.framework", "Versions", python_version, "bin")
        environment['ssh_dir'] = os.path.join(userhome, '.ssh')
    else:
        environment['fileName'] = os.path.join(userhome, '.pydistutils.cfg')
        environment['bin_dir'] = os.path.join(userhome, "bin")
        environment['install_dir'] = os.path.join(userhome, "lib", "python", python_version, "site-packages")
    return environment

environment = detect_environment()

system_os = {   'darwin' : "[install]\ninstall_lib = {0} \ninstall_scripts = {1} \n".format(environment['install_dir'], environment['bin_dir']),
                'linux' : "[install]\ninstall_lib = {0} \ninstall_scripts = {1} \n".format(environment['install_dir'], environment['bin_dir']),
                'linux2' : "[install]\ninstall_lib = {0} \ninstall_scripts = {1} \n".format(environment['install_dir'], environment['bin_dir']),
                'sunos5' : "[install]\ninstall_lib = {0} \ninstall_scripts = {1} \n".format(environment['install_dir'], environment['bin_dir']),
                'windows' : "[install]\ninstall_lib = {0} \ninstall_scripts = {1} \n".format(environment['install_dir'], environment['bin_dir']),
            }

class Filer():
    def __init__(self):
        print "Filer initalised"

    def createFile(self, FQFileName):
        self.fileName = FQFileName
        if not os.path.exists(self.fileName):  # Avoid clobbering files
            try:
                print
                print "Creating : {0}".format(self.fileName)
                self.o = open(self.fileName, "w")
            finally:
                self.o.flush()
                self.o.close()

    def writeThisToFile(self, stringToWrite):
        if os.path.exists(self.fileName):  # Avoid clobbering files
            try:
                print
                print "Writing to : {0}".format(self.fileName)
                self.w = open(self.fileName, "w")
                self.w.write(stringToWrite)
                self.w.write("\n")
            finally:
                self.w.flush()
                self.w.close()


class ThirdPartyApp():
    def __init__(self):
        print
        print "Third Party Install Instance Initialised"
        self.thirdparty = os.path.join(os.getcwd(), "thirdparty")
        if not os.path.exists(self.thirdparty):
            try:
                print
                print "Creating Thirdparty Directory: {0}".format(self.thirdparty)
                os.mkdir(self.thirdparty)
            except OSError :
                pass

        if not os.path.exists(environment['install_dir']):
            try:
                print "Creating Python Egg Directory: {0}".format(environment['install_dir'])
                os.makedirs(environment['install_dir'])
            except OSError :
                pass

        if not os.path.exists(environment['bin_dir']):
            try:
                print "Creating Python Egg Directory: {0}".format(environment['bin_dir'])
                os.makedirs(environment['bin_dir'])
            except OSError :
                pass

    def legacy_download_this(self, url, to_dir, saveas=None):
        """This Class Method is only used once to pull down the very basic requirements of the project.
        **kwargs saveas is used if the downloaded file should be renamed when saved to disk.
        """
        import urllib2, shutil
        self.url = url
        self.to_dir = to_dir
        self.saveas = saveas
        if self.saveas:
            self.saveto = os.path.join(self.to_dir, self.saveas)
        else:
            self.saveto = os.path.join(self.to_dir, os.path.basename(self.url))
            
        self.src = self.dst = None
        if not os.path.exists(self.saveto):  # Avoid repeated downloads
            try:
                print
                print "Attempting to Download : {0} from {1}".format(os.path.basename(self.url), os.path.dirname(self.url))
                self.src = urllib2.urlopen(self.url)
                # Read/write all in one block, so we don't create a corrupt file
                # if the download is interrupted.
                self.data = self.src.read()
                self.dst = open(self.saveto,"wb"); self.dst.write(self.data)
            finally:
                if self.src:
                    self.src.close()
                if self.dst:
                    self.dst.close()
                    print "{0} Downloaded Successfully".format(os.path.basename(self.url))
                    print
        return os.path.realpath(self.saveto)


    def determine_compression_algorithim(self, file):
        self.file = file
        if self.file.endswith(".tar") :
            self.arc_type = 'r:*'
        elif self.file.endswith(".gz") :
            self.arc_type = 'r:gz'
        elif self.file.endswith(".bz2") :
            self.arc_type = 'r:bz2'
        elif self.file.endswith(".zip") :
            self.arc_type = 'r:*'
        print "File {0} detected as a {1} ".format(self.file, self.arc_type.split(":")[1])
        return self.arc_type

    def extract_archive(self, file, to_dir):
        self.file = file
        self.to_dir = to_dir
        print "Archive to extract: ", self.file
        self.tar = tarfile.open(self.file, determine_compression_algorithim(self.file))
        self.tar.extractall(self.to_dir)
        self.tar.close()

    def read_thirdparty_config(self):
        if os.path.exists("thirdparty.cfg"):
            self.fileToRead = ("thirdparty.cfg")
        print self.fileToRead
        self.thirdparty_app = {}
        self.f = open(self.fileToRead,'r')
        self.details = self.f.readlines()
        for self.detail in self.details:
            if not self.detail.isspace() :
                if not self.detail.startswith('#'):
                    self.pair = self.detail.split('||')
                    if self.pair[0]:
                        self.thirdparty_app[self.pair[0].strip()] = (self.pair[1].strip(), self.pair[2].strip())
        return self.thirdparty_app


def cleandest():
    builddest = os.path.abspath("build")
    distdest = os.path.abspath("dist")
    buildegg = os.path.join(environment['install_dir'], "releasetools-*")
    if os.path.exists(builddest):
        try:
            print "Cleaning Build Destination: {0}".format(builddest)
            shutil.rmtree(builddest)
        except OSError :
            pass

    if os.path.exists(distdest):
        try:
            print "Cleaning Dist Destination: : {0}".format(distdest)
            shutil.rmtree(distdest)
        except OSError :
            pass

    if os.path.exists(buildegg):
        try:
            print "Destroying Previously Built Egg: : {0}".format(buildegg)
            shutil.rmtree(buildegg)
        except OSError :
            pass

def configure_python() :
    """Configure python to use seperate site packages dir if NO Virtual Environment is detected"""
    print "Operating System Detected : ", environment['os_detected']
    f = Filer()
    f.createFile(environment['fileName'])
    f.writeThisToFile(system_os[environment['os_detected']])
    third_party_app = ThirdPartyApp()
    third_party_app.legacy_download_this('http://nexus.art:8081/nexus/service/local/repositories/thirdparty/content/com/telecommunity/peak/ez_setup/0.6.11/ez_setup-0.6.11.py',
                                         environment['install_dir'],
                                         saveas='ez_setup.py')
    app_list = third_party_app.read_thirdparty_config()
    for each in app_list:
        if each == 'ez_setup':
            third_party_app.legacy_download_this(app_list[each][0], os.getcwd(), saveas='ez_setup.py')
        else:
            third_party_app.legacy_download_this(app_list[each][0], os.path.join(os.path.join(os.getcwd(), "thirdparty")))
    