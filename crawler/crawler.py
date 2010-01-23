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
import difflib
import os
import ConfigParser
import optparse
import urlparse
import hashlib
import HTMLParser
import time

CACHEDIR = "htmlcache"
METADIR = "cache"

CACHETIME = 3600*24*7
PAUSETIME = 1

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
                    
class App:
    def __init__(self):
        self.queue = []
        self.indexed = []

    def process_html(self, filename, url=''):
        handle = open(filename)
        text = handle.read()
        handle.close()
        parser = LinkParser(url)
        try:
            parser.feed(text)
        except:
            pass
        
        for link in parser.links:
            if link.endswith(".metalink") or link.endswith(".meta4"):
                download_metalink(link)
            elif (link.startswith(os.path.dirname(url))):
                self.add(link)

    def crawl(self, webpage):
        m = hashlib.md5()
        m.update(webpage)

        filename = os.path.join(CACHEDIR, m.hexdigest() + ".html")
        try:
            handle = urllib.urlopen(webpage)
        except:
            print "Webpage Download Error:", webpage
            return
        text = handle.read()
        handle.close()

        handle = open(filename, "w")
        handle.write(text)
        handle.close()
        time.sleep(PAUSETIME)
        
        self.process_html(filename, webpage)
        return

    def add(self, page):
        if (page not in self.queue) and (page not in self.indexed):
            self.queue.append(page)
        
    def run(self):
        while len(self.queue) > 0:
            print "Queue len:", len(self.queue)
            page = self.queue.pop()
            print "Crawling", page
            self.crawl(page)
            self.indexed.append(page)

        
def get_version():
    return "Version 1.0" 

def run():
    parser = optparse.OptionParser(usage = "usage: %prog [options]")
    parser.add_option("--version", dest="printversion", action="store_true", help="Display the version information for this program")
 
    (options, args) = parser.parse_args()

    if options.printversion != None:
        print get_version()
        return
        
    if not os.path.exists(CACHEDIR):
        os.makedirs(CACHEDIR)
        
    app = App()

    config = parse_config()

    items = config.keys()
        
    for key in items:
        app.add(key)
        
    app.run()        

if __name__=="__main__":
    run()
        