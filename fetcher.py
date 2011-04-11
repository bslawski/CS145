#!/usr/bin/env python
"""
A simple program to extract links in a web page, by Minghong Lin, for CS/EE144.
If you use Python, you can import this file and simply call the function
"fetch_links(URL)" to get a list (may be empty) which contains all hyperlinks
in the web page specified by the URL. It returns None if the URL is not a valid
HTML page or some error occurred.
If you use other programming language, you can make a system call to execute this
file and pipe the output to your program. The command is
"python fetcher.py http://..."
The output is a list (may be empty "[]") of hyperlinks which looks like:
"['http://today.caltech.edu', 'http://www.caltech.edu/copyright/']"
The output is "None" if the URL is not a valid HTML page or some error occurred.
"""
#A simple HTML parser named SGMLParser is in the standard Python module sgmllib.
#urljoin is used to combine a base URL and a relative URL to an absolute URL.
#We would use urllib2 to retrieve the webpage.
from sgmllib import SGMLParser
from urlparse import urljoin
import urllib
import urllib2

#SGMLParser is like a template for implementing a HTML parser. All its methods
#for handling HTML tags are "do-nothing" methods. We have to inherit from it
#and override some methods in order to extract the hyperlinks.
class URLLister(SGMLParser):
    
    #Reset the parser by calling this method.
    def reset(self):
        SGMLParser.reset(self)
        self.urls = []

    #Just to simplify the methods start_a/do_area/start_frame/start_iframe.
    def _extract_url(self,attrs,keyword):
        href = [v for (k, v) in attrs if k==keyword]
        if href:
            self.urls.extend(href)

    #start_TAG() and do_TAG() are called by SGMLParser whenever it finds a TAG.
    #"<a> ... </a>" tag may contain an "href" attribute which is a hyperlink.
    def start_a(self, attrs):
        self._extract_url(attrs,'href')

    #"<area ...>" tag may contain an "href" attribute which is a hyperlink.            
    def do_area(self, attrs):
        self._extract_url(attrs,'href')

    #"<frame ...>" tag may contain an "src" attribute which is a hyperlink.            
    def do_frame(self, attrs):
        self._extract_url(attrs,'src')

    #"<iframe ...>" tag may contain an "src" attribute which is a hyperlink.            
    def do_iframe(self, attrs):
        self._extract_url(attrs,'src')

    #Refine the hyperlinks: ignore the parameters in dynamic URL, converting
    #all hyperlinks to absolute URLs, remove duplicated URLs.
    def get_links(self,current_url):
        res=set()       #Use datastructure "set" to avoid duplicated URLs.
        for url in self.urls:
            url=url.split('?')[0]   #Extract the part before '?' if any.
            url=url.split('#')[0]   #Extract the part before '#' if any.
            url=urljoin(current_url,url.strip())   #Convert to absolute URL.
            if url.startswith("http://") or url.startswith("https://"):
                res.add(url)
        res.discard(current_url)   #Self-link is removed
        return list(res)

#Fetch an HTML file, return the real (redirected) URL and the content.
def fetch_html_page(url):
    content=None
    real_url=url
    try:
        urllib2.socket.setdefaulttimeout(10)  #Bad page, timeout in 10s.
        usock = urllib2.urlopen(url)
        real_url=usock.url  #real_url will be changed if there is a redirection. 
        if "text/html" in usock.info()['content-type']:
            content=usock.read()    #Fetch it if it is html but not mp3/avi/...
        usock.close()
    except:
        pass
    return (real_url, content)

#Fetch the hyperlinks. First fetch the content then use URLLister to parse them.
#def fetch_links(url):
#    links=None
#    try:
#        parser = URLLister()
#        ru,s=fetch_html_page(url)
#        if s is not None:
#            parser.feed(s)
#            parser.close()
#            links=parser.get_links(ru)
#    except:
#        pass
#    return links

def fetch_links(userid):
    new_ids=None
    try:
        sock = urllib.urlopen('http://api.twitter.com/1/followers/ids.json' \
                            + '?user_id=' + userid)
        json_file = sock.read()
        new_ids = json_file.rsplit(',')
    except:
        print 'Unable to read follower list of user ' + userid
    print new_ids
    return new_ids
        


#Entrance of this script, just like the "main()" function in C.
if __name__ == "__main__":
    import sys
    if len(sys.argv)!=2 or not sys.argv[1].startswith("http://"):

        pn=sys.argv[0]
        i=max(pn.rfind("\\"),pn.rfind("/"))+1
        print "usage: %s http://...\tShow all hyperlinks in an HTML page."%pn[i:]
    else:
        print fetch_links(sys.argv[1])
