#!/usr/bin/env python

import sys
import random

UNKNOWN_RATE = .3
nlines = int(sys.argv[1])

f = open(sys.argv[2], 'w')
count = 0
for line in range(0, nlines):
    count += 1
    nfol = random.randint(0,150)
    if nfol == 0:
        continue
    f.write(str(line))
    for fol in range(0,nfol):
        folid = random.randint(0, nlines * (1. + UNKNOWN_RATE))
        f.write('\t' + str(folid))
    f.write('\n')
    if count % 1000 == 0:
        print str(count) + " users written"

f.close()
