#!/usr/bin/python

import sys

p = float(sys.argv[1])

for n in range(11):
    print 1 - (1 - p)**n
