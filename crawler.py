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
import httplib

def crawlerRun(threadID, sleeptime):

        global poolLock, urlPool, urlFound, activeThreads, poolOpen, proxyLock, proxyInd, proxyList, poolLen, foundLen

#        print "Thread " + str(threadID) + " Started"
        sys.stdout.flush()

	MAX_RESULTS = 100000 #20010 # How many results? Finite execution, rather than crawling entire reachable(URL_seeds)'
        POOL_LIMIT = 100000
	
	output = 10

        # file to save structure in
        try :
            f = open('structure.' + str(threadID) + '.dat','w')
        except IOError :
            print "Unable to open " + "structure." + str(threadID) + \
                  ".dat for writing.  Thread " + str(threadID) + "exiting."
            sys.stdout.flush()
            exit()

        nlookups = 150
        myLink = None

	while foundLen < MAX_RESULTS:

                """ Changes url periodically to avoid lookup limit """
                if nlookups >= 20:

#                    print "\t\t\t\tThread " + str(threadID) + " aquiring new proxy."
                    sys.stdout.flush()
                    proxyLock.acquire()
                    myLink = changeURL()
                    nlookups = 0
                    myIP = myLink[0]
                    myPort = myLink[1]
                    proxyLock.release()
#                    print "\t\t\t\tUsing " + myIP + ":" + str(myPort)

                while poolLen == 0 :
#                    print "\t\t\t\tThread " + str(threadID) + " unable to retrieve user from pool." \
#                          + " Pausing for " + str(sleeptime) + " sec."
#                    sys.stdout.flush()
                    time.sleep(sleeptime)
                    poolLen = len(urlPool)

                poolLock.acquire()
                if poolLen > 0:
                    user = urlPool.pop(0) # fetch next page (FIFO -> Breath First)
                else:
                    continue
                poolLock.release()
                followers = fetch_links(user, myIP, myPort)
                nlookups += 1

                if followers == None :
                    poolLock.acquire()
                    urlPool.insert(0, user)
                    poolLock.release()
                    proxyLock.acquire()
                    myLink = changeURL()
                    proxyLock.release()
#                    print '\t\t\t\tProfile ' + str(user) + ' is busy.  Absorbing back into pool.'
                    sys.stdout.flush()
                    continue

                try:
                    int(followers[0])
                except ValueError:
                    poolLock.acquire()
                    urlPool.append(user)
                    poolLock.release()
#                    print followers
                    proxyLock.acquire()
                    myLink = changeURL()
                    proxyLock.release()
                    continue 

                urlFound.append(user)
                foundLen += 1

		if (not (followers == None) and len(followers) > 0 and not (followers[0] == '')):
                        new_pages = []
			# Add unencountered pages to queue
                        for ids in followers :
                            if not (ids in urlPool or ids in urlFound) :
                                new_pages.append(ids)

                        writeUser(f, user, followers)
                        if poolOpen:
                            poolLock.acquire()
       			    urlPool.extend(new_pages) # add pages to queue	
                            poolLock.release()
        
#                foundLen = len(urlFound)

		# Print progress
		if ((foundLen % output) == 0 and foundLen < MAX_RESULTS):
                    poolLen = len(urlPool)
                    print "Progress: %d pages crawled.  %d users in pool." % (foundLen, poolLen)
                    sys.stdout.flush()

                # Closes url pool if max size is reached.  Prevents slow-down of crawl
                if poolOpen : poolLen = len(urlPool)
                if poolLen > POOL_LIMIT and poolOpen:
                    print "\t\t\t\tMax URL Pool size reached! Closing Pool..."
                    sys.stdout.flush()
                    poolOpen = False

	f.close()

	# Output results
	print "Thread " + str(threadID) + " Finished! " + \
              str(activeThreads - 1) + " Threads Running."
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

    for id in range(0, nfiles + 1):
        try:
            tempfile = open('structure.' + str(id) + '.dat', 'r')
        except IOError:
            print "Unable to open structure." + str(id) + ".dat for reading."

        for line in tempfile:
            outfile.write(line)
            count += 1
        tempfile.close()
#        os.remove('structure.' + str(id) + '.dat')

    outfile.close()
    print "Data file written.  Structure contains " + str(count) + " nodes."


def changeURL() :
    global proxyInd, proxyList, proxyFile
#    print "using IP number " + str(proxyInd)
    newIP = proxyList[0][proxyInd]
    newPort = proxyList[1][proxyInd]
    proxyInd += 1
    if proxyInd == len(proxyList[0]):
        print "\tswitching proxy list..."
        proxyFile = (proxyFile + 1) % 2
        readProxyList(proxyFile)

    return [newIP, newPort]


def readProxyList(proxyFile) :
    global proxyInd
    try:
        f = open('proxy_list' + str(proxyFile) + '.txt')
    except IOError:
        print "Proxy file not found!"
        exit()

    proxyIP = []
    proxyPort = []

    for line in f:
        proxyLine = line.split()
        proxyIP.append(proxyLine[0])
        proxyPort.append(int(proxyLine[1]))

    print "\tUsing proxy list " + str(proxyFile)
    proxyInd = 0
    return [proxyIP, proxyPort]


# Entrance of the script

if __name__ == "__main__":
    import sys, pstats, cProfile, os.path

    startTime = time.time()

    usage = """

USAGE: crawler <int seedID> <int nThreads>
       seedID must be a valid Twitter ID number
       nThreads must be positive

"""

    proxyFile = 0
    proxyList = readProxyList(proxyFile)

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
    followers = fetch_links(seedID, proxyList[0][0], proxyList[1][0])
#    print followers
    if followers == None:
        print usage
        print "Unable to open seedID.  Twitter may be busy.\n\n"
        exit()


    try :
        f = open('structure.' + str(nThreads) + '.dat','w')
        writeUser(f, seedID, followers)
        f.close()
    except IOError :
        print "Unable to open " + "structure." + str(nThreads) + \
              ".dat for writing.  Crawler exiting."
        sys.stdout.flush()
        exit()


    urlPool.extend(followers)

    poolLock = thread.allocate_lock()
    proxyLock = thread.allocate_lock()

    proxyInd = 0
    activeThreads = 0
    poolOpen = True

#    print followers

    nfollowers = len(followers)
    poolLen = nfollowers
    foundLen = 1
    if nfollowers < nThreads:

        for threadID in range(0, nfollowers):
            print "Thread " + str(threadID) + " Started"
            activeThreads += 1
            thread.start_new_thread(crawlerRun, (threadID, 15))

        while len(urlPool) < nThreads - nfollowers:
            pass

        for threadID in range(nfollowers,nThreads):
            print "Thread " + str(threadID) + " Started"
            activeThreads += 1
            thread.start_new_thread(crawlerRun, (threadID, 15))

    else:
        for threadID in range(0,nThreads):
            print "Thread " + str(threadID) + " Started"
            activeThreads += 1
            thread.start_new_thread(crawlerRun, (threadID, 15))


    while activeThreads > 0:
        pass

    concatFiles(nThreads)

    crawlTime = time.time() - startTime
    crawlSec = int(crawlTime % 60)
    crawlMin = int((crawlTime % 3600) / 60)
    crawlHour = int(crawlTime / 3600)
    print "Crawl Time:  " + str(crawlHour) + " Hours  " \
          + str(crawlMin) + " Min  " + str(crawlSec) + " Sec"

    print "Crawl Finished!  Results in structure.dat"
