#!/usr/bin/python

import sys
import os

prism_file_path = sys.argv[1]
prism_file = open(prism_file_path, "r")
prism_dirname = os.path.dirname(prism_file_path)

for line in prism_file:
    if "INCLUDE " in line:
        included_file_path = line.split(" ")[1].rstrip()
        included_file = open(os.path.join(prism_dirname, included_file_path), "r")
        for included_line in included_file:
            print included_line,
    else:
        print line,
