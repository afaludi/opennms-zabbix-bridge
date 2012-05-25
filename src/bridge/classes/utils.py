# vim: tabstop=4 shiftwidth=4 softtabstop=4
import os
import fnmatch
import sys
import subprocess
import stat
import time

def check_environment_vars():
    if os.getenv('MAVEN_HOME') == None:
        print "MAVEN_HOME Environment variable must be set!"
        sys.exit(1)
    elif os.getenv('JAVA_HOME') == None:
        print "JAVA_HOME Environment variable must be set!"
        sys.exit(1)
    else:
        mvn = os.path.join(os.getenv('MAVEN_HOME'), 'bin', 'mvn')

def locate(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern
    in and below supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)


def execute(execution_list):
    execute = subprocess.Popen(execution_list, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while 1:
        logLine = execute.stdout.readline()
        if (not logLine) and (exitcode is not None):
            break
        log = logLine[:-1]
        if not log == '':
            print log
    execute.poll()
    if execute.returncode ==0 :
        sys.exit()

def executePoll(execution_list):
    import subprocess
    import os
    import sys
    try:
        execute = subprocess.check_call(execution_list, shell=False,)
    except Exception as e:
        print "Process Execution Error:"
        print e
        sys.exit(1)

def singleton(cls):
    __instances = {}
    def getinstance():
        if cls not in __instances:
            __instances[cls] = cls()
        return __instances[cls]
    return getinstance


def timethis(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        r = func(*args, **kwargs)
        end = time.time()
        print func, end-start
        return r
    return wrapper


def fileFinder(base_dir, target_file):
    matches = []
    for root, dirnames, filenames in os.walk(base_dir):
        for filename in fnmatch.filter(filenames, target_file):
            matches.append(os.path.join(root, filename))
    return matches


def func_once(func):
    "A decorator that runs a function only once."
    def decorated(*args, **kwargs):
        try:
            return decorated._once_result
        except AttributeError:
            decorated._once_result = func(*args, **kwargs)
            return decorated._once_result
    return decorated

def method_once(method):
    "A decorator that runs a method only once."
    attrname = "_%s_once_result" % id(method)
    def decorated(self, *args, **kwargs):
        try:
            return getattr(self, attrname)
        except AttributeError:
            setattr(self, attrname, method(self, *args, **kwargs))
            return getattr(self, attrname)
    return decorated

# Example, will only parse the document once
#@func_once
#def get_document():
#    import xml.dom.minidom
#    return xml.dom.minidom.parse("document.xml")



if __name__ == '__main__':
    pass
