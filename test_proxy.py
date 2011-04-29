#!/usr/bin/env python

import httplib
import sys

h = httplib.HTTPConnection(sys.argv[1], int(sys.argv[2]))
h.connect()
h.request("GET", "http://api.twitter.com/1/followers/ids.json?user_id=20296417")
resp = h.getresponse()
new_ids = resp.read()
new_ids = new_ids.lstrip('[')
new_ids = new_ids.rstrip(']')
new_ids = new_ids.split(',')

print new_ids
