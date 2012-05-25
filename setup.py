# vim: tabstop=4 shiftwidth=4 softtabstop=4
import os, site, errno;
import sys
python_version = sys.version[:3]
if python_version not in ('2.6','2.7'):
    print "Python Version Detected as: %s" % python_version
    print """This application is only compatible with Python 2.6 and greater.
You will have to install at least python2.6 to use this application.

NOTE: Python2.7 is still in development mode, and has not been tested
with this software or many of its dependencies."""
    sys.exit(1)

rawversion = sys.version[:3]
rawversion.split(".")
sysversion = rawversion.split(".")[0] + rawversion.split(".")[1]
DEFAULT_VERSION = "0.6c11" 


from src.fsa.releasetools.environment import setuputil

setuputil.cleandest()
environment = setuputil.detect_environment()
site.addsitedir(os.path.expanduser(environment['install_dir']))
sys.path.append(os.path.expanduser(environment['install_dir']))
sys.path.append(os.path.expanduser(environment['bin_dir']))
setuputil.configure_python()


from ez_setup import use_setuptools
use_setuptools(version=DEFAULT_VERSION)

from setuptools import setup, find_packages

version = "0.0.2"
setup (
    # basic package data
    name = "releasetools",
    version=version,
    description="Standard Harnes for all python shared utilities",
    long_description="""Python Project for Releasing.""",
    classifiers=[],
    keywords='',
    author='Charles Sibbald',
    author_email='email address',
    url='',
    license='GPL',

    #package structure
    packages = find_packages('src',
                            exclude=['ez_setup', 'tests', 'code_coverage']),
                            package_dir = {'':'src'},
                            zip_safe = False,

    # install your application executable
    entry_points = {
        'console_scripts': [
            'environment = fsa.releasetools.environment.installer:main',
            'agentP = fsa.releasetools.agentP.agentProvocateur:main',
            'releasetool = fsa.releasetools.classes.releasetool:main',
        ]
    },
    install_requires = [
        'docutils',
        'nose',
        'coverage',
        'zope.interface',
        'zope.exceptions',
        #'urlgrabber',
        'unittest2',
        'sphinx',
        'pbp.skels',
        'mocker',
        'twisted == 10.1.0',
        'pexpect',
        'rython',
		'mako',
    ],
    # use this to run tests automatically,
    # but to see coverage report run ~/bin/nosetests -v --with-coverage
    test_suite='nose.collector',
)
