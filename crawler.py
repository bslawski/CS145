#!/usr/bin/env python
"""
A webcrawler that crawls Twitter using follower lists
"""
from fetcher import fetch_links
import re, csv
from collections import deque
import random
import time
import thread
import threading
import time
import os

def crawlerRun(threadID, sleeptime):

        global poolLock, nlookups, urlPool, urlFound, nusers, activeThreads

        print "Thread: " + str(threadID) + " started"
        sys.stdout.flush()

	MAX_RESULTS = 20 #20010 # How many results? Finite execution, rather than crawling entire reachable(URL_seeds)'
	URLS_FETCH = 3
	
	output = 10

        # file to save structure in
        try :
            f = open('structure.' + str(threadID) + '.dat','w')
        except IOError :
            print "Unable to open " + "structure." + str(threadID) + \
                  ".dat for writing.  Thread " + str(threadID) + "exiting."
            sys.stdout.flush()
            exit()


	while nusers < MAX_RESULTS:

                """ Changes url periodically to avoid lookup limit """
                if nlookups >= 125:

                    print "MAX LOOKUPS REACHED!"
                    sys.stdout.flush()
                    # makes sure no new lookups occur while url is being changed
#                    poolLock.acquire()
#                    self.changeURL()
#                    poolLock.release()

                    exit()

                while len(urlPool) == 0 :
                    print "\t\t\t\tThread " + str(threadID) + " unable to retrieve user from pool." \
                          + " Pausing for " + str(sleeptime) + " sec."
                    sys.stdout.flush()
                    time.sleep(30)

                poolLock.acquire()
		user = urlPool.pop(0) # fetch next page (FIFO -> Breath First)
                poolLock.release()
		nusers += 1
                followers = fetch_links(user)
                nlookups += 1

                if followers == None :
                    poolLock.acquire()
                    urlPool.append(user)
                    poolLock.release()
                    nusers -= 1
                    print '\t\t\t\tProfile ' + str(user) + ' is busy.  Absorbing back into pool.'
                    sys.stdout.flush()
                    continue

                urlFound.append(user)

		if (not (followers == None) and len(followers) > 0 and not (followers[0] == '')):
                        new_pages = []
			# Add unencountered pages to queue
                        for ids in followers :
                            if not (ids in urlPool or ids in urlFound) :
                                new_pages.append(ids)

                        writeUser(f, user, followers)
                        if len(urlPool) < 200000:
                            poolLock.acquire()
       			    urlPool.extend(new_pages) # add pages to queue	
                            poolLock.release()
        
		# Print progress
		if ((nusers % output) == 0 and nusers < MAX_RESULTS):
			print "Progress: %d pages crawled.  %d users in pool." % (nusers, len(urlPool))
			sys.stdout.flush()

	f.close()

	# Output results
	print "Thread " + str(threadID) + " Finished!"
        sys.stdout.flush()
        activeThreads -= 1


def writeUser(writefile, user, followers) :
    writefile.write(user + ':')
    for fol_id in followers :
        writefile.write(' ' + fol_id)
    writefile.write('\n')    


def concatFiles(nfiles) :
    print "Writing data file..."

    count = 0

    try:
        outfile = open('structure.dat', 'w')
    except IOError:
        print "Unable to open structure.dat for writing."
        exit()

    for id in range(0,nfiles):
        try:
            tempfile = open('structure.' + str(id) + '.dat', 'r')
        except IOError:
            print "Unable to open structure." + str(id) + ".dat for reading."

        for line in tempfile:
            outfile.write(line)
            count += 1
        tempfile.close()
        os.remove('structure.' + str(id) + '.dat')

    outfile.close()
    print "Data file written.  Structure contains " + str(count) + " nodes."


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
    urlFound = []

    if not len(sys.argv[1:]) == 2 :
        print usage
        exit()

    try:
        seedID = sys.argv[1]
        nThreads = int(sys.argv[2])
    except ValueError:
        print usage
        exit()

    # Tests the seedID
    print "Beginning crawl at user ID " + seedID
    followers = fetch_links(seedID)
    if followers == None:
        print usage
        print "Unable to open seedID.  Twitter may be busy.\n\n"
        exit()

    urlPool.extend(followers)

    poolLock = thread.allocate_lock()

    nlookups = 1
    nusers = 1
    activeThreads = 0

    for id in range(0,nThreads):
        activeThreads += 1
        thread.start_new_thread(crawlerRun, (id, 30))

    while activeThreads > 0:
        pass

    concatFiles(nThreads)

    print "Crawl Finished!  Results in structure.dat"
