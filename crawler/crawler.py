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

#CACHEDIR = "htmlcache"
METADIR = "/var/www/nabber/projects/metalink/crawler/index/"

CACHETIME = 3600*24*7
PAUSETIME = 1
SKIPEXT = ["rpm", "jpg", "mpg", "iso", "gif", "png", "drpm"]

def download_metalink(url):
    filename = os.path.join(METADIR, os.path.basename(url))
    if not os.path.exists(METADIR):
        os.makedirs(METADIR)
    
    mtime = 0
    if os.access(filename, os.F_OK):
        mtime = os.stat(filename)[8]
        
    if mtime + CACHETIME > time.time():
        print filename, "already cached."
        return False
        
    try:
        urllib.urlretrieve(url, filename)
    except IOError:
        print "IOError for", filename
    
    print filename, "updated."
    time.sleep(PAUSETIME)
    return True

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
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.queue = []
        self.indexed = []
        self.url = url
        self.add(url)

    def process_html(self, text, url=''):
        parser = LinkParser(url)
        try:
            parser.feed(text)
        except HTMLParser.HTMLParseError:
            pass
        
        for link in parser.links:
            if link.endswith(".metalink") or link.endswith(".meta4"):
                download_metalink(link)
            else:
                self.add(link)

    def crawl(self, webpage):
        m = hashlib.md5()
        m.update(webpage)

        try:
            handle = urllib.urlopen(webpage)
        except:
            print "Webpage Download Error:", webpage
            return
        text = handle.read()
	self.indexed.append(handle.geturl())
        handle.close()

        time.sleep(PAUSETIME)
        
        self.process_html(text, webpage)
        return

    def add(self, page):
        if not page.startswith(os.path.dirname(self.url)):
            return
        if os.path.basename(page).startswith("?view="):
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
        
    def run(self):
        while len(self.queue) > 0:
            print "Queue len:", len(self.queue)
            page = self.queue.pop()
            self.indexed.append(page)
            print "Crawling", page
            self.crawl(page)

        
def get_version():
    return "Version 1.0" 

def run():
    parser = optparse.OptionParser(usage = "usage: %prog [options]")
    parser.add_option("--version", dest="printversion", action="store_true", help="Display the version information for this program")
    parser.add_option("-t", dest="threaded", action="store_true", help="Run each website in its own thread")
 
    (options, args) = parser.parse_args()

    if options.printversion != None:
        print get_version()
        return
        
#    if not os.path.exists(CACHEDIR):
#        os.makedirs(CACHEDIR)
        
    config = parse_config()

    if options.threaded:
        items = config.keys()        
        for key in items:
            app = App(key)
            app.start()
            #thread.start_new_thread(app.run, (),)
            time.sleep(PAUSETIME)
        return        

    items = config.keys()        
    for key in items:
        app = App(key)
        app.run()        

if __name__=="__main__":
    run()
        
