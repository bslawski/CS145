#!/usr/bin/env python
"""
A webcrawler that crawls webpages in the *.caltech.edu domain

TODO:
* Clean up (e.g. make class + fix style (line width etc.))
* Implement robots.txt adherence
* Make it a class rather than a script
* Expand w/ possibility of watching in-degree (extra credit)

"""
from fetcher import fetch_links
import re, csv
from collections import deque
import random
import time
import thread
import threading
import time


def crawler(crawlerID):

        global poolLock, nlookups, urlPool

	MAX_ITERATIONS = 200000 # How many iterations? Finite execution, despite tons of garbage pages.
	MAX_RESULTS = 15 #20010 # How many results? Finite execution, rather than crawling entire reachable(URL_seeds)'
	URLS_FETCH = 3
	
	nusers = 1
	
	count = 0
	output = 1

        # file to save structure in
        f = open('structure.' + str(threadID) + '.dat','w')

	while (queue) and (count < MAX_ITERATIONS) and (nusers < MAX_RESULTS):

                """ Changes url periodically to avoid lookup limit """
                if nlookups >= 125:
                    # makes sure no new lookups occur while url is being changed
#                    poolLock.acquire()
#                    self.changeURL()
#                    poolLock.release()

                    exit()

                while len(urlPool) == 0 :
                    print "Thread " + str(crawlerID) + " unable to retrieve user from pool." \
                          + " Pausing for 30 sec.\n"
                    time.sleep(30)

                poolLock.acquire()
		user = urlPool.popleft() # fetch next page (FIFO -> Breath First)
                poolLock.release()
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
                        if len(queue) < 200000:
                            poolLock.acquire()
       			    urlPool.extend(new_pages) # add pages to queue	
                            poolLock.release()
        
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


""" TODO: implement this function """
#def changeURL() :


# Entrance of the script

if __name__ == "__main__":
    import sys, pstats, cProfile, os.path

    usage = """

USAGE: crawler <int seedID> <int nThreads>
       seedID must be a valid Twitter ID number
       nThreads must be positive

"""

    urlPool = []

    if not len(sys.argv[1:]) == 2 :
        print usage
        exit()

    try:
        seedID = int(sys.argv[1])
        nThreads = int(sys.argv[2])
    except ValueError:
        print usage
        exit()

    # Tests the seedID
    followers = fetch_links(seedID)
    if followers == None:
        print usage
        print "Unable to open seedID.  Twitter may be busy.\n\n"
        exit()

    poolLock = thread.allocate_lock()

    nlookups = 1
    activeThreads = 0

    for id in range(0,nThreads):
        activeThreads += 1
        thread.start_new_thread(crawler, (id))


