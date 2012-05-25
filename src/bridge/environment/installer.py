# vim: tabstop=4 shiftwidth=4 softtabstop=4
import os
import sys
import subprocess
import stat

from fsa.releasetools.classes.filer import Filer
from fsa.releasetools.environment.setuputil import ThirdPartyApp

userhome = os.path.expanduser("~")

class Install():
    """Install Class is used to setup an environment from scratch

    The install Class must be run against a fresh install of ubuntu 10.04
    desktop or server. Ideally server if the desktop will not be used for
    any gui work.
    """

    def __init__(self):
        print "Installer initalised"


    def releasetools_profile(self):
        """Minimalistic .profile file"""

        self.releasetools_profile_file = """# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

# the default umask is set in /etc/profile; for setting the umask
# for ssh logins, install and configure the libpam-umask package.
#umask 022

# if running bash
if [ -n "$BASH_VERSION" ]; then
    # include .bashrc if it exists
    if [ -f "$HOME/.bashrc" ]; then
        . "$HOME/.bashrc"
    fi
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$HOME/bin:\$PATH"
fi

PS1="${LOGNAME}@[BCVM] \w$ "
export PS1
export EDITOR=vi
export PYTHONPATH=~/lib/python/2.6/site-packages

. ~/env.sh
"""
        return self.releasetools_profile_file


    def init_script_agentp(self):
        """AgentP init.d start script"""

        agentp_init = """start on runlevel [35]
    exec sudo -H -E su - releasetools -c '/home/releasetools/bin/agentP'
end script

"""
        return agentp_init


    def executioner(self, execution_list):
        ###TODO: Refactor into single method - to avoid repetition with below
        self.execution_list = execution_list
        execute = subprocess.Popen(self.execution_list, shell=False, stdout=subprocess.PIPE)
        while 1:
            self.logLine = execute.stdout.readline()
            self.exitcode = execute.poll()
            if (not self.logLine) and (self.exitcode is not None):
                break
            self.log = self.logLine[:-1]
            if not self.log == '':
                print self.log

    def ubuntu_update(self):
        self.update = ['sudo', 'aptitude', 'update']
        self.autoclean = ['sudo', 'aptitude', 'autoclean']
        #Execute the above lists in order
        print "Updating Ubuntu System Packages"
        self.executioner(self.update)
        print "Auto-cleaning packages downloaded during installs/updates"
        self.executioner(self.autoclean)

    def apt_get_install(self, package_list):
        self.package_list = package_list
        self.apt_get = ['sudo', 'apt-get', '-y', 'install']
        for package in self.package_list:
            self.apt_get.append(package)
        print "Installing packages using apt-get"
        print self.apt_get
        self.executioner(self.apt_get)

    def update_aptitude_repositories(self, repository):
        self.repository = repository
        self.update_repo = ['sudo', 'apt-add-repository', self.repository]
        print "Updating Ubuntu Repositories with: {0}".format(self.repository)
        self.executioner(self.update_repo)
        self.ubuntu_update()

    def write_config_file(self, text, full_path_and_file):
        self.text = text
        self.path = full_path_and_file
        f = Filer()
        if not os.path.exists(self.path):
            try:
                os.makedirs(os.path.dirname(self.path))
            except OSError :
                print "Directory: {0} Exists".format(os.path.dirname(self.path))
        f.createFile(os.path.join(self.path))
        f.writeThisToFile(self.text)

    def append_config_to_file(self, text, full_path_and_file):
        self.text = text
        self.fileName = full_path_and_file
        f = Filer()
        if os.path.exists(self.fileName):
            try :
                f.appendThisToFile(self.text, self.fileName)
            except OSError :
                print "Unable to append to file: {0}".format(self.fileName)

    def make_all_required_dirs(self):
        """Method to create all directories in a dictionary, and ownership details"""
        self.dir_dictionary = {
            '/home/releasetools/myweb' : 'releasetools',
            '/home/releasetools/myweb/requestrouter' : 'releasetools',
            '/home/releasetools/deploy_history' : 'releasetools',
            '/opt/pythonvm' : 'releasetools',
            '/opt/pythonvm/dbdumps' : 'releasetools',
            '/opt/pythonvm/deploylogs': 'releasetools',
            '/var/log/agentP': 'releasetools',
            '/var/log/webtool': 'releasetools',
        }
        for dir in self.dir_dictionary:
            print "Creating Directory: {0}, Owned by {1}".format(dir, self.dir_dictionary[dir])
            #Can not use native python due to sudo issue.
            try :
                if not os.path.exists(dir):
                    os.system('sudo mkdir -p {0}'.format(dir))
                    os.system('sudo chown -R {0}:{1} {2} '.format(self.dir_dictionary[dir], self.dir_dictionary[dir], dir))
            except OSError:
                pass

    def make_symlinks(self, source, dest):
        self.source = source
        self.dest = dest
        if os.path.exists(self.source):
            if not os.path.exists(self.dest):
                try:
                    self.symlink_cmd = ['sudo', 'ln', '-s', self.source, self.dest ]
                    self.executioner(self.symlink_cmd)
                except OSError:
                    pass

    def deploy_tarballs(self):
        """Deploy a list of required tarballs"""
        self.thirdpartyapp = ThirdPartyApp()
        self.tarballs = {
            'ant' : ['http://elvis.ithrconsulting.com:8080/dropbox/vm/apache-ant-1.7.1.tar.gz', '/usr/local'],
            'maven' : ['http://elvis.ithrconsulting.com:8080/dropbox/vm/apache-maven-2.0.11.tar.gz', '/usr/local'],
            'jboss423GA' : ['http://elvis.ithrconsulting.com:8080/dropbox/vm/jboss-4.2.3.GA.tar.gz', '/usr/local'],
            'jboss403SP1' : ['http://elvis.ithrconsulting.com:8080/dropbox/vm/jboss-4.0.3SP1.tar.gz', '/usr/local'],
        }
        for pkg in self.tarballs:
            print
            print
            print "Downloading Downloading {0}, this may take a while".format(pkg)
            #TODO : add urlgrabber method to setuputil.
            print "Please bear with me while i write a download progress method"
            self.thirdpartyapp.legacy_download_this(self.tarballs[pkg][0], userhome)
            #self.progress_download_this(self.tarballs[pkg][0], userhome)
            self.tarball = os.path.basename(self.tarballs[pkg][0])
            try :
                if os.path.exists(self.tarballs[pkg][1]):
                    if self.tarball.endswith('.tar.gz'):
                        self.extract_cmd = ['sudo', 'tar', '-zxvf', os.path.join(userhome, self.tarball), '-C', self.tarballs[pkg][1]]
                        self.executioner(self.extract_cmd)
                        os.remove(os.path.join(userhome, self.tarball))
                    elif self.tarball.endswith('.dmp'):
                        print "Detected Oracle DB Dump {0}, Not extracting.".format(self.tarball)
                        os.system('sudo mkdir -p {0}'.format(self.tarballs[pkg][1]))
                        os.system('sudo chown -R releasetools:releasetools {0}'.format(self.tarballs[pkg][1]))
                        self.dbdump_string = "mv /home/releasetools/{0} /opt/pythonvm/dbdumps".format(self.tarball)
                        os.system(self.dbdump_string)
                elif not os.path.exists(self.tarballs[pkg][1]):
                    os.system('sudo mkdir -p {0}'.format(self.tarballs[pkg][1]))
                    os.system('sudo chown -R releasetools:releasetools {0}'.format(self.tarballs[pkg][1]))
                    if self.tarball.endswith('.tar.gz'):
                        self.extract_cmd = ['sudo', 'tar', '-zxvf', os.path.join(userhome, self.tarball), '-C', self.tarballs[pkg][1]]
                        self.executioner(self.extract_cmd)
                        os.remove(os.path.join(userhome, self.tarball))
                    elif self.tarball.endswith('.dmp'):
                        print "Detected Oracle DB Dump {0}, Not extracting.".format(self.tarball)
                        os.system('sudo mkdir -p {0}'.format(self.tarballs[pkg][1]))
                        os.system('sudo chown -R releasetools:releasetools {0}'.format(self.tarballs[pkg][1]))
                        self.dbdump_string = "mv /home/releasetools/{0} /opt/pythonvm/dbdumps".format(self.tarball)
                        os.system(self.dbdump_string)
            except OSError:
                print "{0} Does not exist".format(self.tarballs[pkg][1])

    def change_owner(self, path, owner, group):
        self.path = path
        self.owner = owner
        self.group = group
        try:
            if os.path.exists(self.path):
                print "Changing {0}: to be owned by {1}:{2}".format(self.path, self.owner, self.group)
                self.new_owner = "{0}:{1}".format(self.owner, self.group)
                self.change_owner_cmd = ['sudo', 'chown', '-R', self.new_owner, self.path ]
                self.executioner(self.change_owner_cmd)
        except OSError:
            pass


def main():
    install = Install()
    install.configure_webtool()

