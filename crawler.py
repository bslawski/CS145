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

def crawler(URL_seeds=["http://www.caltech.edu"]):
	#URL_seeds = ["http://www.caltech.edu"]

	MAX_ITERATIONS = 200000 # How many iterations? Finite execution, despite tons of garbage pages.
	MAX_RESULTS = 100 #20010 # How many results? Finite execution, rather than crawling entire reachable(URL_seeds)'
	URLS_FETCH = 3
	
	DOMAIN_PATTERN = '^http[s]?://([^.]+?[.])*?.?' # restrict search to this domain
	def search(x): return re.search(DOMAIN_PATTERN, x)
	def match(x): return re.match(DOMAIN_PATTERN, x)
	
	URLs_found = set(URL_seeds) # set holding pages all URLs encountered
	result = {} # dictionary holding URL + links out	
	# Using both deque (for breadth-first + efficiency) and a set (for ease of eliminating duplicates)
	queue = deque(URL_seeds) # queue holding pages to process
	queue_set = set(URL_seeds) # set holding pages in queue
	
	count = 0
	output = 1
	while (queue) and (count < MAX_ITERATIONS) and (len(result) < MAX_RESULTS):
		# Process a page
		count += 1
		#URL = queue.pop() # next page is arbitrary set element
		URL = queue.popleft() # fetch next page (FIFO -> Breath First)
		links_on_page = fetch_links('20296417')
		links_on_page = None
		if (links_on_page is not None):
			# Store results
			links_on_page = filter(search, links_on_page) # don't examine pages not matching DOMAIN_PATTERN
			links = set(links_on_page) # (set) links encountered on page
			result[URL] = len(links) # (dictionary) add page and its number of links
			
			# Add unencountered pages to queue
			#links.difference_update(URLs_found) # throw away all URLs previously encountered
			#queue_set.update(links) # add previously unencountered pages to queue
			new_pages = links.difference(queue_set, URLs_found) # throw away all URLs previously encountered
			queue_set.update(new_pages) # add pages to set
			queue.extend(new_pages) # add pages to queue
			
		# Print progress
		if (((count % output) == 0) or ((len(result) % 100) == 0)):
			output = count / output
			print "Progress: %d pages crawled. %d results found. Queue of %d" % (count, len(result), len(queue))
			
	
	# Output results
	print "\nFinished!"
	print "Found %d results, by crawling through %d pages. Queue at termination: %d" % (len(result), count, len(queue))

	# TODO: Output queue

	# Write results to CSV file
	output_file = "output.txt"
	f = open(output_file, 'a')
	URL_List = []
	try:
	    for key in result:
		URL_List.append(key)
	    	f.write(key + '\n')                            
	finally:
	    f.close()
	print "\nWrote results to file %s" % output_file	

	result_file = "result.txt"
	f = open(result_file, 'a')
	try:
	    for i in range(URLS_FETCH):
		if URL_List != []:
		    url = random.choice(URL_List)
		    f.write(url + '\n')
	finally:
	    f.close()
	print "\nWrote final results to file %s" %result_file       

#Entrance of this script, just like the "main()" function in C.

if __name__ == "__main__":
    import sys, pstats, cProfile, os.path

    if len(sys.argv)==1 or not sys.argv[1].startswith("http://"):
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

#p = pstats.Stats('crawlprof')
#p.sort_stats('time').print_stats(10)

