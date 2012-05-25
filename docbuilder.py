#!/usr/bin/env python
import os
import sys
userhome = os.path.expanduser("~")

projectname = "releasetools"

def builddocs():
    sphinx = os.path.join(userhome, "bin", "sphinx-build")
    docsource = os.path.abspath(os.path.join("docs", "source"))
    docdest = os.path.join(userhome, "www", projectname)
    if not os.path.exists(docdest):
        try:
            print "Creating Destination Docs Directory: {0}".format(docdest)
            os.makedirs(docdest)
        except OSError :
            if exc.errno == errno.EEXIST:
                pass
            else: raise

    doThis = "{0} {1} {2} ".format(sphinx, docsource, docdest)
    print "Attempting to run {0} against {1}".format(sphinx, docsource)
    print "Docs target: {0}".format(docdest)
    executeThis = os.system(doThis)


if __name__ == "__main__":
    builddocs()