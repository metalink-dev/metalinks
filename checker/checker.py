#!/usr/bin/env python
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2008, Neil McNab
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
# Filename: $URL: https://metalinks.svn.sourceforge.net/svnroot/metalinks/checker/metalink.py $
# Last Updated: $Date: 2008-03-24 00:31:39 -0700 (Mon, 24 Mar 2008) $
# Version: $Rev: 130 $
# Author(s): Neil McNab
#
# Description:
#   Command line application and Python library that checks or downloads
# metalink files.  Requires Python 2.5 or newer.
#
# Instructions:
#   1. You need to have Python installed.
#   2. Run on the command line using: python metalink.py
#
#   Usage: metalink.py [options]
#
#   Options:
#     -h, --help            show this help message and exit
#     -d, --download        Actually download the file(s) in the metalink
#     -f FILE, --file=FILE  Metalink file to check
#     -t TIMEOUT, --timeout=TIMEOUT
#                           Set timeout in seconds to wait for response
#                           (default=10)
#     -o OS, --os=OS        Operating System preference
#     -l LANG, --lang=LANG  Language preference (ISO-639/3166)
#     -c LOC, --country=LOC
#                           Two letter country preference (ISO 3166-1 alpha-2)
#
# Library Instructions:
#   - Use as expected.
#
# import metalink
#
# files = metalink.get("file.metalink", os.getcwd())
# results = metalink.check_metalink("file.metalink")
#
# CHANGELOG:
# Version 3.6
# -----------
# - Support for resuming segmented downloads
# - Modified for better Python 2.4 support
#
# Version 3.5
# -----------
# - Code cleanup
# - FTP close connection speed improvement
# - Added documentation for how to use as a library
# - Sort by country pref first (if set), then pref value in metalink
# 
# Version 3.4
# -----------
# - segmented download FTP size support
# - support for user specified OS and language preferences
# - finished FTP proxy support
#
# Version 3.3
# -----------
# - Bugfix for when type attr not present
# - Support for FTP segmented downloads
#
# Version 3.2
# -----------
# - If type="dynamic", client checks origin location
#
# Version 3.1
# -----------
# - Now handles all SHA hash types and MD5
# - Minor bug fixes
#
# Version 3.0
# -----------
# - Speed and bandwidth improvements for checking mode
# - Added checking of chunk checksums
# - If chunk checksums are present, downloads are resumed
# - Proxy support (experimental, HTTP should work, FTP and HTTPS not likely)
#
# Version 2.0.1
# -------------
# - Bugfix when doing size check on HTTP servers, more reliable now
#
# Version 2.0
# -----------
# - Support for segmented downloads! (HTTP urls only, falls back to old method if only FTP urls)
#
# Version 1.4
# -----------
# - Added support for checking the file size on FTP servers
#
# Version 1.3.1
# -------------
# - Made error when XML parse fails a little clearer.
#
# Version 1.3
# -----------
# - Fixed bug when no "size" attribute is present
#
# Version 1.2
# -----------
# - Added totals output
#
# Version 1.1
# -----------
# - Bugfixes for FTP handling, bad URL handling
# - rsync doesn't list as a URL Error
# - reduced timeout value
#
# Version 1.0
# -----------
# This is the initial release.
#
# TODO
# - Pass test for bad piece checksum (don't hang)
# - resume download support for non-segmented downloads
# - download priority based on speed
# - use maxconnections
# - dump FTP data chunks directly to file instead of holding in memory
# - maybe HTTPS proxy support if people need it
########################################################################

import optparse
import urllib2
import urlparse
import os.path
import xml.dom.minidom
import random
import sys
import httplib
import re
import socket
import ftplib
import threading
import time
import base64
import copy
import hashlib

import download
import xmlutils

SEGMENTED = True
LIMIT_PER_HOST = 1
HOST_LIMIT = 5
MAX_REDIRECTS = 20
CONNECT_RETRY_COUNT = 3

LANG = None
OS = None
COUNTRY = None

# Configure proxies (user and password optional)
# HTTP_PROXY = http://user:password@myproxy:port
HTTP_PROXY=""
FTP_PROXY=""
HTTPS_PROXY=""

# Protocols to use for segmented downloads
PROTOCOLS=("http","https","ftp")
#PROTOCOLS=("ftp")

# DO NOT CHANGE
VERSION="Metalink Checker Version 3.6"

def run():
    '''
    Start a console version of this application.
    '''
    # Command line parser options.
    parser = optparse.OptionParser(version=VERSION)
    parser.add_option("--download", "-d", action="store_true", dest="download", help="Actually download the file(s) in the metalink")
    parser.add_option("--file", "-f", dest="filevar", metavar="FILE", help="Metalink file to check")
    parser.add_option("--timeout", "-t", dest="timeout", metavar="TIMEOUT", help="Set timeout in seconds to wait for response (default=10)")
    parser.add_option("--os", "-o", dest="os", metavar="OS", help="Operating System preference")
    parser.add_option("--lang", "-l", dest="language", metavar="LANG", help="Language preference (ISO-639/3166)")
    parser.add_option("--country", "-c", dest="country", metavar="LOC", help="Two letter country preference (ISO 3166-1 alpha-2)")
    
    (options, args) = parser.parse_args()

    if options.filevar == None:
        parser.print_help()
        return

    socket.setdefaulttimeout(10)
    set_proxies()
    if options.timeout != None:
        socket.setdefaulttimeout(int(options.timeout))

    if options.country != None and len(options.country) != 2:
        print "Invalid country length, must be 2 letter code"
        return

    global LANG
    global OS
    global COUNTRY
    LANG = options.language
    OS = options.os
    COUNTRY = options.country
    
    if options.download:
        progress = ProgressBar(55)
        download_metalink(options.filevar, os.getcwd(), handler=progress.download_update)
        progress.download_end()
    else:
        results = check_metalink(options.filevar)
        print_totals(results)

def set_proxies():
    # Set proxies
    proxies = {}
    if HTTP_PROXY != "":
        proxies['http'] = HTTP_PROXY
    if HTTPS_PROXY != "":
        proxies['https'] = HTTPS_PROXY
    if FTP_PROXY != "":
        proxies['ftp'] = FTP_PROXY
        
    proxy_handler = urllib2.ProxyHandler(proxies)
    opener = urllib2.build_opener(proxy_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler, urllib2.HTTPSHandler, urllib2.FTPHandler)
    # install this opener
    urllib2.install_opener(opener)

def print_totals(results):
    for key in results.keys():
        print "=" * 79
        print "Summary for:", key

        status_count = 0
        size_count = 0
        error_count = 0
        total = len(results[key])
        for subkey in results[key].keys():
            status = results[key][subkey][0]
            status_bool = False
            if status != "OK" and status != "?":
                status_bool = True

            size = results[key][subkey][1]
            size_bool = False
            if size == "FAIL":
                size_bool = True

            if size_bool:
                size_count += 1
            if status_bool:
                status_count += 1
            if size_bool or status_bool:
                error_count += 1

        print "Download errors: %s/%s" % (status_count, total)
        print "Size check failures: %s/%s" % (size_count, total)
        print "Overall failures: %s/%s" % (error_count, total)

##def print_summary(results):
##    for key in results.keys():
##        print "=" * 79
##        print "Summary for:", key
##        print "-" * 79
##        print "Response Code\tSize Check\tURL"
##        print "-" * 79
##        for subkey in results[key].keys():
##            print "%s\t\t%s\t\t%s" % (results[key][subkey][0], results[key][subkey][1], subkey)

##def confirm_prompt(noprompt):
##    invalue = "invalid"
##
##    if noprompt:
##        return True
##    
##    while (invalue != "" and invalue[0] != "n" and invalue[0] != "N" and invalue[0] != "Y" and invalue[0] != "y"):
##        invalue = raw_input("Do you want to continue? [Y/n] ")
##
##    try:
##        if invalue[0] == "n" or invalue[0] == "N":
##            return False
##    except IndexError:
##        pass
##    
##    return True

################ checks ############################

def check_metalink(src):
    '''
    Decode a metalink file, can be local or remote
    First parameter, file to download, URL or file path to download from
    Returns the results of the check in a dictonary
    '''
    src = download.complete_url(src)
    datasource = urllib2.urlopen(src)
    try:
        dom2 = xml.dom.minidom.parse(datasource)   # parse an open file
    except:
        print "ERROR parsing XML."
        raise
    datasource.close()
    
    metalink_node = xmlutils.get_subnodes(dom2, ["metalink"])
    try:
        metalink_type = get_attr_from_item(metalink_node, "type")
    except:
        metalink_type = None
    if metalink_type == "dynamic":
        origin = get_attr_from_item(metalink_node, "origin")
        if origin != src:
            return check_metalink(origin)
    
    urllist = xmlutils.get_subnodes(dom2, ["metalink", "files", "file"])
    if len(urllist) == 0:
        print "No urls to download file from."
        return False

    results = {}
    for filenode in urllist:
        try:
            size = xmlutils.get_xml_tag_strings(filenode, ["size"])[0]
        except:
            size = None
        name = xmlutils.get_attr_from_item(filenode, "name")
        print "=" * 79
        print "File: %s Size: %s" % (name, size)
        results[name] = check_file_node(filenode)

    return results

def check_process(headers, filesize):
    size = "?"
    
    sizeheader = get_header(headers, "Content-Length")

    if sizeheader != None and filesize != None:
        if sizeheader == filesize:
            size = "OK"
        else:
            size = "FAIL"

    response_code = "OK"
    temp_code = get_header(headers, "Response")
    if temp_code != None:
        response_code = temp_code
        
    return (response_code, size)

def get_header(textheaders, name):
    textheaders = str(textheaders)
    
    headers = textheaders.split("\n")
    for line in headers:
        line = line.strip()
        result = line.split(": ")
        if result[0].lower() == name.lower():
            return result[1]

    return None

def check_file_node(item):
    '''
    Downloads a specific version of a program
    First parameter, file XML node
    Second parameter, file path to save to
    Third parameter, optional, force a new download even if a valid copy already exists
    Fouth parameter, optional, progress handler callback
    Returns dictionary of file paths with headers
    '''
    try:
        size = get_xml_tag_strings(item, ["size"])[0]
    except:
        size = None
    urllist = xmlutils.get_subnodes(item, ["resources", "url"])
    if len(urllist) == 0:
        print "No urls to download file from."
        return False
            
    number = 0
    filename = {}

    count = 1
    result = {}
    while (count <= len(urllist)):
        filename = urllist[number].firstChild.nodeValue.strip()
        print "-" *79
        print "Checking: %s" % filename
        checker = URLCheck(filename)
        headers = checker.info()
        result[checker.geturl()] = check_process(headers, size)
        print "Response Code: %s\tSize Check: %s" % (result[checker.geturl()][0], result[checker.geturl()][1])   
        number = (number + 1) % len(urllist)
        count += 1
        
    return result
       
class URLCheck:    
    def __init__(self, url):
        self.infostring = ""
        self.url = url
        urlparts = urlparse.urlparse(url)
        self.scheme = urlparts.scheme
        
        if self.scheme == "http":
            # need to set default port here
            port = httplib.HTTP_PORT
            try:
                if urlparts.port != None:
                    port = urlparts.port
            except ValueError:
                self.infostring += "Response: Bad URL\r\n"
                return
    
            conn = HTTPConnection(urlparts.hostname, port)
            try:
                conn.request("HEAD", url)
            except socket.error, error:
                self.infostring += "Response: Connection Error\r\n"
                return
                
            resp = conn.getresponse()
            
            # handle redirects here and set self.url
            count = 0
            while (resp.status == httplib.MOVED_PERMANENTLY or resp.status == httplib.FOUND) and count < MAX_REDIRECTS:
                url = resp.getheader("location")
                print "Redirected: %s" % url
                conn.close()
                urlparts = urlparse.urlparse(url)
                # need to set default port here
                port = httplib.HTTP_PORT
                if urlparts.port != None:
                    port = urlparts.port
                
                conn = HTTPConnection(urlparts.hostname, urlparts.port)
                conn.request("HEAD", url)
                resp = conn.getresponse()
                count += 1

            self.url = url
            if resp.status == httplib.OK:
                self.infostring += "Response: OK\r\n"
            else:
                self.infostring += "Response: %s %s\r\n" % (resp.status, resp.reason)
            
            # need to convert list into string
            for header in resp.getheaders():
                self.infostring += header[0] + ": " + header[1] + "\r\n"

            conn.close()
                
        elif self.scheme == "https":
            # need to set default port here
            port = httplib.HTTPS_PORT
            try:
                if urlparts.port != None:
                    port = urlparts.port
            except ValueError:
                self.infostring += "Response: Bad URL\r\n"
                return
    
            conn = HTTPSConnection(urlparts.hostname, port)
            try:
                conn.request("HEAD", url)
            except socket.error, error:
                #dir(error)
                self.infostring += "Response: Connection Error\r\n"
                return
                
            resp = conn.getresponse()
            
            # handle redirects here and set self.url
            count = 0
            while (resp.status == httplib.MOVED_PERMANENTLY or resp.status == httplib.FOUND) and count < MAX_REDIRECTS:
                url = resp.getheader("location")
                print "Redirected: %s" % url
                conn.close()
                urlparts = urlparse.urlparse(url)
                # need to set default port here
                port = httplib.HTTPS_PORT
                if urlparts.port != None:
                    port = urlparts.port
                
                conn = HTTPSConnection(urlparts.hostname, urlparts.port)
                conn.request("HEAD", url)
                resp = conn.getresponse()
                count += 1

            self.url = url
            if resp.status == httplib.OK:
                self.infostring += "Response: OK\r\n"
            else:
                self.infostring += "Response: %s %s\r\n" % (resp.status, resp.reason)
            
            # need to convert list into string
            for header in resp.getheaders():
                self.infostring += header[0] + ": " + header[1] + "\r\n"

            conn.close()
                
        elif self.scheme == "ftp":
            try:
                username = urlparts.username
                password = urlparts.password
            except AttributeError:
                # needed for python < 2.5
                username = None

            if username == None:
                username = "anonymous"
                password = "anonymous"

            ftpobj = FTP()
            try:
                ftpobj.connect(urlparts[1])
            except socket.gaierror:
                self.infostring += "Response: Bad Hostname\r\n"
                return
            except socket.timeout:
                self.infostring += "Response: timed out\r\n"
                return

            try:
                ftpobj.login(username, password)
            except (ftplib.error_perm), error:
                self.infostring += "Response: %s\r\n" % error.message
                
            if ftpobj.exist(url):
                self.infostring += "Response: OK\r\n"
            else:
                self.infostring += "Response: Not Found\r\n"
                
            try:
                size = ftpobj.size(url)
            except:
                size = None
                
            try:
                ftpobj.quit()
            except: pass
            
            if size != None:
                self.infostring += "Content-Length: %s\r\n" % size   

        else:
            self.infostring += "Response: ?\r\n"
            
    def geturl(self):
        return self.url

    def info(self):
        # need response and content-length for HTTP
        return self.infostring
            

#########################################


########### PROXYING OBJECTS ########################

class FTP:
    def __init__(self, host=None, user="", passwd="", acct=""):
        self.conn = None
        self.headers = {}
        if host != None:
            self.connect(host)
        if user != "":
            self.login(user, passwd, acct)

    def connect(self, host, port=ftplib.FTP_PORT):
        if FTP_PROXY != "":
            # parse proxy URL
            url = urlparse.urlparse(FTP_PROXY)
            if url[0] == "" or url[0] == "http":
                port = httplib.HTTP_PORT
                if url[1].find("@") != -1:
                    host = url[1].split("@", 2)[1]
                else:
                    host = url[1]
                    
                try:
                    if url.port != None:
                        port = url.port
                    if url.username != None:
                        self.headers["Proxy-authorization"] = "Basic " + base64.encodestring(url.username+':'+url.password) + "\r\n"
                except AttributeError:
                    pass
                self.conn = httplib.HTTPConnection(host, port)
            else:
                raise AssertionError, "Transport %s not supported for FTP_PROXY" % url.scheme

        else:
            self.conn = ftplib.FTP()
            self.conn.connect(host, port)

    def login(self, *args):
        if FTP_PROXY == "":
            return self.conn.login(*args)

    def size(self, url):
        if FTP_PROXY != "":
            result = self.conn.request("HEAD", url)
            return int(result.getheader("Content-length", None))
        else:
            urlparts = urlparse.urlsplit(url)
            size = self.conn.size(urlparts.path)
            return size

    def exist(self, url):
        if FTP_PROXY != "":
            result = self.conn.request("HEAD", url)
            if result.status < 400:
                return True
            return False
        else:
            urlparts = urlparse.urlsplit(url)
            try:
                files = self.conn.nlst(os.path.dirname(urlparts.path))
            except:
                return False

            # directory listing can be in two formats, full path or current directory
            if (os.path.basename(urlparts.path) in files) or (urlparts.path in files):
                return True

            return False

    def ntransfercmd(self, cmd, rest=0, rest_end=None):
        if FTP_PROXY != "":
            if cmd.startswith("RETR"):
                url = cmd.split(" ", 2)
                size = self.size(url)
                if rest_end == None:
                    rest_end = size
                result = self.conn.request("GET", url, "", {"Range": "bytes=%lu-%lu\r\n" % (rest, rest_end)})
                result.recv = result.read
                return (result, size)
            return (None, None)
        else:
            return self.conn.ntransfercmd(cmd, rest)

    def voidcmd(self, *args):
        return self.conn.voidcmd(*args)

    def quit(self):
        if FTP_PROXY != "":
            return self.conn.close()
        else:
            return self.conn.quit()

class HTTPConnection:
    def __init__(self, host, port=httplib.HTTP_PORT):
        self.headers = {}
        
        if HTTP_PROXY != "":
            # parse proxy URL
            url = urlparse.urlparse(HTTP_PROXY)
            if url.scheme == "" or url.scheme == "http":
                host = url.hostname
                port = url.port
                if url.username != None:
                    self.headers["Proxy-authorization"] = "Basic " + base64.encodestring(url.username+':'+url.password) + "\r\n"
            else:
                raise AssertionError, "Transport %s not supported for HTTP_PROXY" % url.scheme

        self.conn = httplib.HTTPConnection(host, port)

    def request(self, method, url, body="", headers={}):
        headers.update(self.headers)
        if HTTP_PROXY == "":
            urlparts = urlparse.urlsplit(url)
            url = urlparts.path + "?" + urlparts.query
        return self.conn.request(method, url, body, headers)

    def getresponse(self):
        return self.conn.getresponse()

    def close(self):
        self.conn.close()

class HTTPSConnection:
    ######## still very broken for proxy!
    def __init__(self, host, port=httplib.HTTPS_PORT):
        self.headers = {}
        
        if HTTPS_PROXY != "":
            # parse proxy URL
            url = urlparse.urlparse(HTTPS_PROXY)
            if url.scheme == "" or url.scheme == "http":
                port = httplib.HTTP_PORT
                host = url.hostname
                if url.port != None:
                    port = url.port
                if url.username != None:
                    self.headers["Proxy-authorization"] = "Basic " + base64.encodestring(url.username+':'+url.password) + "\r\n"
            else:
                raise AssertionError, "Transport %s not supported for HTTPS_PROXY" % url.scheme

            self.conn = httplib.HTTPConnection(host, port)
        else:
            self.conn = httplib.HTTPSConnection(host, port)

    def request(self, method, url, body="", headers={}):
        headers.update(self.headers)
        urlparts = urlparse.urlsplit(url)
        if HTTPS_PROXY != "":
            port = httplib.HTTPS_PORT
            if urlparts.port != None:
                port = urlparts.port
            return self.conn.request("CONNECT", urlparts.hostname + ":" + port, body, headers)
        else:
            url = urlparts.path + "?" + urlparts.query
            return self.conn.request("GET", url, body, headers)

    def getresponse(self):
        return self.conn.getresponse()

    def close(self):
        return self.conn.close()

#####################################################

############# segmented download functions #############

class Segment_Manager:
    def __init__(self, urls, localfile, size=0, chunk_size = 262144, chunksums = {}, reporthook = None):        
        self.sockets = []
        self.chunks = []
        self.limit_per_host = LIMIT_PER_HOST
        self.host_limit = HOST_LIMIT
        self.size = int(size)
        self.orig_urls = urls
        self.urls = urls
        self.chunk_size = int(chunk_size)
        self.chunksums = chunksums
        self.reporthook = reporthook
        self.filter_urls()
        
        # Open the file.
        try:
            self.f = open(localfile, "rb+")
        except IOError:
            self.f = open(localfile, "wb+")
            
        self.resume = FileResume(localfile + ".temp")
        self.resume.update_block_size(self.chunk_size)

    def get_chunksum(self, index):
        mylist = {}
        
        try:
            for key in self.chunksums.keys():
                mylist[key] = self.chunksums[key][index]
        except: pass
        
        return mylist

    def get_size(self):
        '''
        Take a best guess at size based on first 3 matching servers
        '''
        i = 0
        sizes = []
        urls = list(self.urls)
        
        while (i < len(urls) and (len(sizes) < 3)):
            url = urls[i]
            protocol = get_transport(url)
            if protocol == "http":
                status = httplib.MOVED_PERMANENTLY
                count = 0
                while (status == httplib.MOVED_PERMANENTLY or status == httplib.FOUND) and count < MAX_REDIRECTS:
                    http = Http_Host(url)
                    if http.conn != None:
                        http.conn.request("HEAD", url)
                        response = http.conn.getresponse()
                        status = response.status
                        url = response.getheader("Location")
                        http.close()
                    count += 1

                size = response.getheader("content-length")

                if (status == httplib.OK) and (size != None):
                    sizes.append(size)

            elif protocol == "ftp":
                ftp = Ftp_Host(url)
                size = ftp.conn.size(url)
                if size != None:
                    sizes.append(size)
                
            i += 1

        if len(sizes) == 1:
            return int(sizes[0])
        if sizes.count(sizes[0]) >= 2:
            return int(sizes[0])
        if sizes.count(sizes[1]) >= 2:
            return int(sizes[1])
        
        return None
    
    def filter_urls(self):
        newurls = {}
        for item in self.urls.keys():
            if (not item.endswith(".torrent")) and (get_transport(item) in PROTOCOLS):
                newurls[item] = self.urls[item]
        self.urls = newurls
        return newurls
            
    def run(self):
        if self.size == "" or self.size == 0:
            self.size = self.get_size()
            if self.size == None:
                #crap out and do it the old way
                self.close_handler()
                return False
        
        while True:
            #print "\ntc:", self.active_count(), len(self.sockets), len(self.urls)
            #if self.active_count() == 0:
            #print self.byte_total(), self.size
            time.sleep(0.1)
            self.update()
            self.resume.extend_blocks(self.chunk_list())
            if self.byte_total() >= self.size and self.active_count() == 0:
                self.close_handler()
                self.resume.complete()
                return True
            #crap out and do it the old way
            if len(self.urls) == 0:
                self.close_handler()
                return False
            
        return False

    def update(self):
        next = self.next_url()
        
        if next == None:
            return
        
        index = self.get_chunk_index()
        if index != None:
            if self.reporthook != None:
                self.reporthook(int(self.byte_total()/self.chunk_size), self.chunk_size, self.size)
            
            start = index * self.chunk_size
            end = start + self.chunk_size
            if end > self.size:
                end = self.size

            if next.protocol == "http" or next.protocol == "https":
                segment = Http_Host_Segment(next, start, end, self.size, self.get_chunksum(index))
                self.chunks[index] = segment
                self.segment_init(index)
            if next.protocol == "ftp":
                #print "allocated to:", index, next.url
                segment = Ftp_Host_Segment(next, start, end, self.size, self.get_chunksum(index))
                self.chunks[index] = segment
                self.segment_init(index)

    def segment_init(self, index):
        segment = self.chunks[index]
        if str(index) in self.resume.blocks:
            segment.end()
            if segment.error == None:
                segment.bytes = segment.byte_count
            else:
                self.resume.remove_block(index)
        else:
            segment.start()

    def get_chunk_index(self):
        i = -1
        for i in range(len(self.chunks)):
            if (self.chunks[i].error != None):
                return i
            # weed out dead segments that have temp errors and reassign
            if (not self.chunks[i].isAlive() and self.chunks[i].bytes == 0):
                return i
        i += 1

        if (i * self.chunk_size) < self.size:
            self.chunks.append(None)
            return i
        
        return None
        
    def gen_count_array(self):
        temp = {}
        for item in self.sockets:
            try:
                temp[item.url] += 1
            except KeyError:
                temp[item.url] = 1
        return temp

    def active_count(self):
        count = 0
        for item in self.chunks:
            if item.isAlive():
                count += 1
        return count

    def next_url(self):
        ''' returns next socket to use or None if none available'''
        self.remove_errors()
  
        if (len(self.sockets) >= (self.host_limit * self.limit_per_host)) or (len(self.sockets) >= (self.limit_per_host * len(self.urls))):
            # We can't create any more sockets, but we can see what's available
            #print "existing sockets"
            for item in self.sockets:
                #print item.active, item.url
                if not item.get_active():
                    return item
            return None

        count = self.gen_count_array()
        # randomly start with a url index
        #urls = list(self.urls)
        #number = int(random.random() * len(self.urls))
        urls = start_sort(self.urls)
        number = 0
    
        countvar = 1
        while (countvar <= len(self.urls)):
            try:
                tempcount = count[urls[number]]
            except KeyError:
                tempcount = 0
            # check against limits
            if ((tempcount == 0) and (len(count) < self.host_limit)) or (0 < tempcount < self.limit_per_host):
                # check protocol type here
                protocol = get_transport(urls[number])
                if (not urls[number].endswith(".torrent")) and (protocol == "http" or protocol == "https"):
                    host = Http_Host(urls[number], self.f)
                    self.sockets.append(host)
                    return host
                if (protocol == "ftp"):
                    try:
                        host = Ftp_Host(urls[number], self.f)
                    except (socket.gaierror, socket.timeout, ftplib.error_temp, ftplib.error_perm, socket.error):
                        #print "FTP connect failed %s" % self.urls[number]
                        self.urls.pop(urls[number])
                        return None
                    self.sockets.append(host)
                    return host
                    
            number = (number + 1) % len(self.urls)
            countvar += 1

        return None

    def remove_errors(self):
        for item in self.chunks:
            if item.error != None:
                #print item.error
                if item.error == httplib.MOVED_PERMANENTLY or item.error == httplib.FOUND:
                    #print "location:", item.location
                    newitem = copy.deepcopy(self.urls[item.url])
                    newitem.url = item.location
                    self.urls[item.location] = newitem
                    self.filter_urls()
                    
                #print "removed %s" % item.url
                try:
                    self.urls.pop(item.url)
                except KeyError: pass

        for socketitem in self.sockets:
            if socketitem.url not in self.urls.keys():
                #print socketitem.url
                #socketitem.close()
                self.sockets.remove(socketitem)

        return

    def byte_total(self):
        total = 0
        count = 0
        for item in self.chunks:
            try:
                if item.error == None:
                    total += item.bytes
            except (AttributeError): pass
            count += 1
        return total

    def chunk_list(self):
        chunks = []
        for i in range(len(self.chunks)):
            #print i, self.chunks[i].bytes
            try:
                if self.chunks[i].bytes == self.chunk_size:
                    chunks.append(i)
            except (AttributeError): pass
        #print chunks
        return chunks
    
    def close_handler(self):
        self.f.close()
        for host in self.sockets:
            host.close()

class Host_Base:
    '''
    Base class for various host protocol types.  Not to be used directly.
    '''
    def __init__(self, url, memmap):
        self.bytes = 0
        self.ttime = 0
        self.start_time = None
        self.error = None
        self.conn = None
        self.active = False
        
        self.url = url
        self.mem = memmap

        transport = get_transport(self.url)
        self.protocol = transport
        
    def import_stats(self, segment):
        pass

    def set_active(self, value):
        self.active = value

    def get_active(self):
        return self.active

class Ftp_Host(Host_Base):
    def __init__(self, url, memmap=None):
        Host_Base.__init__(self, url, memmap)

        self.connect()

    def connect(self):
        if self.protocol == "ftp":
            urlparts = urlparse.urlsplit(self.url)
            try:
                username = urlparts.username
                password = urlparts.password
            except AttributeError:
                # needed for python < 2.5
                username = None
                
            if username == None:
                username = "anonymous"
                password = "anonymous"
            try:
                port = urlparts.port
            except:
                port = ftplib.FTP_PORT
            if port == None:
                port = ftplib.FTP_PORT

            self.conn = FTP()
            self.conn.connect(urlparts[1], port)
            try:
                self.conn.login(username, password)
            except:
                #self.error = "login failed"
                raise
                return
            # set to binary mode
            self.conn.voidcmd("TYPE I")
        else:
            self.error = "unsupported protocol"
            raise AssertionError
            #return
        
    def close(self):
        if self.conn != None:
            try:
                self.conn.quit()
            except:
                pass

    def reconnect(self):
        self.close()
        self.connect()
            
class Http_Host(Host_Base):
    def __init__(self, url, memmap=None):
        Host_Base.__init__(self, url, memmap)
        
        urlparts = urlparse.urlsplit(self.url)
        if self.url.endswith(".torrent"):
            self.error = "unsupported protocol"
            return
        elif self.protocol == "http":
            try:
                port = urlparts.port
            except:
                port = httplib.HTTP_PORT
            if port == None:
                port = httplib.HTTP_PORT
            try:
                self.conn = HTTPConnection(urlparts[1], port)
            except httplib.InvalidURL:
                self.error = "invalid url"
                return
        elif self.protocol == "https":
            try:
                port = urlparts.port
            except:
                port = httplib.HTTPS_PORT
            if port == None:
                port = httplib.HTTPS_PORT
            try:
                self.conn = HTTPSConnection(urlparts[1], port)
            except httplib.InvalidURL:
                self.error = "invalid url"
                return
        else:
            self.error = "unsupported protocol"
            return
        
    def close(self):
        if self.conn != None:
            self.conn.close()

class Host_Segment:
    '''
    Base class for various segment protocol types.  Not to be used directly.
    '''
    def __init__(self, host, start, end, filesize, checksums = {}):
        threading.Thread.__init__(self)
        self.host = host
        self.host.set_active(True)
        self.byte_start = start
        self.byte_end = end
        self.byte_count = end - start
        self.filesize = filesize
        self.url = host.url
        self.mem = host.mem
        self.checksums = checksums
        self.error = None        
        self.ttime = 0
        self.response = None
        self.bytes = 0
        self.buffer = ""
        self.temp = ""

    def avg_bitrate(self):
        bits = self.bytes * 8
        return bits/self.ttime

    def checksum(self):
        lock = threading.Lock()
        lock.acquire()
        
        self.mem.seek(self.byte_start, 0)
        chunkstring = self.mem.read(self.byte_count)
        
        lock.release()

        return verify_chunk_checksum(chunkstring, self.checksums)

    def close(self):
        if self.error != None:
            self.host.close()

        self.host.set_active(False)

    def end(self):
        if not self.checksum():
            self.error = "Chunk checksum failed"
        self.close()

class Ftp_Host_Segment(threading.Thread, Host_Segment):
    def __init__(self, *args):
        threading.Thread.__init__(self)
        Host_Segment.__init__(self, *args)

    def run(self):
        # Finish early if checksum is OK
        if self.checksum() and len(self.checksums) > 0:
            self.bytes += self.byte_count
            self.close()
            return
        
        # check for supported hosts/urls
        urlparts = urlparse.urlsplit(self.url)
        if self.host.conn == None:
            #print "bad socket"
            self.error = "bad socket"
            self.close()
            return
        
        size = None
        retry = True
        count = 0
        while retry and count < CONNECT_RETRY_COUNT:
            retry = False
            try:
                (self.response, size) = self.host.conn.ntransfercmd("RETR " + urlparts.path, self.byte_start, self.byte_end)
            except (ftplib.error_perm), error:
                self.error = error.message
                self.close()
                return
            except (socket.gaierror, socket.timeout), error:
                self.error = error.args
                self.close()
                return
            except EOFError:
                self.error = "EOFError"
                self.close()
                return
            except AttributeError:
                self.error = "AttributeError"
                self.close()
                return
            except (socket.error), error:
                #print "reconnect", self.host.url
                self.host.reconnect()
                retry = True
                count += 1
            except (ftplib.error_temp), error:
                # this is not an error condition, most likely transfer TCP connection was closed
                #count += 1
                #self.error = "error temp", error.message
                self.temp = error.message
                self.close()
                return
            except (ftplib.error_reply), error:
                # this is likely just an extra chatty FTP server, ignore for now
                pass

            if count >= CONNECT_RETRY_COUNT:
                self.error = "socket reconnect attempts failed"
                self.close()
                return
    
        if size != None:
            if self.filesize != size:
                self.error = "bad file size"
                return
        
        self.start_time = time.time()
        while True:
            if self.readable():
                self.handle_read()
            else:
                self.ttime += (time.time() - self.start_time)
                self.end()
                return

    def readable(self):
        if self.response == None:
            return False
        return True
    
    def handle_read(self):
        try:
            data = self.response.recv(1024)
        except socket.timeout:
            self.error = "read timeout"
            self.response = None
            return

        if len(data) == 0:
            return

        self.buffer += data
        #print len(self.buffer), self.byte_count
        if len(self.buffer) >= self.byte_count:
            # When using a HTTP proxy there is no shutdown() call
            try:
                self.response.shutdown(socket.SHUT_RDWR)
            except AttributeError:
                pass

            tempbuffer = self.buffer[:self.byte_count]
            self.buffer = ""

            self.bytes += len(tempbuffer)

            lock = threading.Lock()
            lock.acquire()
            
            self.mem.seek(self.byte_start, 0)
            self.mem.write(tempbuffer)
            self.mem.flush()

            lock.release()
        
            self.response = None
            
        # this method writes directly to file on each data grab, not working for some reason
##        if (self.bytes + len(data)) >= self.byte_count:
##            # When using a HTTP proxy there is no shutdown() call
##            try:
##                self.response.shutdown(socket.SHUT_RDWR)
##            except AttributeError:
##                pass
##
##            index = self.byte_count - (self.bytes + len(data))
##
##            writedata = data[:index]
##
##            lock = threading.Lock()
##            lock.acquire()
##            
##            self.mem.seek(self.byte_start + self.bytes, 0)
##            self.mem.write(writedata)
##            self.mem.flush()
##            
##            lock.release()
##
##            self.response = None
##        else:
##            writedata = data
##
##            lock = threading.Lock()
##            lock.acquire()
##            
##            self.mem.seek(self.byte_start + self.bytes, 0)
##            self.mem.write(writedata)
##            
##            lock.release()
##
##        self.bytes += len(writedata)

        
class Http_Host_Segment(threading.Thread, Host_Segment):
    def __init__(self, *args):
        threading.Thread.__init__(self)
        Host_Segment.__init__(self, *args)
        
    def run(self):
        # Finish early if checksum is OK
        if self.checksum() and len(self.checksums) > 0:
            self.bytes += self.byte_count
            self.close()
            return
        
        if self.host.conn == None:
            self.error = "bad socket"
            self.close()
            return

        try:
            self.host.conn.request("GET", self.url, "", {"Range": "bytes=%lu-%lu\r\n" % (self.byte_start, self.byte_end - 1)})
        except:
            self.error = "socket exception"
            self.close()
            return
        
        self.start_time = time.time()
        while True:
            if self.readable():
                self.handle_read()
            else:
                self.ttime += (time.time() - self.start_time)
                self.end()
                return

    def readable(self):
        if self.response == None:
            try:
                self.response = self.host.conn.getresponse()
            except socket.timeout:
                self.error = "timeout"
                return False
            # not an error state, connection closed, kicks us out of thread
            except httplib.ResponseNotReady:
                return False
            except:
                self.error = "response error"
                return False
            
        if self.response.status == httplib.PARTIAL_CONTENT:
            return True
        elif self.response.status == httplib.MOVED_PERMANENTLY or self.response.status == httplib.FOUND:
            self.location = self.response.getheader("Location")
            self.error = self.response.status
            self.response = None
            return False
        else:
            self.error = self.response.status
            self.response = None
            return False
        return False
    
    def handle_read(self):
        try:
            data = self.response.read()
        except socket.timeout:
            self.error = "timeout"
            self.response = None
            return
        except httplib.IncompleteRead:
            self.error = "incomplete read"
            self.response = None
            return
        if len(data) == 0:
            return

        rangestring = self.response.getheader("Content-Range")
        request_size = int(rangestring.split("/")[1])

        if request_size != self.filesize:
            self.error = "bad file size"
            self.response = None
            return

        body = data
        size = len(body)
        # write out body to file

        lock = threading.Lock()
        lock.acquire()
        
        self.mem.seek(self.byte_start, 0)
        self.mem.write(body)
        self.mem.flush()

        lock.release()
        
        self.bytes += size
        self.response = None


###################################################

class ProgressBar:
    def __init__(self, length = 68):
        self.length = length
        #print ""
        #self.update(0, 0)
        self.total_size = 0

    def download_update(self, block_count, block_size, total_size):
        self.total_size = total_size
        
        current_bytes = float(block_count * block_size) / 1024 / 1024
        total_bytes = float(total_size) / 1024 / 1024
            
        try:
            percent = 100 * current_bytes / total_bytes
        except ZeroDivisionError:
            percent = 0
            
        if percent > 100:
            percent = 100

        if total_bytes < 0:
            return

        size = int(percent * self.length / 100)
        bar = ("#" * size) + ("-" * (self.length - size))
        output = "[%s] %.0f%% %.2f/%.2f MB" % (bar, percent, current_bytes, total_bytes)
        
        self.line_reset()
        sys.stdout.write(output)

    def update(self, count, total):
        if count > total:
            count = total
            
        try:
            percent = 100 * float(count) / total
        except ZeroDivisionError:
            percent = 0

        if total < 0:
            return

        size = int(percent * self.length / 100)
        bar = ("#" * size) + ("-" * (self.length - size))
        output = "[%s] %.0f%%" % (bar, percent)
        
        self.line_reset()
        sys.stdout.write(output)

    def line_reset(self):
        sys.stdout.write("\b" * 80)
        if os.name != 'nt':
            sys.stdout.write("\n")
        
    def end(self):
        self.update(1, 1)
        #print ""

    def download_end(self):
        self.download_update(1, self.total_size, self.total_size)
        #print ""

if __name__ == "__main__":
    run()
