import fnmatch
import os
import pprint

base_dir = os.path.join(os.path.expanduser('~'), 'tmp', 'svntest', 'testcheckout', 'mock-project', 'trunk')


def file_finder(base_dir, target_file):
    matches = []
    for root, dirnames, filenames in os.walk(base_dir):
        for filename in fnmatch.filter(filenames, target_file):
            matches.append(os.path.join(root, filename))
    return matches

for pom in file_finder(base_dir, 'pom.xml'):
    print pom