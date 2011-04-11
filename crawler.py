#!/usr/bin/env python
"""
A webcrawler that crawls webpages in the *.caltech.edu domain

TODO:
* Clean up (e.g. make class + fix style (line width etc.))
* Implement robots.txt adherence
* Make it a class rather than a script
* Expand w/ possibility of watching in-degree (extra credit)

BUGS (minor):
* for some reason one entry of the form '~kip/"' made it into the results.
* for some reason the result for 'http://www.its.caltech.edu/' has got no value

"""
from fetcher import fetch_links
import re, csv
from collections import deque
import random
import time


# Seeded with BarackObama
def crawler(URL_seeds=['813286']):

	MAX_ITERATIONS = 200000 # How many iterations? Finite execution, despite tons of garbage pages.
	MAX_RESULTS = 5000 #20010 # How many results? Finite execution, rather than crawling entire reachable(URL_seeds)'
	URLS_FETCH = 3
	
	URLs_found = set(URL_seeds) # set holding pages all URLs encountered
	nusers = 1

	queue = deque(URL_seeds) # queue holding pages to process
	
	count = 0
	output = 1

        # file to save structure in
        f = open('structure.dat','w')

        nlookups = 0
        starttime = time.time()

	while (queue) and (count < MAX_ITERATIONS) and (nusers < MAX_RESULTS):

                if nlookups >= 150:
                    nlookups = 0
                    sleeptime = 3600 - (time.time() - starttime)
                    if sleeptime > 0:
                        print '\nSleeping for ' + str(sleeptime) + ' seconds\n'
                        time.sleep(sleeptime)
                    starttime = time.time()
		user = queue.popleft() # fetch next page (FIFO -> Breath First)
		nusers += 1
                followers = fetch_links(user)
                nlookups += 1

                if followers == None :
                    queue.appendleft(user)
                    nusers -= 1
                    print '\nTwitter is busy. Pausing 10 min.\n'
                    time.sleep(600)
                    continue

		if (not (followers == None) and len(followers) > 0 and not (followers[0] == '')):
                        new_pages = []
			# Add unencountered pages to queue
                        for ids in followers :
                            if not (ids in queue or ids in URLs_found) :
                                new_pages.append(ids)

                        write_user(f, user, followers)
                        count += 1
       			queue.extend(new_pages) # add pages to queue	
        
		# Print progress
		if (((count % output) == 0) or ((nusers % 1) == 0)):
			output = count / output
			print "Progress: %d pages crawled. %d results found. Queue of %d" % (count, nusers, len(queue))
			
	f.close()

	# Output results
	print "\nFinished!"
	print "Found %d results, by crawling through %d pages. Queue at termination: %d" % (nusers, count, len(queue))


def write_user(writefile, user, followers) :
    writefile.write(user + ':')
    for fol_id in followers :
        writefile.write(' ' + fol_id)
    writefile.write('\n')    

#Entrance of this script, just like the "main()" function in C.

if __name__ == "__main__":
    import sys, pstats, cProfile, os.path

    if len(sys.argv)==1 :
       if len(sys.argv)==1:
    		# No args: Use default startpage
    		print crawler()
       else:
              try:
                   i = 0;
                   input_filename = sys.argv[1];
                   f1 = open(input_filename, "r")
                   for line in f1:
                         list = []
                         list.append(line)
                         i += 1
                         print "Number %d" %i
                         print list
                         print crawler(list)                   
                   f1.close()

              except IOError:
                   print >> sys.stderr, "Input file doesn't exist"
    else:
    	# One or more webpages specified. Seed crawl with these.
        print sys.argv[1:]
        print crawler(sys.argv[1:])


