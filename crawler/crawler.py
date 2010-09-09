#!/usr/bin/env python
########################################################################
#
# Project: Metalinks
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2010, Neil McNab
# License: GNU General Public License Version 2
#   (http://www.gnu.org/copyleft/gpl.html)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# Filename: $URL: https://appupdater.svn.sourceforge.net/svnroot/appupdater/server_tools/crawler.py $
# Last Updated: $Date: 2010-01-16 18:28:50 -0800 (Sat, 16 Jan 2010) $
# Author(s): Neil McNab
#
# Description:
#   Crawls webpages looking for metalinks.
#
# TODO check for metalink header from mirrorbrain websites.
########################################################################

import urllib
import os
import ConfigParser
import optparse
import urlparse
import hashlib
import HTMLParser
import time
import threading
import robotparser

#CACHEDIR = "htmlcache"
METADIR = "/var/www/nabber/projects/metalink/crawler/index/"

CACHETIME = 3600*24*6
PAUSETIME = 1
SKIPEXT = ["magnet","rpm","jpg","mpg","iso","gif","png","drpm","img","zip",'dmg','md5','sha1','sha256','exe','txt','gz','bz2','cz','sh','pdf']

class LinkParser(HTMLParser.HTMLParser):
    def __init__(self, url):
        HTMLParser.HTMLParser.__init__(self)
        self.url = url
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    self.links.append(urlparse.urljoin(self.url, attr[1]))

def parse_config(configfile="config.ini"):
    configdict = {}
    config = ConfigParser.RawConfigParser()
    config.read(configfile)
    for sect in config.sections():
        configdict[sect] = {}
        for options in config.items(sect):
            configdict[sect][options[0]] = options[1]
    return configdict                    
                    
class App(threading.Thread):
    def __init__(self, url, debug = False, obey_robots=True, nocrawl=False):
        threading.Thread.__init__(self)
        self.queue = []
        self.indexed = []
        self.metalink_count = 0
        self.rp = None

        self.url = url
        self.debug = debug
        self.obey_robots = obey_robots
        self.nocrawl = nocrawl

        self.add(url)

    def download_metalink(self, url):
        self.metalink_count += 1
        filename = os.path.join(METADIR, os.path.basename(url))
        if not os.path.exists(METADIR):
            os.makedirs(METADIR)
    
        mtime = 0
        if os.access(filename, os.F_OK):
            mtime = os.stat(filename)[8]
        
        if mtime + CACHETIME > time.time():
            if self.debug:
                print filename, "already cached."
            return False
        
        try:
            urllib.urlretrieve(url, filename)
        except IOError:
            print "IOError for", filename
    
        if self.debug:
            print filename, "updated."
        time.sleep(PAUSETIME)
        return True

    def process_html(self, text, url=''):
        parser = LinkParser(url)
        try:
            parser.feed(text)
        except HTMLParser.HTMLParseError:
            pass
        
        for link in parser.links:
            if os.path.basename(link).startswith("?view="):
                pass
            elif link.endswith(".metalink") or link.endswith(".meta4"):
                self.download_metalink(link)
            elif not self.nocrawl:
                self.add(link)

    def crawl(self, webpage):
        m = hashlib.md5()
        m.update(webpage)

        if not self.check_robots(webpage):
            print "Crawling prohibited by robots.txt:", webpage
            return

        try:
            handle = urllib.urlopen(webpage)
        except:
            print "Webpage Download Error:", webpage
            return
        try:
            text = handle.read()
        except MemoryError:
            print "Memory Error:", webpage
            return
	self.indexed.append(handle.geturl())
        handle.close()

        time.sleep(PAUSETIME)
        
        self.process_html(text, handle.geturl())
        return

    def add(self, page):
        if not page.startswith(os.path.dirname(self.url)):
            return
        loc = page.rfind("#")
        if loc != -1:
            page = page[:page.rfind("#")]
        ext = page[page.rfind(".")+1:].lower()
        if ext in SKIPEXT:
            return
        if page in self.queue:
            return
        if page in self.indexed:
            return
        self.queue.append(page)

    def init_robots(self):
        if not self.obey_robots:
            return
        self.rp = robotparser.RobotFileParser()
        parts = urlparse.urlparse(self.url)
        self.rp.set_url(parts.scheme + '://' + parts.netloc + "/robots.txt")
        self.rp.read()

    def check_robots(self, url):
        if (not self.obey_robots) or (self.rp == None):
            return True
        return self.rp.can_fetch("*", url)

    def run(self):
        self.init_robots()
        starttime = time.time()
        while len(self.queue) > 0:
            page = self.queue.pop()
            if self.debug:
                print "Queue len:", len(self.queue), "Metalink Count:", self.metalink_count, "Run time:", int(time.time() - starttime), "seconds"
                print "Crawling", page
            self.indexed.append(page)
            self.crawl(page)

        self.runtime = time.time() - starttime

        
def get_version():
    return "Version 1.0" 

def run():
    parser = optparse.OptionParser(usage = "usage: %prog [options]")
    parser.add_option("--version", dest="printversion", action="store_true", help="Display the version information for this program")
    parser.add_option("-t", dest="threaded", action="store_true", help="Run each website in its own thread")
    parser.add_option("-d", dest="debug", action="store_true", help="Show full printout information")
    parser.add_option("-r", dest="robots", action="store_false", help="Ignore robots.txt")
    parser.add_option("-c", dest="nocrawl", action="store_true", help="Do not crawl (single page)")
 
    parser.set_defaults(robots=True, nocrawl=False)
    (options, args) = parser.parse_args()

    if options.printversion != None:
        print get_version()
        return

    nocrawl = {}
    if len(args) > 0:
        items = args
        for key in args:
            nocrawl[key] = {"crawl": options.nocrawl}
    else:
        config = parse_config()
        items = config.keys()

    apps = []

    if options.threaded:
        for key in items:
            nocrawl = False
            try:
                nocrawl = config[key]["crawl"]
            except: pass
            app = App(key, options.debug, options.robots, nocrawl)
            apps.append(app)
            app.start()
            time.sleep(PAUSETIME)
    else:
        for key in items:
            nocrawl = False
            try:
                nocrawl = config[key]["crawl"]
            except: pass
            app = App(key, options.debug, options.robots, nocrawl)
            apps.append(app)
            app.run()

    while (threading.activeCount() > 1):
        time.sleep(1)

    for app in apps:
        timepermetalink = 0
        try:
            timepermetalink = app.runtime/app.metalink_count
        except: pass
        print app.url
        print "Metalink Count:", app.metalink_count, "Runtime in minutes:", int(app.runtime/60), "Time/Metalink:", timepermetalink

    return

if __name__=="__main__":
    run()
        
