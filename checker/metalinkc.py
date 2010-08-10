#!/usr/bin/env python
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2010, Neil McNab
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
#   Metalink Checker is a command line application that checks general 
# validity (valid XML) or downloads (executes) metalink files. It downloads 
# the files, checks their SHA1 or MD5 verification and verifies that the 
# files are working.
#
#   Command line application and Python library that checks or downloads
# metalink files.  Requires Python 2.5 or newer.
#
# Instructions:
#   1. You need to have Python installed.
#   2. To check PGP signatures you need to install gpg (http://www.gnupg.org) or gpg4win (http://www.gpg4win.org/)
#   3. Run on the command line using: python metalink.py
#
# Usage: metalinkc.py [-c|-d|-j|--convert|--rconvert] [options] arg1 arg2 ...
#
# Options:
#   --version             show program's version number and exit
#   -h, --help            show this help message and exit
#   -d, --download        Actually download the file(s) in the metalink
#   -c, --check           Check the metalink file URLs
#   -t TIMEOUT, --timeout=TIMEOUT
#                         Set timeout in seconds to wait for response
#                         (default=10)
#   -o OS, --os=OS        Operating System preference
#   -s, --no-segmented    Do not use the segmented download method
#   -l LANG, --lang=LANG  Language preference (ISO-639/3166)
#   --country=LOC         Two letter country preference (ISO 3166-1 alpha-2)
#   -k DIR, --pgp-keys=DIR
#                         Directory with the PGP keys that you trust (default:
#                         working directory)
#  -p FILE, --pgp-store=FILE
#                         File with the PGP keys that you trust (default:
#                         ~/.gnupg/pubring.gpg)
#   -g GPG, --gpg-binary=GPG
#                         (optional) Location of gpg binary path if not in the
#                         default search path
#   -j, --convert-jigdo   Convert Jigdo format file to Metalink
#   --port=PORT           Streaming server port to use (default: No streaming
#                         server)
#   --html=HTML           Extract links from HTML webpage
#   --convert             Conversion from 3 to 4 (IETF RFC)
#   --rconvert            Reverses conversion from 4 (IETF RFC) to 3
#   --output=OUTFILE      Output conversion result to this file instead of
#                         screen
#   -r, --rss             RSS/Atom Feed Mode, implies -d
#   -w WRITEDIR           Directory to write output files to (default: current
#                         directory)
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
#
# Version 5.1
# -----------
# - Bugfixes for segmented downloads
# - Native Jigdo download support
# - Added download time
# - Now requires Python 2.5 or newer because Metalink RFC requires SHA-256
#
# Version 5.0
# -----------
# - Added support for Metalink v4 (IETF RFC)
# - Changed executable name from metalink to metalinkc
# - Removed unneeded -f options
# - Added conversion options
#
# Version 4.4
# -----------
# - Bugfix for when HTTP 302 redirect code is issued during download
#
# Version 4.3
# -----------
# - Added custom HTTP header support
# - Added option to parse an HTML file for .metalink files to check
# - Started Debian packaging
# - Added a beta feature for media streaming
# - Added a minimal GUI for checking
# - Various bugfixes
#
# Version 4.2
# -----------
# - PGP bugfix
# - Jigdo to Metalink convertor
# - Other bugfixes
#
# Version 4.1
# -----------
# - Start of transition of how command line options are used
# - XML parsing speed and memory improvements
# - Checking function is now multithreaded for speed improvements
# - Displays download bitrates
# - Grabs proxy info from environment variables and Windows registry
# - Fix for faulty file locking, this causes corrupted downloads
#
# Version 4.0
# -----------
# - Uses gzip compression when available on server (non-segmented downloads only)
# - Fixed memory leak when computing a checksum
# - Bugfixes for download resuming
#
# Version 3.8
# -----------
# - Will now download any file type and auto-detect metalink files
# - Added option to disable segmented downloads to command line
# - Added support for metalink "Accept" HTTP header
#
# Version 3.7.4
# -------------
# - Fixed default key import directory
#
# Version 3.7.3
# -------------
# - Fixes for use with UNIX/Linux
# - bugfixes in checker code
#
# Version 3.7.2
# -------------
# - Modified to remove the pyme dependency
#
# Version 3.7.1
# -------------
# - Removed missing imports
#
# Version 3.7
# -----------
# - Added first attempt at PGP signature checking
# - Minor bugfixes
#
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
# - resume download support for non-segmented downloads
# - download priority based on speed
# - use maxconnections
# - dump FTP data chunks directly to file instead of holding in memory
# - maybe HTTPS proxy support if people need it
########################################################################
try: import GPG
except: pass
try: import win32api
except: pass
try: import win32con
except: pass
try: import win32process
except ImportError: pass
try: import bz2
except ImportError: pass
import copy
import gzip
import httplib
import binascii
import ftplib
import sys
import gettext
import BaseHTTPServer
import socket
import math
import optparse
import threading
import calendar
import zlib
import os.path
import urllib2
import os
import rfc822
import xml.parsers.expat
import locale
import re
import HTMLParser
import time
import subprocess
import StringIO
import base64
import urlparse
import hashlib
import random
class Dummy:
    pass
#!/usr/bin/env python
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2010, Neil McNab
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
# Filename: $URL: https://metalinks.svn.sourceforge.net/svnroot/metalinks/checker/checker.py $
# Last Updated: $Date: 2010-04-21 22:05:23 -0700 (Wed, 21 Apr 2010) $
# Version: $Rev: 653 $
# Author(s): Neil McNab
#
# Description:
#   Command line application and Python library that checks metalink files.
# Requires Python 2.5 or newer.
#
# Library Instructions:
#   - Use as expected.
#
# import checker
#
# results = checker.check_metalink("file.metalink")
#
########################################################################




NAME="Metalink Checker"
VERSION="5.1"

#WEBSITE="http://www.metalinker.org"
WEBSITE="http://www.nabber.org/projects/checker/"

MAX_REDIRECTS = 20
MAX_THREADS = 10

def translate():
    '''
    Setup translation path
    '''
    if __name__=="__main__":
        try:
            base = os.path.basename(__file__)[:-3]
            localedir = os.path.join(os.path.dirname(__file__), "locale")
        except NameError:
            base = os.path.basename(sys.executable)[:-4]
            localedir = os.path.join(os.path.dirname(sys.executable), "locale")
    else:
        temp = __name__.split(".")
        base = temp[-1]
        localedir = os.path.join("/".join(["%s" % k for k in temp[:-1]]), "locale")

    #print base, localedir
    localelang = locale.getdefaultlocale()[0]
    if localelang == None:
        localelang = "LC_ALL"
    t = gettext.translation(base, localedir, [localelang], None, 'en')
    return t.ugettext

_ = translate()

ABOUT = NAME + "\n" + _("Version") + ": " + VERSION + "\n" + \
                     _("Website") + ": " + WEBSITE + "\n\n" + \
                     _("Copyright") + ": 2009 Neil McNab\n" + \
                     _("License") + ": " + _("GNU General Public License, Version 2") + "\n\n" + \
                     NAME + _(" comes with ABSOLUTELY NO WARRANTY.  This is free software, and you are welcome to redistribute it under certain conditions, see LICENSE.txt for details.")


class Webpage(HTMLParser.HTMLParser):

    def __init__(self, *args):
        self.urls = []
        self.url = ""
        HTMLParser.HTMLParser.__init__(self, *args)

    def set_url(self, url):
        self.url = url

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for item in attrs:
                if item[0] == "href":
                    url = item[1]
                    if not download.is_remote(item):
                        #fix relative links
                        url = download.path_join(self.url, url)
                    if not url.startswith("mailto:"):
                        self.urls.append(url)
                        #print url


class Checker:
    def __init__(self):
        self.threadlist = []
        self.running = False
        self.clear_results()
        self.cancel = False
        
    def check_metalink(self, src):
        '''
        Decode a metalink file, can be local or remote
        First parameter, file to download, URL or file path to download from
        Returns the results of the check in a dictonary
        '''
        self.running = True
        src = download.complete_url(src)
        
        try:
            metalinkobj = download.parse_metalink(src, nocheck=False)
        except:
            print _("ERROR parsing XML.")
            raise
            
        if not metalinkobj:
            return False
        
        if metalinkobj.type == "dynamic":
            origin = metalinkobj.origin
            if origin != src and origin != "":
                try:
                    result = self.check_metalink(origin)
                    self.running = True
                    return result
                except:
                    print "Error downloading from origin %s, not using." % origin
        
        urllist = metalinkobj.files
        if len(urllist) == 0:
            print _("No urls to download file from.")
            self.running = False
            return False

        #results = {}
        for filenode in urllist:
            #size = filenode.size
            #name = filenode.filename
            #print "=" * 79
            #print _("File") + ": %s " % name + _("Size") + ": %s" % size
            myheaders = {}
            if download.is_remote(src):
                myheaders = {'referer': src}
            self.check_file_node(filenode, myheaders)

        self.running = False
        #return results

    def isAlive(self):
        if self.running:
            return True
        for threadobj in self.threadlist:
            if threadobj.isAlive():
                return True
        return False

    def activeCount(self):
        count = 0
        for threadobj in self.threadlist:
            if threadobj.isAlive():
                count += 1
        return count

    def _add_result(self, key1, key2, value):
        try:
            self.results[key1]
        except KeyError:
            self.results[key1] = {}

        try:
            self.new_results[key1]
        except KeyError:
            self.new_results[key1] = {}
            
        self.results[key1][key2] = value
        self.new_results[key1][key2] = value

    def get_results(self, block=True):
        while block and self.isAlive():
            time.sleep(0.1)

        return self.results

    def get_new_results(self):
        temp = self.new_results
        self.new_results = {}
        return temp

    def stop(self):
        self.cancel = True
        while self.isAlive():
            time.sleep(0.1)        

    def clear_results(self):
        self.stop()
        self.threadlist = []
        self.results = {}
        self.new_results = {}
        
    def _check_process(self, headers, filesize, checksums = {}):
        size = "?"
        checksum = "?"
        
        sizeheader = self._get_header(headers, "Content-Length")
        
        # digest code, untested since no servers seem to support this
        digest = self._get_header(headers, "Content-MD5")
        if digest != None:
            try:
                if binascii.hexlify(binascii.a2b_base64(digest)).lower() == checksums['md5'].lower():
                    checksum = _("OK")
                else:
                    checksum = _("FAIL")
            except KeyError: pass

        digest = self._get_header(headers, "Digest")
        if digest != None:
            digests = digest.split(",")
            for d in digests:
                (name, value) = d.split("=", 2)
                typestr = ""
                if name.lower() == "sha":
                    typestr = "sha1"
                elif name.lower() == "md5":
                    typestr = "md5"
                    
                if typestr != "" and checksum == "?":
                    try:
                        if binascii.hexlify(binascii.a2b_base64(value)).lower() == checksums[typestr].lower():
                            checksum = _("OK")
                        else:
                            checksum = _("FAIL")
                    except KeyError: pass

        if sizeheader != None and filesize != None:
            if int(sizeheader) == int(filesize):
                size = _("OK")
            elif int(filesize) != 0:
                size = _("FAIL")

        response_code = _("OK")
        temp_code = self._get_header(headers, "Response")
        if temp_code != None:
            response_code = temp_code
            
        return [response_code, size, checksum]

    def _get_header(self, textheaders, name):
        textheaders = str(textheaders)
        
        headers = textheaders.split("\n")
        headers.reverse()
        for line in headers:
            line = line.strip()
            result = line.split(": ")
            if result[0].lower() == name.lower():
                return result[1]

        return None

    def check_file_node(self, item, myheaders = {}):
        '''
        First parameter, file object
        Returns dictionary of file paths with headers
        '''
        self.running = True
        #self.results[item.name] = {}
        size = item.size
        urllist = item.resources
        if len(urllist) == 0:
            print _("No urls to download file from.")
            self.running = False
            return False

        def thread(filename, myheaders):
            checker = URLCheck(filename, myheaders)
            headers = checker.info()
            redir = self._get_header(headers, "Redirected")
            result = self._check_process(headers, size, item.get_checksums())
            result.append(redir)
            #self.results[item.name][checker.geturl()] = result
            self._add_result(item.filename, filename, result)
            #print "-" *79
            #print _("Checked") + ": %s" % filename
            #if redir != None:
            #    print _("Redirected") + ": %s" % redir
            #print _("Response Code") + ": %s\t" % self.results[item.name][filename][0] + _("Size Check") + ": %s" % self.results[item.name][filename][1]
                
        number = 0
        filename = {}
            
        count = 1
        result = {}
        while (count <= len(urllist)):
            filename = urllist[number].url
            #don't start too many threads at once
            while self.activeCount() > MAX_THREADS and not self.cancel:
                time.sleep(0.1)
            mythread = threading.Thread(target = thread, args = [filename, myheaders], name = filename)
            mythread.start()
            self.threadlist.append(mythread)
            #thread(filename)
            number = (number + 1) % len(urllist)
            count += 1

        # don't return until all threads are finished (except the one main thread)
        #while threading.activeCount() > 1:
        #    pass
        #return result
        self.running = False
       
class URLCheck:    
    def __init__(self, url, myheaders = {}):
        self.infostring = ""
        self.url = url
        urlparts = urlparse.urlparse(url)
        self.scheme = urlparts.scheme
        headers = {"Want-Digest": "MD5;q=0.3, SHA;q=1"}
        headers.update(myheaders)
        
        if self.scheme == "http":
            # need to set default port here
            port = httplib.HTTP_PORT
            try:
                if urlparts.port != None:
                    port = urlparts.port
            except ValueError:
                self.infostring += _("Response") + ": " + _("Bad URL") + "\r\n"
                return
    
            conn = download.HTTPConnection(urlparts.hostname, port)
            try:
                conn.request("HEAD", url, headers = headers)
            except socket.error, error:
                self.infostring += _("Response") + ": " + _("Connection Error") + "\r\n"
                return

            try:
                resp = conn.getresponse()
            except socket.timeout:
                self.infostring += _("Response") + ": " + _("Timeout") + "\r\n"
                return
            except socket.error, error:
                self.infostring += _("Response") + ": " + _("Connection Error") + "\r\n"
                return
            
            # handle redirects here and set self.url
            count = 0
            while (resp != None and (resp.status == httplib.MOVED_PERMANENTLY or resp.status == httplib.FOUND) and count < MAX_REDIRECTS):
                url = resp.getheader("location")
                #print _("Redirected from ") + self.url + " to %s." % url
                self.infostring += _("Redirected") + ": %s\r\n" % url
                conn.close()
                urlparts = urlparse.urlparse(url)
                # need to set default port here
                port = httplib.HTTP_PORT
                if urlparts.port != None:
                    port = urlparts.port
                
                conn = download.HTTPConnection(urlparts.hostname, urlparts.port)
                try:
                    conn.request("HEAD", url, headers = headers)
                    resp = conn.getresponse()
                except socket.gaierror:
                    resp = None
                
                count += 1

            self.url = url
            if resp == None:
                self.infostring += _("Response") + ": socket error\r\n"
            elif resp.status == httplib.OK:
                self.infostring += _("Response") + ": " + _("OK") + "\r\n"
            else:
                self.infostring += _("Response") + ": %s %s\r\n" % (resp.status, resp.reason)
            
            # need to convert list into string
            if resp != None:
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
                self.infostring += _("Response") + ": " + _("Bad URL") + "\r\n"
                return
    
            conn = download.HTTPSConnection(urlparts.hostname, port)
            try:
                conn.request("HEAD", url, headers = headers)
            except socket.error, error:
                #dir(error)
                self.infostring += _("Response") + ": " + _("Connection Error") + "\r\n"
                return
                
            resp = conn.getresponse()
            
            # handle redirects here and set self.url
            count = 0
            while (resp.status == httplib.MOVED_PERMANENTLY or resp.status == httplib.FOUND) and count < MAX_REDIRECTS:
                url = resp.getheader("location")
                #print _("Redirected") + ": %s" % url
                self.infostring += _("Redirected") + ": %s\r\n" % url
                conn.close()
                urlparts = urlparse.urlparse(url)
                # need to set default port here
                port = httplib.HTTPS_PORT
                if urlparts.port != None:
                    port = urlparts.port
                
                conn = download.HTTPSConnection(urlparts.hostname, urlparts.port)
                conn.request("HEAD", url, headers = headers)
                resp = conn.getresponse()
                count += 1

            self.url = url
            if resp.status == httplib.OK:
                self.infostring += _("Response") + ": " + _("OK") + "\r\n"
            else:
                self.infostring += _("Response") + ": %s %s\r\n" % (resp.status, resp.reason)
            
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

            ftpobj = download.FTP()
            try:
                ftpobj.connect(urlparts[1])
            except socket.gaierror:
                self.infostring += _("Response") + ": " + _("Bad Hostname") + "\r\n"
                return
            except socket.timeout:
                self.infostring += _("Response") + ": " + _("timed out") + "\r\n"
                return
            except socket.error:
                self.infostring += _("Response") + ": " + _("Connection refused") + "\r\n"
                return
            except (ftplib.error_perm, ftplib.error_temp), error:
                self.infostring += _("Response") + ": %s\r\n" % error.message
                return
            
            try:
                ftpobj.login(username, password)
            except (ftplib.error_perm, ftplib.error_temp), error:
                self.infostring += _("Response") + ": %s\r\n" % error.message
                
            if ftpobj.exist(url):
                self.infostring += _("Response") + ": " + _("OK") + "\r\n"
            else:
                self.infostring += _("Response") + ": " + _("Not Found") + "\r\n"
                
            try:
                size = ftpobj.size(url)
            except:
                size = None
                
            try:
                ftpobj.quit()
            except: pass
            
            if size != None:
                self.infostring += _("Content Length") + ": %s\r\n" % size   

        else:
            self.infostring += _("Response") + ": ?\r\n"
            
    def geturl(self):
        return self.url

    def info(self):
        # need response and content-length for HTTP
        return self.infostring
checker = Dummy()
checker.ABOUT = ABOUT
checker.Checker = Checker
checker.MAX_REDIRECTS = MAX_REDIRECTS
checker.MAX_THREADS = MAX_THREADS
checker.NAME = NAME
checker.URLCheck = URLCheck
checker.VERSION = VERSION
checker.WEBSITE = WEBSITE
checker.Webpage = Webpage
checker._ = _
checker.translate = translate
#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2010, Neil McNab
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
# Filename: $URL: https://metalinks.svn.sourceforge.net/svnroot/metalinks/checker/download.py $
# Last Updated: $Date: 2010-08-09 22:57:41 -0400 (Mon, 09 Aug 2010) $
# Author(s): Neil McNab
#
# Description:
#   Download library that can handle metalink files.
#
# Library Instructions:
#   - Use as expected.
#
# import download
#
# files = download.get("file.metalink", os.getcwd())
#
# Callback Definitions:
# def cancel():
#   Returns True to cancel, False otherwise
# def pause():
#   Returns True to pause, False to continue/resume
# def status(block_count, block_size, total_size):
#   Same format as urllib.urlretrieve reporthook
#   block_count - a count of blocks transferred so far
#   block_size - a block size in bytes
#   total_size - the total size of the file in bytes
# def bitrate(bitrate):
#   bitrate - kilobits per second (float)
#
########################################################################
#import logging

#import utils
#import thread
#import logging


# for jython support
#try: import bz2
#except ImportError: pass



USER_AGENT = "Metalink Checker/5.1 +http://www.nabber.org/projects/"

SEGMENTED = True
LIMIT_PER_HOST = 1
HOST_LIMIT = 5
MAX_REDIRECTS = 20
CONNECT_RETRY_COUNT = 3

MAX_CHUNKS = 256
DEFAULT_CHUNK_SIZE = 262144

LANG = []
OS = None
COUNTRY = None

lang = locale.getdefaultlocale()[0]
if lang == None:
    lang = "LC_ALL"
lang = lang.replace("_", "-").lower()
LANG = [lang]

if len(lang) == 5:
    COUNTRY = lang[-2:]

PGP_KEY_DIR="."
PGP_KEY_EXTS = (".gpg", ".asc")
PGP_KEY_STORE=None

# Configure proxies (user and password optional)
# HTTP_PROXY = http://user:password@myproxy:port
HTTP_PROXY=""
FTP_PROXY=""
HTTPS_PROXY=""
SOCKS_PROXY=""

# Streaming server setings to use
HOST = "localhost"
PORT = None

# Protocols to use for segmented downloads
PROTOCOLS=("http","https","ftp")
#PROTOCOLS=("ftp")

# See http://www.poeml.de/transmetalink-test/README
MIME_TYPE = "application/metalink+xml"

##### PROXY SETUP #########

def reg_query(keyname, value=None):
    if os.name != "nt":
        return []

    blanklines = 1
    
    if value == None:
        tempresult = os.popen2("reg.exe query \"%s\"" % keyname)
    else:
        tempresult = os.popen2("reg.exe query \"%s\" /v \"%s\"" % (keyname, value))
    stdout = tempresult[1]
    stdout = stdout.readlines()

    # handle case when reg.exe isn't in path
    if len(stdout) == 0:
        if value == None:
            tempresult = os.popen2(os.environ["WINDIR"] + "\\system32\\reg.exe query \"%s\"" % keyname)
        else:
            tempresult = os.popen2(os.environ["WINDIR"] + "\\system32\\reg.exe query \"%s\" /v \"%s\"" % (keyname, value))
        stdout = tempresult[1]
        stdout = stdout.readlines()

    # For Windows XP, this was changed in Vista!
    if len(stdout) > 0 and stdout[1].startswith("! REG.EXE"):
        blanklines += 2
        if value == None:
            blanklines += 2

    stdout = stdout[blanklines:]
    
    return stdout

def get_key_value(key, value):
    '''
    Probes registry for uninstall information
    First parameter, key to look in
    Second parameter, value name to extract
    Returns the uninstall command as a string
    '''
    # does not handle non-paths yet
    result = u""

    try:
        keyid = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, key)
        tempvalue = win32api.RegQueryValueEx(keyid, value)
        win32api.RegCloseKey(keyid)
        result = unicode(tempvalue[0])
    except NameError:
        # alternate method if win32api is not available, probably only works on Windows NT variants
        stdout = reg_query(u"HKCU\\" + key, value)
        
        try:
            # XP vs. Vista
            if stdout[1].find(u"\t") != -1:
                lines = stdout[1].split(u"\t")
                index = 2
            else:
                lines = stdout[1].split(u"    ")
                index = 3
            result = lines[index].strip()
        except IndexError:
            result = u""
    except: pass

    result = unicode(os.path.expandvars(result))
    return result

def get_proxy_info():
    global HTTP_PROXY
    global FTP_PROXY
    global HTTPS_PROXY

    # from environment variables
    if os.environ.has_key('http_proxy') and HTTP_PROXY == "":
        HTTP_PROXY=os.environ['http_proxy']
    if os.environ.has_key('ftp_proxy') and FTP_PROXY == "":
        FTP_PROXY=os.environ['ftp_proxy']
    if os.environ.has_key('https_proxy') and HTTPS_PROXY == "":
        HTTPS_PROXY=os.environ['https_proxy']

    # from IE in registry
    proxy_enable = get_key_value("Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings", "ProxyEnable")
    try:
    	proxy_enable = int(proxy_enable[-1])
    except IndexError:
        proxy_enable = False

    if proxy_enable:
        proxy_string = get_key_value("Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings", "ProxyServer")
        if proxy_string.find("=") == -1:
            # if all use the same settings
            for proxy in ("HTTP_PROXY", "FTP_PROXY", "HTTPS_PROXY"):
                if getattr(sys.modules[__name__], proxy) == "":
                    setattr(sys.modules[__name__], proxy, "http://" + str(proxy_string))
        else:
            proxies = proxy_string.split(";")
            for proxy in proxies:
                name, value = proxy.split("=")
                if getattr(sys.modules[__name__], name.upper() + "_PROXY") == "":
                    setattr(sys.modules[__name__], name.upper() + "_PROXY", "http://" + value)

get_proxy_info()

def translate():
    '''
    Setup translation path
    '''
    if __name__=="__main__":
        base = ""
        localedir = ""
        try:
            base = os.path.basename(__file__)[:-3]
            localedir = os.path.join(os.path.dirname(__file__), "locale")
        except NameError:
            if sys.executable != None:
                base = os.path.basename(sys.executable)[:-4]
                localedir = os.path.join(os.path.dirname(sys.executable), "locale")
    else:
        temp = __name__.split(".")
        base = temp[-1]
        localedir = os.path.join("/".join(["%s" % k for k in temp[:-1]]), "locale")

    #print base, localedir
    localelang = locale.getdefaultlocale()[0]
    if localelang == None:
        localelang = "LC_ALL"
    t = gettext.translation(base, localedir, [localelang], None, 'en')
    return t.ugettext

_ = translate()
    
def urlopen(url, data = None, metalink_header=False, headers = {}):
    #print "URLOPEN:", url, headers
    url = complete_url(url)
    req = urllib2.Request(url, data, headers)
    req.add_header('User-agent', USER_AGENT)
    req.add_header('Cache-Control', "no-cache")
    req.add_header('Pragma', "no-cache")
    req.add_header('Accept-Encoding', 'gzip')
    if metalink_header:
        req.add_header('Accept', MIME_TYPE + ", */*")

    fp = urllib2.urlopen(req) 
    try:
        if fp.headers['Content-Encoding'] == "gzip":
            return metalink.open_compressed(fp)
    except KeyError: pass

    return fp

def urlhead(url, metalink_header=False, headers = {}):
    '''
    raise IOError for example if the URL does not exist
    '''
    #print "URLHEAD:", url, headers
    url = complete_url(url)
    req = urllib2.Request(url, None, headers)
    req.add_header('User-agent', USER_AGENT)
    req.add_header('Cache-Control', "no-cache")
    req.add_header('Pragma', "no-cache")
    if metalink_header:
        req.add_header('Accept', MIME_TYPE + ", */*")

    req.get_method = lambda: "HEAD"
    #logging.debug(url)
    fp = urllib2.urlopen(req)
    newheaders = fp.headers
    fp.close()
    return newheaders

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
    opener = urllib2.build_opener(proxy_handler, urllib2.HTTPBasicAuthHandler(), 
            urllib2.HTTPHandler, urllib2.HTTPSHandler, urllib2.FTPHandler)
    # install this opener
    urllib2.install_opener(opener)

def get(src, path, checksums = {}, force = False, handlers = {}, segmented = SEGMENTED, headers = {}):
    '''
    Download a file, decodes metalinks.
    First parameter, file to download, URL or file path to download from
    Second parameter, file path to save to
    Third parameter, optional, expected dictionary of checksums
    Fourth parameter, optional, force a new download even if a valid copy already exists
    Fifth parameter, optional, progress handler callback
    Sixth parameter, optional, boolean to try using segmented downloads
    Returns list of file paths if download(s) is successful
    Returns False otherwise (checksum fails)
    raise socket.error e.g. "Operation timed out"
    '''
    if src.endswith(".jigdo"):
        return download_jigdo(src, path, force, handlers, segmented, headers)
    # assume metalink if ends with .metalink

    result = download_metalink(src, path, force, handlers, segmented, headers)
    if result:
        return result
            
    # assume normal file download here
    # parse out filename portion here
    filename = os.path.basename(src)
    result = download_file(src, os.path.join(path, filename), 
            0, checksums, force, handlers, segmented = segmented, headers = headers)
    if result:
        return [result]
    return False
    
def download_file(url, local_file, size=0, checksums={}, force = False, 
        handlers = {}, segmented = SEGMENTED, chunksums = {}, chunk_size = 0, headers = {}):
    '''
    url {string->URL} locations of the file
    local_file string local file name to save to
    checksums ?
    force ?
    handler ?
    segmented ?
    chunksums ?
    chunk_size ?
    returns ? 
    unicode Returns file path if download is successful.
        Returns False otherwise (checksum fails).    
    '''
    # convert string filename into something we can use
    #urllist = {}
    #urllist[url] = URL(url)

    fileobj = metalink.MetalinkFile(local_file)
    fileobj.set_size(size)
    fileobj.hashlist = checksums
    fileobj.pieces = chunksums
    fileobj.piecelength = chunk_size
    fileobj.add_url(url)

    return download_file_urls(fileobj, force, handlers, segmented, headers)
    
def download_file_urls(metalinkfile, force = False, handlers = {}, segmented = SEGMENTED, headers = {}):
    '''
    Download a file.
    MetalinkFile object to download
    Second parameter, optional, force a new download even if a valid copy already exists
    Third parameter, optional, progress handler callback
    Fourth parameter, optional, try to use segmented downloading
    Returns file path if download is successful
    Returns False otherwise (checksum fails)    
    '''
    
    if os.path.exists(metalinkfile.filename) and (not force):
        actsize = os.stat(metalinkfile.filename).st_size
        if len(metalinkfile.hashlist) > 0:
            checksum = verify_checksum(metalinkfile.filename, metalinkfile.hashlist)
            if checksum:
                handlers["status"](1, actsize, actsize)
                print ""
                print _("Already downloaded %s.") % os.path.basename(metalinkfile.filename)
                return metalinkfile.filename
            else:
                print _("Checksum failed, retrying download of %s.") % os.path.basename(metalinkfile.filename)
                
        if metalinkfile.size == actsize:
            handlers["status"](1, actsize, actsize)
            print ""
            print _("Already downloaded %s.") % os.path.basename(metalinkfile.filename)
            return metalinkfile.filename

        if os.path.exists(metalinkfile.filename + ".temp"):
            print _("Resuming download of %s.") % os.path.basename(metalinkfile.filename)

    directory = os.path.dirname(metalinkfile.filename)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    if metalinkfile.piecelength == 0:
        metalinkfile.piecelength = DEFAULT_CHUNK_SIZE

    print _("Downloading to %s.") % metalinkfile.filename
        
    seg_result = False
    if segmented:
        manager = Segment_Manager(metalinkfile, headers)
        manager.set_callbacks(handlers)
        seg_result = manager.run()
        
        if not seg_result:
            #seg_result = verify_checksum(local_file, checksums)
            print "\n" + _("Could not download all segments of the file, trying one mirror at a time.")

    if (not segmented) or (not seg_result):
        manager = NormalManager(metalinkfile, headers)
        manager.set_callbacks(handlers)
        manager.run()
        
    if manager.get_status():
        return metalinkfile.filename
    return False
            
class Manager:
    def __init__(self):
        self.cancel_handler = None
        self.pause_handler = None
        self.status_handler = None
        self.bitrate_handler = None
        self.time_handler = None
        self.status = True
        self.size = -1
        self.end_bitrate()

    def set_time_callback(self, handler):
        self.time_handler = handler        
        
    def set_cancel_callback(self, handler):
        self.cancel_handler = handler
        
    def set_pause_callback(self, handler):
        self.pause_handler = handler
        
    def set_status_callback(self, handler):
        self.status_handler = handler

    def set_bitrate_callback(self, handler):
        self.bitrate_handler = handler

    def set_callbacks(self, callbackdict):
        for key in callbackdict.keys():
            setattr(self, key + "_handler", callbackdict[key])

    def run(self, wait=None):
        result = self.status
        while result:
            if self.pause_handler != None and self.pause_handler():
                self.end_bitrate()
                time.sleep(1)
            else:
                if wait != None:
                    time.sleep(wait)
                result = self.cycle()
            
        return self.get_status()
        
    def cycle(self):
        pass
         
    def get_status(self):
        return self.status
    
    def close_handler(self):
        return

    def start_bitrate(self, bytes):
        '''
        Pass in current byte count
        '''
        self.oldsize = bytes
        self.oldtime = time.time()

    def end_bitrate(self):
        self.oldsize = 0
        self.oldtime = None
        
    def get_bitrate(self, bytes):
        '''
        Pass in current byte count
        '''
        if self.oldtime != None and (time.time() - self.oldtime) != 0:
            return ((bytes - self.oldsize) * 8 / 1024)/(time.time() - self.oldtime)
        return 0
        
    def get_time(self, bytes):
        bitrate = self.get_bitrate(bytes)
        if bitrate == 0 or (self.size - bytes) < 0:
            return "??:??"
        
        secondsleft = (self.size - bytes)/(bitrate*1024/8)
        hours = secondsleft / 3600
        minutes = (secondsleft % 3600) / 60
        seconds = (secondsleft % 60)
        if int(hours) > 0:
            return "%.2d:%.2d:%.2d" % (hours, minutes, seconds)
        return "%.2d:%.2d" % (minutes, seconds)
        
class NormalManager(Manager):
    def __init__(self, metalinkfile, headers = {}):
        Manager.__init__(self)
        self.local_file = metalinkfile.filename
        self.size = metalinkfile.size
        self.chunksums = metalinkfile.get_piece_dict()
        self.checksums = metalinkfile.hashlist
        self.urllist = start_sort(metalinkfile.get_url_dict())
        self.start_number = 0
        self.number = 0
        self.count = 1
        self.headers = headers.copy()

    def random_start(self):
        # do it the old way
        # choose a random url tag to start with
        #urllist = list(urllist)
        #number = int(random.random() * len(urllist))
        self.start_number = int(random.random() * len(self.urllist))
        self.number = self.start_number
        
    def cycle(self):
        if self.cancel_handler != None and self.cancel_handler():
            return False
        try:
            self.status = True
            remote_file = complete_url(self.urllist[self.number])

            manager = URLManager(remote_file, self.local_file, self.checksums, self.headers)
            manager.set_status_callback(self.status_handler)
            manager.set_cancel_callback(self.cancel_handler)
            manager.set_pause_callback(self.pause_handler)
            manager.set_bitrate_callback(self.bitrate_handler)
            manager.set_time_callback(self.time_handler)
            self.get_bitrate = manager.get_bitrate
            self.status = manager.run()

            self.number = (self.number + 1) % len(self.urllist)
            self.count += 1
            
            return self.count <= len(self.urllist)
        except KeyboardInterrupt:
            print "Download Interrupted!"
            try:
                manager.close_handler()
            except: pass
            return False
    
class URLManager(Manager):
    def __init__(self, remote_file, filename, checksums = {}, headers = {}):
        '''
        modernized replacement for urllib.urlretrieve() for use with proxy
        '''
        Manager.__init__(self)
        self.filename = filename
        self.checksums = checksums
        self.block_size = 1024
        self.counter = 0
        self.total = 0

    ### FIXME need to check contents from previous download here
        self.resume = FileResume(filename + ".temp")
        self.resume.add_block(0)
    
        self.data = ThreadSafeFile(filename, 'wb+')
        
        try:
            self.temp = urlopen(remote_file, headers = headers)
        except:
            self.status = False
            self.close_handler()
            return
        myheaders = self.temp.info()

        try:
            self.size = int(myheaders['Content-Length'])
        except KeyError:
            self.size = 0

        self.streamserver = None
        if PORT != None:
            self.streamserver = StreamServer((HOST, PORT), StreamRequest)
            self.streamserver.set_stream(self.data)
        
            #thread.start_new_thread(self.streamserver.serve, ())
            mythread = threading.Thread(target=self.streamserver.serve)
            mythread.start()
 
    def close_handler(self):
        self.resume.complete()
        try:
            if PORT == None:
                self.data.close()
            self.temp.close()
        except: pass
        
        if self.status:
            self.status = filecheck(self.filename, self.checksums, self.size)
            
    def cycle(self):
        if self.oldtime == None:
            self.start_bitrate(self.counter * self.block_size)
        if self.cancel_handler != None and self.cancel_handler():
            self.close_handler()
            return False
        
        block = self.temp.read(self.block_size)
        self.data.acquire()
        self.data.write(block)
        self.data.release()
        self.counter += 1
        self.total += len(block)

        self.resume.set_block_size(self.counter * self.block_size)

        if self.streamserver != None:        
            self.streamserver.set_length(self.counter * self.block_size)
                        
        if self.status_handler != None:
            self.status_handler(self.total, 1, self.size)

        if self.bitrate_handler != None:
            self.bitrate_handler(self.get_bitrate(self.counter * self.block_size))

        if self.time_handler != None:
            self.time_handler(self.get_time(self.counter * self.block_size))    
            
        if not block:
            self.close_handler()

        #print self.get_bitrate(self.counter * self.block_size)
        return bool(block)
    
def filecheck(local_file, checksums, size, handler = None):
    if verify_checksum(local_file, checksums):
        actsize = 0
        try:
            actsize = os.stat(local_file).st_size
        except: pass
            
        if handler != None:
            tempsize = size
            if size == 0:
                tempsize = actsize
            handler(1, actsize, tempsize)

        if (int(actsize) == int(size) or size == 0):
            return True
    
    print "\n" + _("Checksum failed for %s.") % os.path.basename(local_file)
    return False
    
def parse_metalink(src, headers = {}, nocheck = False, ver=3):
    src = complete_url(src)
    is_metalink = nocheck
    
    # not all servers support HEAD where GET is also supported
    # also a WindowsError is thrown if a local file does not exist
    if src.endswith(".metalink") or src.endswith(".meta4"):
        is_metalink = True
    try:
        # add head check for metalink type, if MIME_TYPE or application/xml? treat as metalink
        myheaders = urlhead(src, metalink_header=True, headers = headers)
        if myheaders["content-type"].startswith(MIME_TYPE):
            print _("Metalink content-type detected.")
            is_metalink = True
        elif myheaders["link"]:
            # Metalink HTTP Link headers implementation
            # does not check for describedby urls but we can't use any of those anyway
            # TODO this should be more robust and ignore commas in <> for urls
            links = myheaders['link'].split(",")
            fileobj = metalink.MetalinkFile4(os.path.basename(src))
            fileobj.set_size(myheaders["content-length"])
            for link in links:
                parts = link.split(";")
                mydict = {}
                for part in parts[1:]:
                    part1, part2 = part.split("=", 1)
                    mydict[part1.strip()] = part2.strip()
                
                pri = ""
                try:
                    pri = mydict["pri"]
                except KeyError: pass
                typestr = ""
                try:
                    typestr = mydict["type"]
                except KeyError: pass
                try:
                    if mydict['rel'] == '"describedby"' and type=="application/metalink4+xml":
                        # TODO support metalink describedby type
                        #fileobj.add_url(parts[0].strip(" <>"), preference=pri)
                        pass
                    elif mydict['rel'] == '"describedby"' and type=="application/pgp-signature":
                        # support openpgp describedby type
                        fp = urlopen(parts[0].strip(" <>"), headers = {"referer": src})
                        fileobj.hashlist['pgp'] = fp.read()
                        fp.close()
                    elif mydict['rel'] == '"describedby"' or mydict['rel'] == '"duplicate"':
                        fileobj.add_url(parts[0].strip(" <>"), type=typestr, priority=pri)
                except KeyError: pass
            try:
                hashes = myheaders['digest'].split(",")
                for myhash in hashes:
                    parts = myhash.split("=", 1)
                    if parts[0].strip() == 'sha':
                        fileobj.hashlist['sha-1'] = binascii.hexlify(binascii.a2b_base64(parts[1].strip()))
                    else:
                        fileobj.hashlist[parts[0].strip()] = binascii.hexlify(binascii.a2b_base64(parts[1].strip()))
            except KeyError: pass
            print _("Using Metalink HTTP Link headers.")
            mobj = metalink.Metalink4()
            mobj.files.append(fileobj)
            return metalink.convert(mobj, ver)
    except KeyError:
        pass
    
    if not is_metalink:
        return False
        
    try:
        datasource = urlopen(src, metalink_header=True, headers = headers)
    except:
        return False

    metalinkobj = metalink.parsehandle(datasource, ver)
    datasource.close()
    return metalinkobj

def parse_rss(src, headers = {}):
    src = complete_url(src)

    try:
        datasource = urlopen(src, headers = headers)
    except:
        return False

    rssobj = metalink.RSSAtom()
    rssobj.parsehandle(datasource)
    datasource.close()
    return rssobj    
    
def download_rss(src, path, force = False, handlers = {}, segmented = SEGMENTED, headers = {}, nocheck = False):
    rssobj = parse_rss(src, headers)
    if not rssobj:
        return False
        
    urllist = rssobj.files
    if len(urllist) == 0:
        print _("No enclosures to download files from.")
        return False

    results = []
    for rssitem in urllist:
        result = download_file(rssitem.url, os.path.join(path, os.path.basename(rssitem.url)), rssitem.size, force=force, handlers=handlers, segmented=segmented)
        if result:
            results.append(result)
            
    if len(results) == 0:
        return False
    
    return results
    
def download_metalink(src, path, force = False, handlers = {}, segmented = SEGMENTED, headers = {}, nocheck = False):
    '''
    Decode a metalink file, can be local or remote
    First parameter, file to download, URL, file path or Metalink object to download from
    Second parameter, file path to save to
    Third parameter, optional, force a new download even if a valid copy already exists
    Fouth parameter, optional, progress handler callback
    Returns list of file paths if download(s) is successful
    Returns False otherwise (checksum fails)
    '''
    myheaders = headers.copy()

    metalinkobj = parse_metalink(src, myheaders, nocheck)
    if not metalinkobj:
        return False
        
    if is_remote(src):
        myheaders['referer'] = src

    if metalinkobj.type == "dynamic":
        origin = metalinkobj.origin
        if origin != src and origin != "":
            print _("Downloading update from %s") % origin
            try:
                return download_metalink(origin, path, force, handlers, segmented, myheaders)
            except: pass

    urllist = metalinkobj.files
    if len(urllist) == 0:
        print _("No urls to download file from.")
        return False

    results = []
    for filenode in urllist:
        ostag = filenode.os
        langtag = filenode.language

        if OS == None or len(ostag) == 0 or ostag[0].lower() == OS.lower():
            if "any" in LANG or len(langtag) == 0 or langtag.lower() in LANG:
                result = download_file_node(filenode, path, force, handlers, segmented, myheaders)
                if result:
                    results.append(result)
    if len(results) == 0:
        return False
    
    return results


def download_jigdo(src, path, force = False, handlers = {}, segmented = SEGMENTED, headers = {}):
    '''
    Decode a jigdo file, can be local or remote
    First parameter, file to download, URL or file path to download from
    Second parameter, file path to save to
    Third parameter, optional, force a new download even if a valid copy already exists
    Fouth parameter, optional, progress handler callback
    Returns list of file paths if download(s) is successful
    Returns False otherwise (checksum fails)
    '''
    newsrc = complete_url(src)
    try:
        datasource = urlopen(newsrc, metalink_header=True, headers = headers)
    except:
        return False

    jigdo = metalink.Jigdo()
    jigdo.parsehandle(datasource)
    datasource.close()

    #print path_join(src, jigdo.template)
    template = get(path_join(src, jigdo.template), path, {"md5": jigdo.template_md5}, force, handlers, segmented, headers)
    if not template:
        print _("Could not download template file!")
        return False

    urllist = jigdo.files
    if len(urllist) == 0:
        print _("No urls to download file from.")
        return False

    results = []
    results.extend(template)
    for filenode in urllist:
        result = download_file_node(filenode, path, force, handlers, segmented, headers)
        if result:
            results.append(result)
    if len(results) == 0:
        return False

    print _("Reconstituting file...")
    md5 = jigdo.mkiso()
    checksum = verify_checksum(jigdo.filename, {'md5': md5})
    if not checksum:
        print _("Checksum failed.")
    
    return results

def convert_jigdo(src, headers = {}):
    '''
    Decode a jigdo file, can be local or remote
    First parameter, file to download, URL or file path to download from
    Returns metalink xml text, False on error
    '''
    
    newsrc = complete_url(src)
    try:
        datasource = urlopen(newsrc, metalink_header=True, headers = headers)
    except:
        return False

    jigdo = metalink.Jigdo()
    jigdo.parsehandle(datasource)
    datasource.close()

    fileobj = metalink.MetalinkFile(jigdo.template)
    fileobj.add_url(os.path.dirname(src) + "/" + jigdo.template)
    fileobj.add_checksum("md5", jigdo.template_md5)
    jigdo.files.insert(0, fileobj)

    urllist = jigdo.files
    if len(urllist) == 0:
        print _("No Jigdo data files!")
        return False
    
    return jigdo.generate()


def download_file_node(item, path, force = False, handler = None, segmented=SEGMENTED, headers = {}):
    '''
    First parameter, file XML node
    Second parameter, file path to save to
    Third parameter, optional, force a new download even if a valid copy already exists
    Fouth parameter, optional, progress handler callback
    Returns list of file paths if download(s) is successful
    Returns False otherwise (checksum fails)
    raise socket.error e.g. "Operation timed out"
    '''

    urllist = []

    for node in item.resources:
        urllist.append(node.url)
        
    if len(urllist) == 0:
        print _("No urls to download file from.")
        return False

    local_file = item.filename
    item.filename = path_join(path, local_file)

    return download_file_urls(item, force, handler, segmented, headers)

def complete_url(url):
    '''
    If no transport is specified in typical URL form, we assume it is a local
    file, perhaps only a relative path too.
    First parameter, string to convert to URL format
    Returns, string converted to URL format
    '''
    if get_transport(url) == "":
        absfile = os.path.abspath(url)
        if absfile[0] != "/":
            absfile = "/" + absfile
        return "file://" + absfile
    return url

def urlretrieve(url, filename, reporthook = None, headers = {}):
    '''
    modernized replacement for urllib.urlretrieve() for use with proxy
    '''
    block_size = 1024
    i = 0
    counter = 0
    temp = urlopen(url, headers = headers)
    myheaders = temp.info()
    
    try:
        size = int(myheaders['Content-Length'])
    except KeyError:
        size = 0

    data = open(filename, 'wb')
    block = True

    ### FIXME need to check contents from previous download here
    resume = FileResume(filename + ".temp")
    resume.add_block(0)

    while block:
        block = temp.read(block_size)
        data.write(block)
        i += block_size
        counter += 1

        resume.set_block_size(counter * block_size)
                        
        if reporthook != None:
            #print counter, block_size, size
            reporthook(counter, block_size, size)

    resume.complete()
            
    data.close()
    temp.close()

    return (filename, headers)


class FileResume:
    '''
    Manages the resume data file
    '''
    def __init__(self, filename):
        self.size = 0
        self.blocks = []
        self.filename = filename
        self._read()

    def set_block_size(self, size):
        '''
        Set the block size value without recomputing blocks
        '''
        self.size = int(size)
        self._write()

    def update_block_size(self, size):
        '''
        Recompute blocks based on new size
        '''
        if self.size == size:
            return

        newblocks = []
        count = 0
        total = 0
        offset = None
        
        for value in self.blocks:
            value = int(value)
            if value == count:
                if offset == None:
                    offset = count
                total += self.size
            elif offset != None:
                start = ((offset * self.size) / size)
                newblocks.extend(map(str, range(start, start + (total / size))))
                total = 0
                offset = None
            count += 1

        if offset != None:
            start = ((offset * self.size) / size)
            newblocks.extend(map(str, range(start, start + (total / size))))

        self.blocks = newblocks
        self.set_block_size(size)

    def start_byte(self):
        '''
        Returns byte to start at, all previous are OK
        '''
        if len(self.blocks) == 0:
            return 0
        
        count = 0
        for value in self.blocks:
            if int(value) != count:
                return (count + 1) * self.size
            count += 1
            
        return None

    def add_block(self, block_id):
        '''
        Add a block to list of completed
        '''
        if str(block_id) not in self.blocks:
            self.blocks.append(str(block_id))
        self._write()
        
    def remove_block(self, block_id):
        '''
        Remove a block from list of completed
        '''
        self.blocks.remove(str(block_id))
        self._write()
        
    def clear_blocks(self):
        '''
        Remove all blocks from completed list
        '''
        self.blocks = []
        self._write()

    def extend_blocks(self, blocks):
        '''
        Replace the list of block ids
        '''
        for block in blocks:
            if str(block) not in self.blocks:
                self.blocks.append(str(block))
        self._write()

    def _write(self):
        filehandle = open(self.filename, "w")
        filehandle.write("%s:" % str(self.size))
        #for block_id in self.blocks:
            #filehandle.write(str(block_id) + ",")
        #print self.blocks
        filehandle.write(",".join(self.blocks))
        filehandle.close()

    def _read(self):
        try:
            filehandle = open(self.filename, "r")
            resumestr = filehandle.readline()
            (size, blocks) = resumestr.split(":")
            self.blocks = blocks.split(",")
            self.size = int(size)
            filehandle.close()
        except (IOError, ValueError):
            self.blocks = []
            self.size = 0

    def complete(self):
        '''
        Download completed, remove block count file
        '''
        os.remove(self.filename)

def verify_chunk_checksum(chunkstring, checksums={}):
    '''
    Verify the checksum of a file
    First parameter, filename
    Second parameter, optional, expected dictionary of checksums
    Returns True if first checksum provided is valid
    Returns True if no checksums are provided
    Returns False otherwise
    '''

    try:
        checksums["sha512"]
        if hashlib.sha512(chunkstring).hexdigest() == checksums["sha512"].lower():
            return True
        else:
            return False
    except (KeyError, AttributeError): pass
    try:
        checksums["sha384"]
        if hashlib.sha384(chunkstring).hexdigest() == checksums["sha384"].lower():
            return True
        else:
            return False
    except (KeyError, AttributeError): pass
    try:
        checksums["sha256"]
        if hashlib.sha256(chunkstring).hexdigest() == checksums["sha256"].lower():
            return True
        else:
            return False
    except (KeyError, AttributeError): pass
    try:
        checksums["sha1"]
        if hashlib.sha1(chunkstring).hexdigest() == checksums["sha1"].lower():
            return True
        else:
            return False
    except KeyError: pass
    try:
        checksums["md5"]
        if hashlib.md5(chunkstring).hexdigest() == checksums["md5"].lower():
            return True
        else:
            return False
    except KeyError: pass
    
    # No checksum provided, assume OK
    return True

def verify_checksum(local_file, checksums={}):
    '''
    Verify the checksum of a file
    First parameter, filename
    Second parameter, optional, expected dictionary of checksums
    Returns True if first checksum provided is valid
    Returns True if no checksums are provided
    Returns False otherwise
    '''
    
    try:
        return pgp_verify_sig(local_file, checksums["pgp"])
    except (KeyError, AttributeError, ValueError, AssertionError): pass
    try:
        checksums["sha512"]
        if filehash(local_file, hashlib.sha512()) == checksums["sha512"].lower():
            return True
        else:
            #print "\nERROR: sha512 checksum failed for %s." % os.path.basename(local_file)
            return False
    except (KeyError, AttributeError): pass
    try:
        checksums["sha384"]
        if filehash(local_file, hashlib.sha384()) == checksums["sha384"].lower():
            return True
        else:
            #print "\nERROR: sha384 checksum failed for %s." % os.path.basename(local_file)
            return False
    except (KeyError, AttributeError): pass
    try:
        checksums["sha256"]
        if filehash(local_file, hashlib.sha256()) == checksums["sha256"].lower():
            return True
        else:
            #print "\nERROR: sha256 checksum failed for %s." % os.path.basename(local_file)
            return False
    except (KeyError, AttributeError): pass
    try:
        checksums["sha1"]
        if filehash(local_file, hashlib.sha1()) == checksums["sha1"].lower():
            return True
        else:
            #print "\nERROR: sha1 checksum failed for %s." % os.path.basename(local_file)
            return False
    except KeyError: pass
    try:
        checksums["md5"]
        if filehash(local_file, hashlib.md5()) == checksums["md5"].lower():
            return True
        else:
            #print "\nERROR: md5 checksum failed for %s." % os.path.basename(local_file)
            return False
    except KeyError: pass
    
    # No checksum provided, assume OK
    return True

def pgp_verify_sig(filename, sig):
    gpg = GPG.GPGSubprocess(keyring=PGP_KEY_STORE)

    for root, dirs, files in os.walk(PGP_KEY_DIR):
        for thisfile in files:
            if thisfile[-4:] in PGP_KEY_EXTS:
                gpg.import_key(open(thisfile).read())
    
    sign = gpg.verify_file_detached(filename, sig)

    print "\n-----" + _("BEGIN PGP SIGNATURE INFORMATION") + "-----"
    if sign.error != None:
        print sign.error
    else:
        #print sig.creation_date
        try:
            print "" + _("timestamp") + ":", time.strftime("%a, %d %b %Y %H:%M:%S (%Z)", time.localtime(float(sign.timestamp)))
        except TypeError: pass
        print "" + _("fingerprint") + ":", sign.fingerprint
        #print sig.signature_id
        #print sign.key_id
        print "" + _("uid") + ":", sign.username
    print "-----" + _("END PGP SIGNATURE INFORMATION") + "-----\n"

    if sign.error != None:
        raise AssertionError, sign.error
    
    if sign.is_valid():
        return True
    
    return False

def is_remote(name):
    transport = get_transport(name)
        
    if transport != "":
        return True
    return False

def is_local(name):
    transport = get_transport(name)
        
    if transport == "":
        return True
    return False

def get_transport(url):
    '''
    Gets transport type.  This is more accurate than the urlparse module which
    just does a split on colon.
    First parameter, url
    Returns the transport type
    '''
    url = str(url)
    result = url.split("://", 1)
    if len(result) == 1:
        transport = ""
    else:
        transport = result[0]
    return transport

def filehash(thisfile, filesha):
    '''
    First parameter, filename
    Returns SHA1 sum as a string of hex digits
    '''
    try:
        filehandle = open(thisfile, "rb")
    except:
        return ""

    chunksize = 1024*1024
    data = filehandle.read(chunksize)
    while(data != ""):
        filesha.update(data)
        data = filehandle.read(chunksize)

    filehandle.close()
    return filesha.hexdigest()

def path_join(first, second):
    '''
    A function that is called to join two paths, can be URLs or filesystem paths
    Parameters, two paths to be joined
    Returns new URL or filesystem path
    '''
    if first == "":
        return second
    if is_remote(second):
        return second

    if is_remote(first):
        if is_local(second):
            return urlparse.urljoin(first, second)
        return second

    return os.path.normpath(os.path.join(first, second))

def start_sort(urldict):
    urls = copy.deepcopy(urldict)
    localurls = {}
    if COUNTRY != None:
        for url in urls.keys():
            if COUNTRY.lower() == urls[url].location.lower():
                localurls[url] = urls[url]
                urls.pop(url)

    newurls = sort_prefs(localurls)
    newurls.extend(sort_prefs(urls))
    #for i in range(len(newurls)):
    #    print i, newurls[i]
    return newurls

def sort_prefs(mydict):
    newurls = []

    for url in mydict.keys():
        newurls.append((mydict[url].preference, mydict[url].url))

    newurls.sort()
    newurls.reverse()
    
    result = []
    for url in newurls:
        result.append(url[1])
    return result

############# segmented download functions #############

class ThreadSafeFile(file):
    def __init__(self, *args):
        file.__init__(self, *args)
        self.lock = threading.Lock()

    def acquire(self):
        return self.lock.acquire()
    
    def release(self):
        return self.lock.release()
    
class Segment_Manager(Manager):
    def __init__(self, metalinkfile, headers = {}):
        Manager.__init__(self)

        self.headers = headers.copy()
        self.sockets = []
        self.chunks = []
        self.limit_per_host = LIMIT_PER_HOST
        self.host_limit = HOST_LIMIT
        #self.size = 0
        #if metalinkfile.size != "":
        self.size = metalinkfile.get_size()
        self.orig_urls = metalinkfile.get_url_dict()
        self.urls = self.orig_urls
        self.chunk_size = int(metalinkfile.piecelength)
        self.chunksums = metalinkfile.get_piece_dict()
        self.checksums = metalinkfile.hashlist
        self.localfile = metalinkfile.filename
        self.filter_urls()
        
        self.status = True
        
        # Open the file.
        try:
            self.f = ThreadSafeFile(self.localfile, "rb+")
        except IOError:
            self.f = ThreadSafeFile(self.localfile, "wb+")
            
        self.resume = FileResume(self.localfile + ".temp")

        self.streamserver = None
        if PORT != None:
            self.streamserver = StreamServer((HOST, PORT), StreamRequest)
            self.streamserver.set_stream(self.f)
        
            #thread.start_new_thread(self.streamserver.serve, ())
            mythread = threading.Thread(target=self.streamserver.serve)
            mythread.start()

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
        
        raise socket.error e.g. "Operation timed out"
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
                size = None
                while (status == httplib.MOVED_PERMANENTLY or status == httplib.FOUND) and count < MAX_REDIRECTS:
                    http = Http_Host(url)
                    if http.conn != None: 
                        try:
                            http.conn.request("HEAD", url, headers = self.headers)
                            response = http.conn.getresponse()
                            status = response.status
                            url = response.getheader("Location")
                            size = response.getheader("content-length")
                        except: pass
                        http.close()
                    count += 1

                if (status == httplib.OK) and (size != None):
                    sizes.append(size)

            elif protocol == "ftp":
                ftp = Ftp_Host(url)
                size = ftp.conn.size(url)
                if size != None:
                    sizes.append(size)
                
            i += 1

        if len(sizes) == 0:
            return None
        if len(sizes) == 1:
            return int(sizes[0])
        if sizes.count(sizes[0]) >= 2:
            return int(sizes[0])
        if sizes.count(sizes[1]) >= 2:
            return int(sizes[1])
        
        return None
    
    def filter_urls(self):
        #print self.urls
        newurls = {}
        for item in self.urls.keys():
            if (not item.endswith(".torrent")) and (get_transport(item) in PROTOCOLS):
                newurls[item] = self.urls[item]
        self.urls = newurls
        return newurls
            
    def run(self, wait=0.1):
        '''
        ?
        '''
        #try:
        if self.size == "" or self.size == 0:
            self.size = self.get_size()
            if self.size == None:
                #crap out and do it the old way
                self.close_handler()
                self.status = False
                return False

        # can't adjust chunk size if it has chunk hashes tied to that size
        if len(self.chunksums) == 0 and self.size/self.chunk_size > MAX_CHUNKS:
            self.chunk_size = self.size/MAX_CHUNKS
            #print "Set chunk size to %s." % self.chunk_size
        self.resume.update_block_size(self.chunk_size)
            
        return Manager.run(self, wait)

    def cycle(self):
        '''
        Runs one cycle
        Returns True if still downloading, False otherwise
        '''
        try:
            bytes = self.byte_total()

            index = self.get_chunk_index()
            if index != None and index > 0 and self.streamserver != None:
                self.streamserver.set_length((index - 1) * self.chunk_size)
            
            if self.oldtime == None:
                self.start_bitrate(bytes)
                
            # cancel was pressed here
            if self.cancel_handler != None and self.cancel_handler():
                self.status = False
                self.close_handler()
                return False
            
            self.update()
            self.resume.extend_blocks(self.chunk_list())

            if bytes >= self.size and self.active_count() == 0:
                self.resume.complete()
                self.close_handler()
                return False
            
            #crap out and do it the old way
            if len(self.urls) == 0:
                self.status = False
                self.close_handler()
                return False
            
            return True
        
        except KeyboardInterrupt:
            print "Download Interrupted!"
            self.close_handler()
            return False
            

    def update(self):
        if self.status_handler != None and self.size != None:
            #count = int(self.byte_total()/self.chunk_size)
            #if self.byte_total() % self.chunk_size:
            #    count += 1
            #self.status_handler(count, self.chunk_size, self.size)
            self.status_handler(self.byte_total(), 1, self.size)    
        if self.bitrate_handler != None:
            self.bitrate_handler(self.get_bitrate(self.byte_total()))
        if self.time_handler != None:
            self.time_handler(self.get_time(self.byte_total()))
            
        next = self.next_url()
        
        if next == None:
            return
        
        index = self.get_chunk_index()
        if index != None:
            start = index * self.chunk_size
            end = start + self.chunk_size
            if end > self.size:
                end = self.size

            if next.protocol == "http" or next.protocol == "https":
                segment = Http_Host_Segment(next, start, end, self.size, self.get_chunksum(index), self.headers)
                segment.set_cancel_callback(self.cancel_handler)
                self.chunks[index] = segment
                self.segment_init(index)
            if next.protocol == "ftp":
                #print "allocated to:", index, next.url
                segment = Ftp_Host_Segment(next, start, end, self.size, self.get_chunksum(index))
                segment.set_cancel_callback(self.cancel_handler)
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
            if (self.chunks[i] == None or self.chunks[i].error != None):
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
            if item != None and item.error != None:
                #print item.error
                if item.error == httplib.MOVED_PERMANENTLY or item.error == httplib.FOUND:
                    #print "location:", item.location
                    try:
                        newitem = copy.deepcopy(self.urls[item.url])
                        newitem.url = item.location
                        self.urls[item.location] = newitem
                    except KeyError: pass
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
        if PORT == None:
            self.f.close()
        for host in self.sockets:
            host.close()

        self.update()

        #try:
        size = int(os.stat(self.localfile).st_size)
        if size == 0:
            try:
                os.remove(self.localfile)
                os.remove(self.localfile + ".temp")
            except: pass
            self.status = False
        elif self.status:
            self.status = filecheck(self.localfile, self.checksums, size)
        #except: pass

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
            self.error = _("unsupported protocol")
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
            self.error = _("unsupported protocol")
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
                self.error = _("invalid url")
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
                self.error = _("invalid url")
                return
        else:
            self.error = _("unsupported protocol")
            return
        
    def close(self):
        if self.conn != None:
            self.conn.close()

class Host_Segment:
    '''
    Base class for various segment protocol types.  Not to be used directly.
    '''
    def __init__(self, host, start, end, filesize, checksums = {}, headers = {}):
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
        self.cancel_handler = None
        self.headers = headers.copy()
        
    def set_cancel_callback(self, handler):
        self.cancel_handler = handler

    def check_cancel(self):
        if self.cancel_handler == None:
            return False
        return self.cancel_handler()
        
    def avg_bitrate(self):
        bits = self.bytes * 8
        return bits/self.ttime

    def checksum(self):
        if self.check_cancel():
            return False
        
        try:
            self.mem.acquire()
            self.mem.seek(self.byte_start, 0)
            chunkstring = self.mem.read(self.byte_count)
            self.mem.release()
        except ValueError:
            return False

        return verify_chunk_checksum(chunkstring, self.checksums)

    def close(self):
        if self.error != None:
            self.host.close()

        self.host.set_active(False)

    def end(self):
        if self.error == None and not self.checksum():
            self.error = _("Chunk checksum failed")
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
            self.error = _("bad socket")
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
                self.error = _("EOFError")
                self.close()
                return
            except AttributeError:
                self.error = _("AttributeError")
                self.close()
                return
            except (socket.error), error:
                #print "reconnect", self.host.url
                try:
                    self.host.reconnect()
                except:
                    pass
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
                self.error = _("socket reconnect attempts failed")
                self.close()
                return
    
        if size != None:
            if self.filesize != size:
                self.error = _("bad file size")
                return
        
        self.start_time = time.time()
        while True:
            if self.readable():
                self.handle_read()
                self.ttime += (time.time() - self.start_time)
            else:
                self.end()
                return

    def readable(self):
        if self.check_cancel():
            return False

        if self.response == None:
            return False
        return True
    
    def handle_read(self):
        try:
            data = self.response.recv(1024)
        except socket.timeout:
            self.error = _("read timeout")
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

            try:
                self.mem.acquire()
                self.mem.seek(self.byte_start, 0)
                self.mem.write(tempbuffer)
                self.mem.flush()
                self.mem.release()
            except ValueError:
                self.error = _("bad file handle")            
        
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
##            self.mem.acquire()
##            self.mem.seek(self.byte_start + self.bytes, 0)
##            self.mem.write(writedata)
##            self.mem.flush()
##            
##            self.mem.release()
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
        #try:
            # Finish early if checksum is OK
            if self.checksum() and len(self.checksums) > 0:
                self.bytes += self.byte_count
                self.close()
                return
            
            if self.host.conn == None:
                self.error = _("bad socket")
                self.close()
                return
    
            try:
                self.headers.update({"Range": "bytes=%lu-%lu\r\n" % (self.byte_start, self.byte_end - 1)})
                self.host.conn.request("GET", self.url, "", self.headers)
            except:
                self.error = _("socket exception")
                self.close()
                return
            
            self.start_time = time.time()
            while True:
                if self.readable():
                    self.handle_read()
                    self.ttime += (time.time() - self.start_time)
                else:
                    self.end()
                    return
        #except BaseException, e:
        #    self.error = utils.get_exception_message(e)

    def readable(self):
        if self.check_cancel():
            return False

        if self.response == None:
            try:
                self.response = self.host.conn.getresponse()
            except socket.timeout:
                self.error = _("timeout")
                return False
            # not an error state, connection closed, kicks us out of thread
            except httplib.ResponseNotReady:
                return False
            except:
                self.error = _("response error")
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
            self.error = _("timeout")
            self.response = None
            return
        except httplib.IncompleteRead:
            self.error = _("incomplete read")
            self.response = None
            return
        except socket.error:
            self.error = _("socket error")
            self.response = None
            return
        except TypeError:
            self.response = None
            return

        if len(data) == 0:
            return

        rangestring = self.response.getheader("Content-Range")
        request_size = int(rangestring.split("/")[1])

        if request_size != self.filesize:
            self.error = _("bad file size")
            self.response = None
            return

        body = data
        size = len(body)
        
        # write out body to file
        try:
            self.mem.acquire()
            self.mem.seek(self.byte_start + self.bytes, 0)
            self.mem.write(body)
            self.mem.flush()
            self.mem.release()
        except ValueError:
            self.error = _("bad file handle")
            self.response = None
            return

        self.bytes += size
        #print self.bytes, self.byte_count
        if self.bytes >= self.byte_count:
            self.response = None

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
            if url.scheme == "" or url.scheme == "http": 
                host = url.hostname 
                port = url.port 
                if url.username != None: 
                    self.headers["Proxy-authorization"] = "Basic " + base64.encodestring(url.username+':'+url.password) + "\r\n"
                self.conn = httplib.HTTPConnection(host, port)
            else:
                raise AssertionError, _("Transport not supported for FTP_PROXY, %s") % url.scheme

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
        if FTP_PROXY == "":
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
                raise AssertionError, _("Transport not supported for HTTP_PROXY, %s") % url.scheme

        self.conn = httplib.HTTPConnection(host, port)

    def request(self, method, url, body="", headers={}):
        '''
        raise socket.error e.g. "Operation timed out"
        '''
        myheaders = headers.copy()
        myheaders.update(self.headers)

        #print "HTTP REQUEST:", headers
        if HTTP_PROXY == "":
            urlparts = urlparse.urlsplit(url)
            url = urlparts.path + "?" + urlparts.query
        return self.conn.request(method, url, body, myheaders)

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
        myheaders = headers.copy()
        myheaders.update(self.headers)
        urlparts = urlparse.urlsplit(url)
        if HTTPS_PROXY != "":
            port = httplib.HTTPS_PORT
            if urlparts.port != None:
                port = urlparts.port
            return self.conn.request("CONNECT", urlparts.hostname + ":" + port, body, myheaders)
        else:
            url = urlparts.path + "?" + urlparts.query
            return self.conn.request("GET", url, body, myheaders)

    def getresponse(self):
        return self.conn.getresponse()

    def close(self):
        return self.conn.close()

class StreamRequest(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        start = 0
        while True:
            if self.server.fileobj != None and (self.server.length - start) > 0:
                try:
                    self.server.fileobj.acquire()
                    loc = self.server.fileobj.tell()
                    self.server.fileobj.seek(start, 0)
                    size = self.server.length - start
                    
                    data = self.server.fileobj.read(size)
                    if len(data) > 0:
                        self.wfile.write(data)

                    self.server.fileobj.seek(loc, 0)
                    self.server.fileobj.release()
                    start += len(data)
                except ValueError:
                    break
            time.sleep(.1)

class StreamServer(BaseHTTPServer.HTTPServer):
    def __init__(self, *args):
        BaseHTTPServer.HTTPServer.__init__(self, *args)
        self.fileobj = None
        self.length = 0

    # based on: http://code.activestate.com/recipes/425210/
    def server_bind(self):
        BaseHTTPServer.HTTPServer.server_bind(self)
        self.socket.setblocking(0)
        self.socket.settimeout(1)
        self.run = True

    def get_request(self):
        while self.run:
            try:
                sock, addr = self.socket.accept()
                sock.setblocking(0)
                sock.settimeout(30)
                return (sock, addr)
            except socket.timeout:
                pass

    def stop(self):
        self.run = False

    def serve(self):
        try:
            while self.run:
                self.handle_request()
        except KeyboardInterrupt:
            print "Server Interrupted!"
            self.fileobj.close()
            self.stop()
        
    def set_stream(self, fileobj):
        self.fileobj = fileobj

    def set_length(self, length):
        self.length = int(length)

##myserver = StreamServer(("localhost", 8080), StreamRequest)
##myserver.set_stream(ThreadSafeFile("C:\\library\\avril\\Avril Lavigne - Complicated.mpg", "rb"))
##myserver.set_length(50000000)
##serverthread = threading.Thread(target=myserver.serve_forever)
##serverthread.start()

#myserver.serve_forever()
download = Dummy()
download.CONNECT_RETRY_COUNT = CONNECT_RETRY_COUNT
download.COUNTRY = COUNTRY
download.DEFAULT_CHUNK_SIZE = DEFAULT_CHUNK_SIZE
download.FTP = FTP
download.FTP_PROXY = FTP_PROXY
download.FileResume = FileResume
download.Ftp_Host = Ftp_Host
download.Ftp_Host_Segment = Ftp_Host_Segment
download.HOST = HOST
download.HOST_LIMIT = HOST_LIMIT
download.HTTPConnection = HTTPConnection
download.HTTPSConnection = HTTPSConnection
download.HTTPS_PROXY = HTTPS_PROXY
download.HTTP_PROXY = HTTP_PROXY
download.Host_Base = Host_Base
download.Host_Segment = Host_Segment
download.Http_Host = Http_Host
download.Http_Host_Segment = Http_Host_Segment
download.LANG = LANG
download.LIMIT_PER_HOST = LIMIT_PER_HOST
download.MAX_CHUNKS = MAX_CHUNKS
download.MAX_REDIRECTS = MAX_REDIRECTS
download.MIME_TYPE = MIME_TYPE
download.Manager = Manager
download.NormalManager = NormalManager
download.OS = OS
download.PGP_KEY_DIR = PGP_KEY_DIR
download.PGP_KEY_EXTS = PGP_KEY_EXTS
download.PGP_KEY_STORE = PGP_KEY_STORE
download.PORT = PORT
download.PROTOCOLS = PROTOCOLS
download.SEGMENTED = SEGMENTED
download.SOCKS_PROXY = SOCKS_PROXY
download.Segment_Manager = Segment_Manager
download.StreamRequest = StreamRequest
download.StreamServer = StreamServer
download.ThreadSafeFile = ThreadSafeFile
download.URLManager = URLManager
download.USER_AGENT = USER_AGENT
download._ = _
download.complete_url = complete_url
download.convert_jigdo = convert_jigdo
download.download_file = download_file
download.download_file_node = download_file_node
download.download_file_urls = download_file_urls
download.download_jigdo = download_jigdo
download.download_metalink = download_metalink
download.download_rss = download_rss
download.filecheck = filecheck
download.filehash = filehash
download.get = get
download.get_key_value = get_key_value
download.get_proxy_info = get_proxy_info
download.get_transport = get_transport
download.is_local = is_local
download.is_remote = is_remote
download.lang = lang
download.parse_metalink = parse_metalink
download.parse_rss = parse_rss
download.path_join = path_join
download.pgp_verify_sig = pgp_verify_sig
download.reg_query = reg_query
download.set_proxies = set_proxies
download.sort_prefs = sort_prefs
download.start_sort = start_sort
download.translate = translate
download.urlhead = urlhead
download.urlopen = urlopen
download.urlretrieve = urlretrieve
download.verify_checksum = verify_checksum
download.verify_chunk_checksum = verify_chunk_checksum
# -*- coding: utf-8 -*-
'''
From sourceforge pycrypto project:
http://sourceforge.net/projects/pycrypto/

Code for running GnuPG from Python and dealing with the results.

Detailed info about the format of data to/from gpg may be obtained from the
file DETAILS in the gnupg source.

Dependencies
   - GPG must be installed
   - http://www.gnupg.org
   - http://www.gpg4win.org
'''

__rcsid__ = '$Id: GPG.py,v 1.3 2003/11/23 15:03:15 akuchling Exp $'



def translate():
    '''
    Setup translation path
    '''
    if __name__=="__main__":
        try:
            base = os.path.basename(__file__)[:-3]
            localedir = os.path.join(os.path.dirname(__file__), "locale")
        except NameError:
            base = os.path.basename(sys.executable)[:-4]
            localedir = os.path.join(os.path.dirname(sys.executable), "locale")
    else:
        temp = __name__.split(".")
        base = temp[-1]
        localedir = os.path.join("/".join(["%s" % k for k in temp[:-1]]), "locale")

    #print base, localedir, locale.getdefaultlocale()
    localelang = locale.getdefaultlocale()[0]
    if localelang == None:
        localelang = "LC_ALL"
    t = gettext.translation(base, localedir, [localelang], None, 'en')
    return t.ugettext

_ = translate()

# Default path used for searching for the GPG binary
DEFAULT_PATH = ['/bin', '/usr/bin', '/usr/local/bin', \
                    '${PROGRAMFILES}\\GNU\\GnuPG', '${PROGRAMFILES(X86)}\\GNU\\GnuPG', 'GPG', \
                    '${SYSTEMDRIVE}\\cygwin\\bin', '${SYSTEMDRIVE}\\cygwin\\usr\\bin', '${SYSTEMDRIVE}\\cygwin\\usr\\local\\bin']

class Signature:
    '''
    Used to hold information about a signature result
    '''

    def __init__(self):
        self.valid = 0
        self.fingerprint = self.creation_date = self.timestamp = None
        self.signature_id = self.key_id = None
        self.username = None
        self.error = None
        self.nopubkey = False

    def BADSIG(self, value):
        self.error = "BADSIG"
        self.valid = 0
        self.key_id, self.username = value.split(None, 1)
    def GOODSIG(self, value):
        self.valid = 1
        #self.error = "GOODSIG"
        self.key_id, self.username = value.split(None, 1)
    def VALIDSIG(self, value):
        #print value
        #self.valid = 1
        #self.error = "VALID_SIG"
        self.fingerprint, self.creation_date, self.timestamp, other = value.split(" ", 3)
    def SIG_ID(self, value):
        #self.error = "SIG_ID"
        self.signature_id, self.creation_date, self.timestamp = value.split(" ", 2)
    def NODATA(self, value):
        self.error = _("File not properly loaded for signature.")
    def ERRSIG(self, value):
        #print value
        self.error = _("Signature error.")
    def NO_PUBKEY(self, value):
        self.key_id = value
        self.nopubkey = True
        self.error = _("Signature error, missing public key with id 0x%s.") % value[-8:]

    def KEYEXPIRED(self, value):
        self.error = _("Signature error, signing key expired at %s.") % value

    def SIGEXPIRED(self, value):
        return self.KEYEXPIRED(value)

    def EXPKEYSIG(self, value):
        # value is the name of the expired key
        self.error = _("Signature error, valid but key expired, %s") % value
        
    def TRUST_ULTIMATE(self, value):
        '''
        see http://cvs.gnupg.org/cgi-bin/viewcvs.cgi/trunk/doc/DETAILS?rev=289
        Trust settings do NOT determine if a signature is good or not!  That is reserved for GOOD_SIG!
        '''
        return
        
    def TRUST_UNDEFINED(self, value):
        self.error = _("Trust undefined")
        #print value.split()
        #raise AssertionError, "File not properly loaded for signature."
    
    def is_valid(self):
        '''
        returns boolean result of signature valididity
        '''
        return self.valid
 
class ImportResult:
    '''
    Used to hold information about a key import result
    '''

    counts = '''count no_user_id imported imported_rsa unchanged
            n_uids n_subk n_sigs n_revoc sec_read sec_imported
            sec_dups not_imported'''.split()
    def __init__(self):
        self.imported = []
        self.results = []
        for result in self.counts:
            setattr(self, result, None)
    
    def NODATA(self, value):
        self.results.append({'fingerprint': None,
            'problem': '0', 'text': 'No valid data found'})
    def IMPORTED(self, value):
        # this duplicates info we already see in import_ok and import_problem
        pass
    ok_reason = {
        '0': 'Not actually changed',
        '1': 'Entirely new key',
        '2': 'New user IDs',
        '4': 'New signatures',
        '8': 'New subkeys',
        '16': 'Contains private key',
    }
    def IMPORT_OK(self, value):
        reason, fingerprint = value.split()
        self.results.append({'fingerprint': fingerprint,
            'ok': reason, 'text': self.ok_reason[reason]})
    problem_reason = {
        '0': 'No specific reason given',
        '1': 'Invalid Certificate',
        '2': 'Issuer Certificate missing',
        '3': 'Certificate Chain too long',
        '4': 'Error storing certificate',
    }
    def IMPORT_PROBLEM(self, value):
        try:
            reason, fingerprint = value.split()
        except:
            reason = value
            fingerprint = '<unknown>'
        self.results.append({'fingerprint': fingerprint,
            'problem': reason, 'text': self.problem_reason[reason]})
    def IMPORT_RES(self, value):
        import_res = value.split()
        for i in range(len(self.counts)):
            setattr(self, self.counts[i], int(import_res[i]))
			
    def KEYEXPIRED(self, value):
        self.error = _("Signature error, signing key expired at %s.") % value

    def summary(self):
        l = []
        l.append('%d imported'%self.imported)
        if self.not_imported:
            l.append('%d not imported'%self.not_imported)
        return ', '.join(l)

class ListResult:
    ''' Parse a --list-keys output

        Handle pub and uid (relating the latter to the former).

        Don't care about (info from src/DETAILS):

        crt = X.509 certificate
        crs = X.509 certificate and private key available
        sub = subkey (secondary key)
        sec = secret key
        ssb = secret subkey (secondary key)
        uat = user attribute (same as user id except for field 10).
        sig = signature
        rev = revocation signature
        fpr = fingerprint: (fingerprint is in field 10)
        pkd = public key data (special field format, see below)
        grp = reserved for gpgsm
        rvk = revocation key
    '''
    def __init__(self):
        self.pub_keys = []
        self.pk = None

    def pub(self, args):
        keyid = args[4]
        date = args[5]
        uid = args[9]
        self.pk = {'keyid': keyid, 'date': date, 'uids': [uid]}
        self.pub_keys.append(self.pk)

    def uid(self, args):
        self.pk['uids'].append(args[9])

class EncryptedMessage:
    ''' Handle a --encrypt command
    '''
    def __init__(self):
        self.data = ''

    def BEGIN_ENCRYPTION(self, value):
        pass
    def END_ENCRYPTION(self, value):
        pass

class GPGSubprocess:    
    def __init__(self, gpg_binary=None, keyring=None):
        """Initialize an object instance.  Options are:

        gpg_binary -- full pathname for GPG binary.  If not supplied,
        the current value of PATH will be searched, falling back to the
        DEFAULT_PATH class variable if PATH isn't available.

        keyring -- full pathname to the public keyring to use in place of
        the default "~/.gnupg/pubring.gpg".
        """
        # If needed, look for the gpg binary along the path
        if gpg_binary is None or gpg_binary == "":
            path = DEFAULT_PATH
            if os.environ.has_key('PATH'):
                temppath = os.environ['PATH']
                path.extend(temppath.split(os.pathsep))
            #else:
            #    path = self.DEFAULT_PATH

            for pathdir in path:
                pathdir = os.path.expandvars(pathdir)
                fullname = os.path.join(pathdir, 'gpg')
                if os.path.exists(fullname):
                    gpg_binary = fullname
                    break

                if os.path.exists(fullname + ".exe"):
                    gpg_binary = fullname + ".exe"
                    break
            else:
                raise ValueError, (_("Couldn't find 'gpg' binary on path %s.")
                                   % repr(path) )

        self.gpg_binary = "\"" + gpg_binary + "\""
        self.keyring = keyring

    def _open_subprocess(self, *args):
        '''
        Internal method: open a pipe to a GPG subprocess and return
        the file objects for communicating with it.
        '''
        cmd = [self.gpg_binary, '--status-fd 2']
        if self.keyring:
            cmd.append('--keyring "%s" --no-default-keyring'% self.keyring)

        cmd.extend(args)
        cmd = ' '.join(cmd)

        #print cmd
        shell = True
        if os.name == 'nt':
            shell = False

        # From: http://www.py2exe.org/index.cgi/Py2ExeSubprocessInteractions
        creationflags = 0
        try:
            creationflags = win32process.CREATE_NO_WINDOW
        except NameError: pass
            
        process = subprocess.Popen(cmd, shell=shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags = creationflags)
        #child_stdout, child_stdin, child_stderr =  #popen2.popen3(cmd)
        #return child_stdout, child_stdin, child_stderr
        #print process.stderr
        return process.stdout, process.stdin, process.stderr

    def _read_response(self, child_stdout, response):
        '''
        Internal method: reads all the output from GPG, taking notice
        only of lines that begin with the magic [GNUPG:] prefix.
        
        Calls methods on the response object for each valid token found,
        with the arg being the remainder of the status line.
        '''
        while 1:
            line = child_stdout.readline()
            #print line
            if line == "": break
            line = line.rstrip()
            if line[0:9] == '[GNUPG:] ':
                # Chop off the prefix
                line = line[9:]
                L = line.split(None, 1)
                keyword = L[0]
                if len(L) > 1:
                    value = L[1]
                else:
                    value = ""
                getattr(response, keyword)(value)

    def _handle_gigo(self, args, file, result):
        '''
        Handle a basic data call - pass data to GPG, handle the output
        including status information. Garbage In, Garbage Out :)
        '''
        child_stdout, child_stdin, child_stderr = self._open_subprocess(*args)

        # Copy the file to the GPG subprocess
        while 1:
            data = file.read(1024)
            if data == "": break
            child_stdin.write(data)
        child_stdin.close()

        # Get the response information
        self._read_response(child_stderr, result)

        # Read the contents of the file from GPG's stdout
        result.data = ""
        while 1:
            data = child_stdout.read(1024)
            if data == "": break
            result.data = result.data + data

        return result
    

    #
    # SIGNATURE VERIFICATION METHODS
    #
    def verify(self, data):
        '''
        Verify the signature on the contents of the string 'data'
        '''
        fileobj = StringIO.StringIO(data)
        return self.verify_file(fileobj)
    
    def verify_file(self, file):
        '''
        Verify the signature on the contents of the file-like object 'file'
        '''
        sig = Signature()
        self._handle_gigo(['--verify -'], file, sig)
        return sig

    def verify_file_detached(self, filename, sigtext):
        '''
        filename - local name of file to check signature for
        sigtext - text of the PGP signature
        '''
        sig = Signature()
        sigfile = StringIO.StringIO(sigtext)
        self._handle_gigo(["--verify - \"%s\"" % filename], sigfile, sig)
        return sig

    #
    # KEY MANAGEMENT
    #
    def import_key(self, key_data):
        ''' import the key_data into our keyring '''
        child_stdout, child_stdin, child_stderr = \
            self._open_subprocess('--import')

        child_stdin.write(key_data)
        child_stdin.close()

        # Get the response information
        result = ImportResult()
        self._read_response(child_stderr, result)

        return result

    def list_keys(self):
        ''' list the keys currently in the keyring '''
        child_stdout, child_stdin, child_stderr = \
            self._open_subprocess('--list-keys --with-colons')
        child_stdin.close()

        # TODO: there might be some status thingumy here I should handle...

        # Get the response information
        result = ListResult()
        valid_keywords = 'pub uid'.split()
        while 1:
            line = child_stdout.readline()
            if not line:
                break
            L = line.strip().split(':')
            if not L:
                continue
            keyword = L[0]
            if keyword in valid_keywords:
                getattr(result, keyword)(L)

        return result

    #
    # ENCRYPTING DATA
    #
    def encrypt_file(self, file, recipients):
        '''Encrypt the message read from the file-like object "file"'''
        args = ['--encrypt --armor']
        for recipient in recipients:
            args.append('--recipient %s'%recipient)
        result = EncryptedMessage()
        self._handle_gigo(args, file, result)
        return result

    def encrypt(self, data, recipients):
        '''Encrypt the message contained in the string "data"'''
        fileobj = StringIO.StringIO(data)
        return self.encrypt_file(fileobj, recipients)


    # Not yet implemented, because I don't need these methods
    # The methods certainly don't have all the parameters they'd need.
    def sign(self, data):
        '''Sign the contents of the string "data"'''
        pass

    def sign_file(self, file):
        '''Sign the contents of the file-like object "file"'''
        pass

    def decrypt_file(self, file):
        '''Decrypt the message read from the file-like object "file"'''
        pass

    def decrypt(self, data):
        '''Decrypt the message contained in the string "data"'''
        pass

def print_hex(binary_data):
    '''
    takes a binary string as input, prints it as hex bytes
    '''
    for byte in binary_data:
        print "%.2x" % ord(byte),

def decode(filename):
    '''
    Decodes data elements from a given PGP file name.
    '''
    if filename == None:
        return []
    if filename.endswith(".asc"):
        return decode_asc(filename)
    else:
        return decode_sig(filename)

def decode_sig(filename):
    '''
    Decodes data elements from a binary (.sig) PGP file.
    '''
    filehandle = open(filename)
    binstr = filehandle.read()
    filehandle.close()
    return decode_data(binstr)

def decode_asc(filename):
    '''
    Decodes data elements from a base 64 encoded (.asc) PGP file.
    '''
    filehandle = open(filename)
    lines = filehandle.readlines()
    filehandle.close()
    return decode_lines(lines)

def decode_lines(lines):
    '''
    Decodes header from PGP ASCII.
    '''
    text = ""
    add = False
    for line in lines:
        if line.strip().startswith("-----END PGP "):
                add = False
        if add and line.strip() != "":
                text += line
        #if line.strip().startswith("-----BEGIN PGP SIGNATURE-----"):
        if line.strip() == "":
                add = True

    binary_data = base64.standard_b64decode(text)
    return decode_data(binary_data)

def decode_data(binary_data):
    '''
    Decodes data packets from a PGP formatted string.
    '''
    pktlist = GPGFile()
    while len(binary_data) > 3:
        packet = decode_header(binary_data)
        pktlist.append(packet)
        binary_data = binary_data[packet['size']+packet['header_size']:]
        #print len(binary_data)
        
    return pktlist

def decode_header(binary_data):
    '''
    Decodes the header of a PGP formatted string.
    '''
    results = {}

    packet_header = ord(binary_data[0])

    binary_data = binary_data[1:]

    format = (packet_header & 0x40) >> 6

    if format == 1:
        # new format packet
        #print "not implemented, new packet format"
        results["content_tag"] = packet_header & 0x1F
        results["format"] = "New"

        #print "new", len(binary_data)
        #results['header_size'] = 0
        octet1 = ord(binary_data[0])
        if octet1 < 192:
            results['size'] = ord(binary_data[0])
            binary_data = binary_data[1:]
        elif 192 <= octet1 <= 223:
            results['size'] = ((ord(binary_data[0]) - 192) << 8) + ord(binary_data[1])
            binary_data = binary_data[2:]
        elif octet1 == 255:
            results['size'] = (ord(binary_data[0]) << 24) | (ord(binary_data[1]) << 16) | (ord(binary_data[2])) << 8 | ord(binary_data[3])
            binary_data = binary_data[4:]
        else:
            print "not implemented, header length", octet1
            return results
    else:
        # old format
        results["format"] = "Old"
        results["content_tag"] = (packet_header >> 2) & 0x0F
        length_type = packet_header & 0x03

        #print length_type

        if length_type < 3:
            length_octets = pow(2, length_type)
            results['header_size'] = length_octets + 1
            #print length_octets
            if length_octets == 1:
                results['size'] = ord(binary_data[0])
                binary_data = binary_data[1:]
            elif length_octets == 2:
                results['size'] = (ord(binary_data[0]) << 8) + ord(binary_data[1])
                binary_data = binary_data[2:]
            elif length_octets == 4:
                results['size'] = (ord(binary_data[0]) << 24) + (ord(binary_data[1]) << 16) + (ord(binary_data[2]) << 8) + ord(binary_data[3])
                binary_data = binary_data[4:]
            else:
                print "not implemented, header length", length_octets
                return results
        elif length_type == 3:
            print "not implemented, length type", length_type
            return results

    return decode_tag(results, binary_data[:results['size']])

def decode_tag(results, binary_data):
        '''
        Decodes packet types from a PGP string.
        '''
        if results['content_tag'] == 2:
            # signature packet
            results["type"] = "Signature Packet"
            sig_version = ord(binary_data[0])
            if sig_version == 3:
                mat_length = ord(binary_data[1])
                sig_type = ord(binary_data[2])
                print "sig type:", sig_type
                create_time = binary_data[3:7]
                print "create time:", print_hex(create_time)
                key_id = binary_data[7:15]
                print "key id:", print_hex(key_id)
                key_algo = ord(binary_data[15])
                hash_algo = ord(binary_data[16])
                print "key algo: %x" % key_algo
                print "hash algo: %x" % hash_algo
                signed_hash = binary_data[17:19]
                print "sig start:", print_hex(signed_hash)
                signature = binary_data[19:]
                #print len(signature)
                r = signature[:20]
                s = signature[20:]
                print "r:", print_hex(signature[:20])
                print "s:", print_hex(signature[20:])
        elif results['content_tag'] == 6:
            results["type"] = "Public Key Packet"
            results["key.version"] = ord(binary_data[0])
            if results["key.version"] == 4:
                create_time = binary_data[1:5]
                #print "create time:", print_hex(create_time)
                #days = binary_data[5:7]
                #print "valid days:", (ord(days[0]) << 8) + ord(days[1])
                results["key.algo"] = ord(binary_data[5])
            elif results["key.version"] == 3:
                #create_time = binary_data[1:5]
                #print "create time:", print_hex(create_time)
                #days = binary_data[5:7]
                #print "valid days:", (ord(days[0]) << 8) + ord(days[1])
                #results["key.algo"] = ord(binary_data[6])
                print "not implemented, key version", results["key.version"]
            else:
                print "not implemented, key version", results["key.version"]

        elif results['content_tag'] == 13:
            results["type"] = "User ID"
            user = ""
            for char in binary_data:
                user += chr(ord(char))
            results["user.value"] = user
        else:
            pass
            #print "not yet implemented, tag", results['content_tag'] 
            
        return results
                    #print "\nAll data:", print_hex(binary_data)

class GPGFile(list):
    '''
    Class to manager PGP packet data.
    '''
    def __init__(self, filename = None, url = None):
        self.url = url
        self.filename = filename
        self.extend(decode(self.filename))
        
    def get_user_ids(self):
        '''
        Returns a list of the display names for keys.
        '''
        idlist = []
        for item in self:
            if item["content_tag"] == 13:
                idlist.append(item["user.value"])

        return idlist

##def binary2int(bin):
##    i = 0
##    total = 0
##    for j in range(len(bin)):
##        total += ord(bin[j]) * pow(2,i)
##        i += 8
##    return total

#if __name__=="__main__":
#    for item in decode_asc("mcnab.asc"):
#        print item
#    print get_user_id("mcnab.asc")



##    
##if __name__ == '__main__':
##    import sys
##    if len(sys.argv) == 1:
##        print 'Usage: GPG.py <signed file>'
##        sys.exit()
##
##    obj = GPGSubprocess()
##    file = open(sys.argv[1], 'rb')
##    sig = obj.verify_file( file )
##    print sig.__dict__
GPG = Dummy()
GPG.DEFAULT_PATH = DEFAULT_PATH
GPG.EncryptedMessage = EncryptedMessage
GPG.GPGFile = GPGFile
GPG.GPGSubprocess = GPGSubprocess
GPG.ImportResult = ImportResult
GPG.ListResult = ListResult
GPG.Signature = Signature
GPG._ = _
GPG.decode = decode
GPG.decode_asc = decode_asc
GPG.decode_data = decode_data
GPG.decode_header = decode_header
GPG.decode_lines = decode_lines
GPG.decode_sig = decode_sig
GPG.decode_tag = decode_tag
GPG.print_hex = print_hex
GPG.translate = translate
#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2010, Hampus Wessman, Neil McNab
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
# Last Updated: $Date: 2010-05-13 23:32:51 -0700 (Thu, 13 May 2010) $
# Author(s): Hampus Wessman, Neil McNab
#
# Description:
#   Functions for accessing XML formatted data.
#   Last updated for RFC final draft 28
#
########################################################################


# for jigdo only

# handle missing module in jython


GENERATOR = "Metalink Checker Version 5.1"

RFC3339 = "%Y-%m-%dT%H:%M:%SZ"
RFC822 = "%a, %d %b %Y %H:%M:%S +0000"

XMLSEP = "/"

HASHMAP = { "sha256": "sha-256", 
            "sha1": "sha-1",
            "sha512": "sha-512",
            "sha224": "sha-224",
            "sha384": "sha-384",
            }

def hashlookup(text):
    try:
        return HASHMAP[text]
    except KeyError:
        return text

def get_first(x):
    try:
        return x[0]
    except:
        return x


class Resource:
    def __init__(self, url, type="default", location="", preference="", maxconnections="", attrs = {}):
        self.errors = []
        self.url = url
        self.location = location
        if type == "default" or type.strip() == "":
            if url.endswith(".torrent"):
                self.type = "bittorrent"
            else:
                chars = url.find(":")
                self.type = url[:chars]
        else:
            self.type = type
        self.preference = str(preference)
        if maxconnections.strip() == "-" or maxconnections.strip() == "":
            self.maxconnections = "-"
        else:
            self.maxconnections = maxconnections

        for attr in attrs:
            setattr(self, attr, attrs[attr])
            
    def generate(self):
        details = ''
        text = ''
        if self.location.strip() != "":
            details += ' location="'+self.location.lower()+'"'
        if self.preference.strip() != "": details += ' preference="'+self.preference+'"'
        if self.maxconnections.strip() != ""and self.maxconnections.strip() != "-" : details += ' maxconnections="'+self.maxconnections+'"'
        text += '        <url type="'+self.type+'"'+details+'>'+self.url+'</url>\n'
        return text
            
    def validate(self):
        valid = True
        if self.url.strip() == "":
            self.errors.append("Empty URLs are not allowed!")
            valid = False
        allowed_types = ["ftp", "ftps", "http", "https", "rsync", "bittorrent", "magnet", "ed2k"]
        if not self.type in allowed_types:
            self.errors.append("Invalid URL: " + self.url + '.')
            valid = False
        elif self.type in ['http', 'https', 'ftp', 'ftps', 'bittorrent']:
            m = re.search(r'\w+://.+\..+/.*', self.url)
            if m == None:
                self.errors.append("Invalid URL: " + self.url + '.')
                valid = False
        if self.location.strip() != "":
            iso_locations = ["AF", "AX", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR", "AM", "AW", "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY", "BE", "BZ", "BJ", "BM", "BT", "BO", "BA", "BW", "BV", "BR", "IO", "BN", "BG", "BF", "BI", "KH", "CM", "CA", "CV", "KY", "CF", "TD", "CL", "CN", "CX", "CC", "CO", "KM", "CG", "CD", "CK", "CR", "CI", "HR", "CU", "CY", "CZ", "DK", "DJ", "DM", "DO", "EC", "EG", "SV", "GQ", "ER", "EE", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF", "GA", "GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD", "GP", "GU", "GT", "GG", "GN", "GW", "GY", "HT", "HM", "VA", "HN", "HK", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM", "JP", "JE", "JO", "KZ", "KE", "KI", "KP", "KR", "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO", "MK", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ", "MR", "MU", "YT", "MX", "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM", "NA", "NR", "NP", "NL", "AN", "NC", "NZ", "NI", "NE", "NG", "NU", "NF", "MP", "NO", "OM", "PK", "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR", "QA", "RE", "RO", "RU", "RW", "SH", "KN", "LC", "PM", "VC", "WS", "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG", "SK", "SI", "SB", "SO", "ZA", "GS", "ES", "LK", "SD", "SR", "SJ", "SZ", "SE", "CH", "SY", "TW", "TJ", "TZ", "TH", "TL", "TG", "TK", "TO", "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "US", "UM", "UY", "UZ", "VU", "VE", "VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW", "UK"]
            if not self.location.upper() in iso_locations:
                self.errors.append(self.location + " is not a valid country code.")
                valid = False
        if self.preference != "":
            try:
                pref = int(self.preference)
                if pref < 0 or pref > 100:
                    self.errors.append("Preference must be between 0 and 100, not " + self.preference + '.')
                    valid = False
            except:
                self.errors.append("Preference must be a number, between 0 and 100.")
                valid = False
        if self.maxconnections.strip() != "" and self.maxconnections.strip() != "-":
            try:
                conns = int(self.maxconnections)
                if conns < 1:
                    self.errors.append("Max connections must be at least 1, not " + self.maxconnections + '.')
                    valid = False
                elif conns > 20:
                    self.errors.append("You probably don't want max connections to be as high as " + self.maxconnections + '!')
                    valid = False
            except:
                self.errors.append("Max connections must be a positive integer, not " + self.maxconnections + ".")
                valid = False
        return valid
        
class Resource4:
    def __init__(self, url, type="", location="", priority="", attrs = {}):
        self.errors = []
        self.url = url
        self.location = location
        if url.endswith(".torrent"):
            self.type = "torrent"
        else:
            self.type = type
        self.priority = str(priority)
        
        for attr in attrs:
            setattr(self, attr, attrs[attr])
            
    def generate(self):
        details = ''
        text = ""
        if self.location.strip() != "":
            details += ' location="'+self.location.lower()+'"'
        if self.priority.strip() != "": details += ' priority="'+self.priority+'"'
        if self.type != "":
            text += '      <metaurl type="' + self.type + '"'+details+'>'+self.url+'</metaurl>\n'
        else:
            text += '      <url'+details+'>'+self.url+'</url>\n'
            
        return text
        
    def validate(self):
        valid = True
        if self.url.strip() == "":
            self.errors.append("Empty URLs are not allowed!")
            valid = False
        allowed_types = ["torrent"]
        if not self.type in allowed_types and self.type.strip() != "":
            self.errors.append("Invalid URL: " + self.url + '.')
            valid = False
        elif self.type in allowed_types:
            m = re.search(r'\w+://.+\..+/.*', self.url)
            if m == None:
                self.errors.append("Invalid URL: " + self.url + '.')
                valid = False
        if self.location.strip() != "":
            iso_locations = ["AF", "AX", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR", "AM", "AW", "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY", "BE", "BZ", "BJ", "BM", "BT", "BO", "BA", "BW", "BV", "BR", "IO", "BN", "BG", "BF", "BI", "KH", "CM", "CA", "CV", "KY", "CF", "TD", "CL", "CN", "CX", "CC", "CO", "KM", "CG", "CD", "CK", "CR", "CI", "HR", "CU", "CY", "CZ", "DK", "DJ", "DM", "DO", "EC", "EG", "SV", "GQ", "ER", "EE", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF", "GA", "GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD", "GP", "GU", "GT", "GG", "GN", "GW", "GY", "HT", "HM", "VA", "HN", "HK", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM", "JP", "JE", "JO", "KZ", "KE", "KI", "KP", "KR", "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO", "MK", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ", "MR", "MU", "YT", "MX", "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM", "NA", "NR", "NP", "NL", "AN", "NC", "NZ", "NI", "NE", "NG", "NU", "NF", "MP", "NO", "OM", "PK", "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR", "QA", "RE", "RO", "RU", "RW", "SH", "KN", "LC", "PM", "VC", "WS", "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG", "SK", "SI", "SB", "SO", "ZA", "GS", "ES", "LK", "SD", "SR", "SJ", "SZ", "SE", "CH", "SY", "TW", "TJ", "TZ", "TH", "TL", "TG", "TK", "TO", "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "US", "UM", "UY", "UZ", "VU", "VE", "VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW", "UK"]
            if not self.location.upper() in iso_locations:
                self.errors.append(self.location + " is not a valid country code.")
                valid = False
        if self.priority != "":
            try:
                pref = int(self.priority)
                if pref < 1 or pref > 100:
                    self.errors.append("Priority must be between 1 and 100, not " + self.priority + '.')
                    valid = False
            except:
                self.errors.append("Priority must be a number, between 1 and 100.")
                valid = False
        return valid

class MetalinkFileBase:
    '''
    This should not be called directly, it is a base class.
    '''
    def __init__(self, filename, attrs, do_ed2k, do_magnet):
        filename = filename.replace("\\", "/")
        filename = filename.lstrip("/.")
        filename = filename.replace("/../", "")
        if filename.endswith("/.."):
            filename = filename[:-3]
        self.filename = filename
        self.errors = []
        self.hashlist = {}
        self.pieces = []
        self.piecelength = 0
        self.piecetype = ""
        self.resources = []
        self.language = ""
        self.os = ""
        self.size = -1
        self.ed2k = ""
        self.magnet = ""
        self.do_ed2k = do_ed2k
        self.do_magnet = do_magnet
        
        for attr in attrs:
            setattr(self, attr, attrs[attr])

    def get_filename(self):
        return self.filename

    def get_checksums(self):
        return self.hashlist

    def add_checksum(self, name, value):
        self.hashlist[name] = value

    def set_checksums(self, hashlist):
        self.hashlist = hashlist

    def get_piece_dict(self):
        temp = {}
        temp[self.piecetype] = self.pieces
        return temp

    def get_url_dict(self):
        temp = {}
        for url in self.resources:
            temp[url.url] = url
        return temp

    def set_size(self, size):
        self.size = int(size)

    def get_size(self):
        return self.size
    
    def clear_res(self):
        self.resources = []
    
    def add_res(self, res):
        self.resources.append(res)
        
    def add_url(self, *args):
        '''
        Override this in your subclass
        '''
        pass

    def scan_file(self, filename, use_chunks=True, max_chunks=255, chunk_size=256, progresslistener=None):
        print "\nScanning file..."
        # Filename and size
        self.filename = os.path.basename(filename)
        self.size = int(os.stat(filename).st_size)
        # Calculate piece length
        if use_chunks:
            minlength = chunk_size*1024
            self.piecelength = 1024
            while self.size / self.piecelength > max_chunks or self.piecelength < minlength:
                self.piecelength *= 2
            print "Using piecelength", self.piecelength, "(" + str(self.piecelength / 1024) + " KiB)"
            numpieces = self.size / self.piecelength
            if numpieces < 2: use_chunks = False
        # Hashes
        fp = open(filename, "rb")

        md5hash = hashlib.md5()
        sha1hash = hashlib.sha1()
        sha256hash = hashlib.sha256()
        piecehash = hashlib.sha1()
        
        #piecenum = 0
        length = 0
        self.pieces = []
        self.piecetype = "sha1"
        num_reads = math.ceil(self.size / 4096.0)
        reads_per_progress = int(math.ceil(num_reads / 100.0))
        reads_left = reads_per_progress
        progress = 0
        while True:
            data = fp.read(4096)
            if data == "": break
            # Progress updating
            if progresslistener:
                reads_left -= 1
                if reads_left <= 0:
                    reads_left = reads_per_progress
                    progress += 1
                    result = progresslistener.Update(progress)
                    if not get_first(result):
                        print "Canceling scan!"
                        return False
            # Process the data
            if md5hash != None: md5hash.update(data)
            if sha1hash != None: sha1hash.update(data)
            if sha256hash != None: sha256hash.update(data)
            if use_chunks:
                left = len(data)
                while left > 0:
                    if length + left <= self.piecelength:
                        piecehash.update(data)
                        length += left
                        left = 0
                    else:
                        numbytes = self.piecelength - length
                        piecehash.update(data[:numbytes])
                        length += numbytes
                        data = data[numbytes:]
                        left -= numbytes
                    if length == self.piecelength:
                        print "Done with piece hash", len(self.pieces)
                        self.pieces.append(piecehash.hexdigest())
                        piecehash = hashlib.sha1()
                        length = 0
        if use_chunks:
            if length > 0:
                print "Done with piece hash", len(self.pieces)
                self.pieces.append(piecehash.hexdigest())
                piecehash = hashlib.sha1()
            print "Total number of pieces:", len(self.pieces)
        fp.close()
        self.hashlist["md5"] = md5hash.hexdigest()
        self.hashlist["sha1"] = sha1hash.hexdigest()
        if sha256hash != None:
            self.hashlist["sha256"] = sha256hash.hexdigest()

        # automatically add an ed2k url here
        ed2khash = ed2k_hash(filename)
        
        if self.do_ed2k:
            self.ed2k = compute_ed2k(filename, ed2khash)
            if self.ed2k != "":
                self.add_url(self.ed2k)

        if self.do_magnet:
            self.magnet = compute_magnet(filename, self.size, self.hashlist["md5"], self.hashlist["sha1"], ed2khash)
            if self.magnet != "":
                self.add_url(self.magnet)

        self.hashlist['pgp'] = read_sig(filename)
            
        if len(self.pieces) < 2: self.pieces = []
        # Convert to strings
        #self.size = str(self.size)
        #self.piecelength = str(self.piecelength)
        print "done"
        if progresslistener: progresslistener.Update(100)
        return True

class MetalinkFile4(MetalinkFileBase):
    def __init__(self, filename, attrs = {}, do_ed2k=True, do_magnet=False):
        self.description = ""
        self.identity = ""
        self.license_name = ""
        self.license_url = ""
        self.publisher_name = ""
        self.publisher_url = ""
        self.version = ""
        self.logo = ""
        MetalinkFileBase.__init__(self, filename, attrs, do_ed2k, do_magnet)

    def compare_checksums(self, checksums):
        for key in ("sha-512","sha-384","sha-256","sha-1","md5"):
            try:
                if self.hashlist[key].lower() == checksums[key].lower():
                    return True
            except KeyError: pass
        return False
        
    def add_url(self, url, type="", location="", priority="", attrs={}):
        self.resources.append(Resource4(url, type, location, priority, attrs))
    
    def validate(self):
        valid = True
        if len(self.resources) == 0:
            self.errors.append("You need to add at least one URL!")
            valid = False
        if self.hashlist["md5"].strip() != "":
            m = re.search(r'[^0-9a-fA-F]', self.hashlist["md5"])
            if len(self.hashlist["md5"]) != 32 or m != None:
                self.errors.append("Invalid md5 hash.")                    
                valid = False
        if self.hashlist["sha-1"].strip() != "":
            m = re.search(r'[^0-9a-fA-F]', self.hashlist["sha-1"])
            if len(self.hashlist["sha-1"]) != 40 or m != None:
                self.errors.append("Invalid sha-1 hash.")
                valid = False
        if str(self.size).strip() != "":
            try:
                size = int(self.size)
                if size < 0:
                    self.errors.append("File size must be at least 0, not " + str(self.size) + '.')
                    valid = False
            except:
                self.errors.append("File size must be an integer, not " + str(self.size) + ".")
                valid = False
        return valid

    def generate_file(self):
        if self.filename.strip() != "":
            text = '  <file name="' + self.filename + '">\n'
        else:
            text = '  <file>\n'
        # Publisher info
        if self.publisher_name.strip() != "" or self.publisher_url.strip() != "":
            lictext = ""
            if self.publisher_name.strip() != "":
                lictext += ' name="' + self.publisher_name + '"'
            if self.publisher_url.strip() != "":
                lictext += ' url="' + self.publisher_url + '"'
            text += '      <publisher%s></publisher>\n' % lictext
        # License info
        if self.license_name.strip() != "" or self.license_url.strip() != "":
            #text += '  <license>\n'
            lictext = ""
            if self.license_name.strip() != "":
                lictext += ' name="' + self.license_name + '"'
            if self.license_url.strip() != "":
                lictext += ' url="' + self.license_url + '"'
            text += '      <license%s></license>\n' % lictext
        # Release info
        if self.identity.strip() != "":
            text += '      <identity>'+self.identity+'</identity>\n'
        if self.version.strip() != "":
            text += '      <version>'+self.version+'</version>\n'
        if self.description.strip() != "":
            text += '      <description>'+self.description+'</description>\n'
        # File info
        if self.size > 0:
            text += '      <size>'+str(self.size)+'</size>\n'
        if self.language.strip() != "":
            text += '      <language>'+self.language+'</language>\n'
        if self.os.strip() != "":
            text += '      <os>'+self.os+'</os>\n'
        # Verification
        for key in self.hashlist.keys():
            if key == 'pgp' and self.hashlist[key] != "":
                text += '      <signature type="%s">' % key + self.hashlist[key] + '</signature>\n'
            elif self.hashlist[key] != "":
                text += '      <hash type="%s">' % hashlookup(key) + self.hashlist[key].lower() + '</hash>\n'
        if len(self.pieces) > 1:
            text += '      <pieces type="'+hashlookup(self.piecetype)+'" length="'+str(self.piecelength)+'">\n'
            for idstr in range(len(self.pieces)):
                text += '        <hash>'+self.pieces[idstr]+'</hash>\n'
            text += '      </pieces>\n'
        # File list
        for res in self.resources:
            text += res.generate()
        text += '  </file>\n'
        return text
        
class MetalinkFile(MetalinkFileBase):
    def __init__(self, filename, attrs = {}, do_ed2k=True, do_magnet=False):
        self.maxconnections = ""
        MetalinkFileBase.__init__(self, filename, attrs, do_ed2k, do_magnet)

    def compare_checksums(self, checksums):
        for key in ("sha512","sha384","sha256","sha1","md5"):
            try:
                if self.hashlist[key].lower() == checksums[key].lower():
                    return True
            except KeyError: pass
        return False
        
    def add_url(self, url, type="default", location="", preference="", conns="", attrs={}):
        self.resources.append(Resource(url, type, location, preference, conns, attrs))
    
    def validate(self):
        valid = True
        if len(self.resources) == 0:
            self.errors.append("You need to add at least one URL!")
            valid = False
        if self.hashlist["md5"].strip() != "":
            m = re.search(r'[^0-9a-fA-F]', self.hashlist["md5"])
            if len(self.hashlist["md5"]) != 32 or m != None:
                self.errors.append("Invalid md5 hash.")                    
                valid = False
        if self.hashlist["sha1"].strip() != "":
            m = re.search(r'[^0-9a-fA-F]', self.hashlist["sha1"])
            if len(self.hashlist["sha1"]) != 40 or m != None:
                self.errors.append("Invalid sha-1 hash.")
                valid = False
        if str(self.size).strip() != "":
            try:
                size = int(self.size)
                if size < 0:
                    self.errors.append("File size must be at least 0, not " + str(self.size) + '.')
                    valid = False
            except:
                self.errors.append("File size must be an integer, not " + str(self.size) + ".")
                valid = False
        if self.maxconnections.strip() != "" and self.maxconnections.strip() != "-":
            try:
                conns = int(self.maxconnections)
                if conns < 1:
                    self.errors.append("Max connections must be at least 1, not " + self.maxconnections + '.')
                    valid = False
                elif conns > 20:
                    self.errors.append("You probably don't want max connections to be as high as " + self.maxconnections + '!')
                    valid = False
            except:
                self.errors.append("Max connections must be a positive integer, not " + self.maxconnections + ".")
                valid = False
        return valid

    def generate_file(self):
        if self.filename.strip() != "":
            text = '    <file name="' + self.filename + '">\n'
        else:
            text = '    <file>\n'
        # File info
        if self.size > 0:
            text += '      <size>'+str(self.size)+'</size>\n'
        if self.language.strip() != "":
            text += '      <language>'+self.language+'</language>\n'
        if self.os.strip() != "":
            text += '      <os>'+self.os+'</os>\n'
        # Verification
#        if self.hashlist["md5"].strip() != "" or self.hashlist["sha1"].strip() != "":
        if len(self.hashlist) > 0 or len(self.pieces) > 0:
            text += '      <verification>\n'
            for key in self.hashlist.keys():
                if key == 'pgp' and self.hashlist[key] != "":
                    text += '      <signature type="%s">' % key + self.hashlist[key] + '</signature>\n'
                elif self.hashlist[key] != "":
                    text += '      <hash type="%s">' % key + self.hashlist[key].lower() + '</hash>\n'
            if len(self.pieces) > 1:
                text += '        <pieces type="'+self.piecetype+'" length="'+str(self.piecelength)+'">\n'
                for idstr in range(len(self.pieces)):
                    text += '          <hash piece="'+str(idstr)+'">'+self.pieces[idstr]+'</hash>\n'
                text += '        </pieces>\n'
            text += '      </verification>\n'
        # File list
        if self.maxconnections.strip() != "" and self.maxconnections.strip() != "-":
            maxconns = ' maxconnections="'+self.maxconnections+'"'
        else:
            maxconns = ""
        text += '      <resources'+maxconns+'>\n'
        for res in self.resources:
            text += res.generate()

        text += '      </resources>\n'
        text += '    </file>\n'
        return text

class XMLTag:
    def __init__(self, name, attrs={}):
        self.name = name
        self.attrs = attrs

    def get_attr(self, name):
        return self.attrs[name]

class MetalinkBase:
    '''
    This is a base class and should not be used directly
    '''
    def __init__(self):
        self.errors = []
        self.files = []
        self.generator = GENERATOR
        self.origin = ""
        self.data = ""

        self.p = xml.parsers.expat.ParserCreate(namespace_separator=XMLSEP)
        self.p.buffer_text = True
        self.parent = []

        self.p.StartElementHandler = self.start_element
        self.p.EndElementHandler = self.end_element
        self.p.CharacterDataHandler = self.char_data
        
    def start_element(self, name, attrs):
        pass
        
    def end_element(self, name):
        pass
            
    def char_data(self, data):
        self.data += data #.strip()

    def parsefile(self, filename):
        handle = open(filename, "rb")
        self.parsehandle(handle)
        handle.close()

    def parsehandle(self, handle):
        return self.p.ParseFile(handle)

    def parse(self, text):
        self.p.Parse(text)

    def download_size(self):
        total = 0
        for fileobj in self.files:
            total += fileobj.get_size()
        return total

    def get_file_by_hash(self, hashtype, value):
        for index in range(len(self.files)):
            if self.files[index].hashlist[hashtype] == value:
                return index
        return None

    def validate_url(self, url):
        if url.endswith(".torrent"):
            typestr = "bittorrent"
        else:
            chars = url.find(":")
            typestr = url[:chars]
        allowed_types = ["ftp", "ftps", "http", "https", "rsync", "bittorrent", "magnet", "ed2k"]
        if not typestr in allowed_types:
            return False
        elif typestr in ['http', 'https', 'ftp', 'ftps', 'bittorrent']:
            m = re.search(r'\w+://.+\..+/.*', url)
            if m == None:
                return False
        return True

    
class Metalink(MetalinkBase):
    def __init__(self):
        self.ver = 3
        self.identity = ""
        self.publisher_name = ""
        self.publisher_url = ""
        self.copyright = ""
        self.description = ""
        self.license_name = ""
        self.license_url = ""
        self.version = ""
        self.upgrade = ""
        self.tags = ""
        self.type = ""
        self.pubdate = ""
        self.refreshdate = ""
        self.XMLNS = "http://www.metalinker.org/"
        MetalinkBase.__init__(self)
        
    def generate(self):
        text = '<?xml version="1.0" encoding="utf-8"?>\n'
        origin = ""
        if self.origin.strip() != "":
            origin = 'origin="'+self.origin+'" '
        typetext = ""
        if self.type.strip() != "":
            typetext = 'type="'+self.type+'" '
        gentext = ""
        if self.generator.strip() != "":
            gentext = 'generator="'+self.generator+'" '
        text += '<metalink version="3.0" '+origin + typetext + gentext + 'xmlns="' + self.XMLNS + '">\n'
        text += self.generate_info()
        text += '  <files>\n'
        for fileobj in self.files:
            text += fileobj.generate_file()
        text += '  </files>\n'
        text += '</metalink>'
        try:
            return text.encode('utf-8')
        except:
            return text.decode('latin1').encode('utf-8')
    
    def generate_info(self):
        text = ""
        # Publisher info
        if self.publisher_name.strip() != "" or self.publisher_url.strip() != "":
            text += '  <publisher>\n'
            if self.publisher_name.strip() != "":
                text += '    <name>' + self.publisher_name + '</name>\n'
            if self.publisher_url.strip() != "":
                text += '    <url>' + self.publisher_url + '</url>\n'
            text += '  </publisher>\n'
        # License info
        if self.license_name.strip() != "" or self.license_url.strip() != "":
            text += '  <license>\n'
            if self.license_name.strip() != "":
                text += '    <name>' + self.license_name + '</name>\n'
            if self.license_url.strip() != "":
                text += '    <url>' + self.license_url + '</url>\n'
            text += '  </license>\n'
        # Release info
        if self.identity.strip() != "":
            text += '  <identity>'+self.identity+'</identity>\n'
        if self.version.strip() != "":
            text += '  <version>'+self.version+'</version>\n'
        if self.copyright.strip() != "":
            text += '  <copyright>'+self.copyright+'</copyright>\n'
        if self.description.strip() != "":
            text += '  <description>'+self.description+'</description>\n'
        if self.upgrade.strip() != "":
            text += '  <upgrade>'+self.upgrade+'</upgrade>\n'
        return text
            
    # 3 handler functions
    def start_element(self, name, attrs):
        self.data = ""
        xmlns, name = name.rsplit(XMLSEP, 1)
        if xmlns != self.XMLNS and xmlns != "":
            return
        self.parent.append(XMLTag(name, attrs))
        if name == "file":
            fileobj = MetalinkFile(attrs["name"], attrs)
            self.files.append(fileobj)
            
        if name == "metalink":
            for attrname in ("origin", "type", "pubdate", "refreshdate"):
                try:
                    setattr(self, attrname, attrs[attrname])
                except KeyError: pass
            
    def end_element(self, name):
        xmlns, name = name.rsplit(XMLSEP, 1)
        if xmlns != self.XMLNS and xmlns != "":
            return
        tag = self.parent.pop()

        try:
            if name == "url" and self.parent[-1].name == "resources":
                fileobj = self.files[-1]
                fileobj.add_url(self.data.strip(), attrs=tag.attrs)
            elif name == "tags" and self.parent[-1].name != "file":
                self.tags = self.data.strip()
            elif name in ("name", "url"):
                setattr(self, self.parent[-1].name + "_" + name, self.data.strip())
            elif name in ("identity", "copyright", "description", "version", "upgrade"):
                setattr(self, name, self.data.strip())
            elif name == "hash" and self.parent[-1].name == "verification":
                hashtype = tag.attrs["type"]
                fileobj = self.files[-1]
                #setattr(fileobj, "hash_" + hashtype, self.data)
                fileobj.hashlist[hashtype] = self.data.strip()
            elif name == "signature" and self.parent[-1].name == "verification":
                hashtype = tag.attrs["type"]
                fileobj = self.files[-1]
                #setattr(fileobj, "hash_" + hashtype, self.data)
                fileobj.hashlist[hashtype] = self.data
            elif name == "pieces":
                fileobj = self.files[-1]
                fileobj.piecetype = tag.attrs["type"]
                fileobj.piecelength = tag.attrs["length"]
            elif name == "hash" and self.parent[-1].name == "pieces":
                fileobj = self.files[-1]
                fileobj.pieces.append(self.data.strip())
            elif name in ("os", "language", "tags"):
                fileobj = self.files[-1]
                setattr(fileobj, name, self.data.strip())
            elif name in ("size"):
                fileobj = self.files[-1]
                if self.data.strip() != "":
                    setattr(fileobj, name, int(self.data.strip()))
            if name == "resources":
                fileobj = self.files[-1]
                try:
                    fileobj.maxconnections = tag.attrs['maxconnections']
                except KeyError: pass
        except IndexError: pass
            
    def validate(self, *args):
        valid = True
        if self.publisher_url.strip() != "":
            if not self.validate_url(self.publisher_url):
                self.errors.append("Invalid URL: " + self.publisher_url + '.')
                valid = False
        if self.license_url.strip() != "":
            if not self.validate_url(self.license_url):
                self.errors.append("Invalid URL: " + self.license_url + '.')
                valid = False
                
        for fileobj in self.files:
            result = fileobj.validate()
            valid = valid and result
            self.errors.extend(fileobj.errors)
        return valid
    
class Metalink4(MetalinkBase):
    def __init__(self):
        self.ver = 4
        self.dynamic=""
        self.published=""
        self.updated=""
        self.XMLNS = "urn:ietf:params:xml:ns:metalink"
        MetalinkBase.__init__(self)

    def generate(self):
        text = '<?xml version="1.0" encoding="utf-8"?>\n'
        text += '<metalink xmlns="' + self.XMLNS + '">\n'

        attr = 'dynamic="false"'        
        if self.dynamic.lower() == "true":
            attr = 'dynamic="true"'

        if self.origin.strip() != "":
            text += '<origin ' + attr + '>'+self.origin+'</origin>\n'
       
        for fileobj in self.files:
            text += fileobj.generate_file()
        text += '</metalink>'
        try:
            return text.encode('utf-8')
        except:
            return text.decode('latin1').encode('utf-8')
        
    # handler functions
    def start_element(self, name, attrs):
        if name.startswith("http://www.metalinker.org"):
            raise AssertionError, "Not a valid Metalink 4 (RFC) file."
            
        self.data = ""
        xmlns, name = name.rsplit(XMLSEP, 1)
        if xmlns != self.XMLNS:
            return
        self.parent.append(XMLTag(name, attrs))
        if name == "file":
            fileobj = MetalinkFile4(attrs["name"], attrs)
            self.files.append(fileobj)
        
    def end_element(self, name):
        xmlns, name = name.rsplit(XMLSEP, 1)
        if xmlns != self.XMLNS:
            return
        tag = self.parent.pop()

        try:
            if name in ("generator", "origin", "published", "updated"):
                setattr(self, name, self.data.strip())
                if name == "origin" and tag.attrs.has_key("dynamic"):
                    self.dynamic = tag.attrs["dynamic"]
            elif name in ("url", "metaurl"):
                fileobj = self.files[-1]
                fileobj.add_url(self.data.strip(), attrs=tag.attrs)
            elif name in ("publisher", "license"):
                fileobj = self.files[-1]
                try:
                    setattr(fileobj, name + "_name", tag.attrs["name"])
                except KeyError: pass
                try:
                    setattr(fileobj, name + "_url", tag.attrs["url"])
                except KeyError: pass
            elif name == "hash" and self.parent[-1].name == "file":
                hashtype = tag.attrs["type"]
                fileobj = self.files[-1]
                #setattr(fileobj, "hash_" + hashtype, self.data)
                fileobj.hashlist[hashtype] = self.data.strip()
            elif name == "signature":
                hashtype = tag.attrs["type"]
                fileobj = self.files[-1]
                #setattr(fileobj, "hash_" + hashtype, self.data)
                fileobj.hashlist[hashtype] = self.data
            elif name == "pieces":
                fileobj = self.files[-1]
                fileobj.piecetype = tag.attrs["type"]
                fileobj.piecelength = tag.attrs["length"]
            elif name == "hash" and self.parent[-1].name == "pieces":
                fileobj = self.files[-1]
                fileobj.pieces.append(self.data.strip())
            elif name in ("os", "language", "identity", "description", "version"):
                fileobj = self.files[-1]
                setattr(fileobj, name, self.data.strip())
            elif name in ("size"):
                fileobj = self.files[-1]
                if self.data.strip() != "":
                    setattr(fileobj, name, int(self.data.strip()))
        except IndexError: pass
            
   
    def validate(self, *args):
        valid = True
                
        for fileobj in self.files:
            result = fileobj.validate()
            valid = valid and result
            self.errors.extend(fileobj.errors)
        return valid

############### RSS/Atom ###################

class RSSAtomItem:
    def __init__(self):
        self.url = None
        self.title = None
        self.size = -1

class RSSAtom():
    def __init__(self):
        self.files = []
        self.title = ""
        
        self.p = xml.parsers.expat.ParserCreate()
        self.p.buffer_text = True
        self.parent = []

        self.p.StartElementHandler = self.start_element
        self.p.EndElementHandler = self.end_element
        self.p.CharacterDataHandler = self.char_data
            
    def char_data(self, data):
        self.data += data #.strip()

    def parsehandle(self, handle):
        return self.p.ParseFile(handle)
        
    # handler functions
    def start_element(self, name, attrs):
        self.data = ""
        self.parent.append(XMLTag(name, attrs))
        if name in ('item', 'entry'):
            self.files.append(RSSAtomItem())
        
    def end_element(self, name):
        tag = self.parent.pop()

        if name == "link":
            if tag.attrs.has_key("rel") and tag.attrs["rel"] == 'enclosure':
                fileobj = self.files[-1]
                if tag.attrs.has_key("href"):
                    fileobj.url = tag.attrs["href"]
                if tag.attrs.has_key("length"):
                    fileobj.size = int(tag.attrs["length"])
                    
        if name == "enclosure":
            fileobj = self.files[-1]
            if tag.attrs.has_key("url"):
                fileobj.url = tag.attrs["url"]
            if tag.attrs.has_key("length"):
                fileobj.size = int(tag.attrs["length"])
                
        if name == "title" and self.parent[-1].name in ("entry","item"):
            fileobj = self.files[-1]
            fileobj.title = self.data
        elif name == "title":
            self.title = self.data    
        
        
############### Jigdo ######################

class DecompressFile(gzip.GzipFile):
    def __init__(self, fp):
        self.fp = fp
        self.geturl = fp.geturl

        gzip.GzipFile.__init__(self, fileobj=fp)

    def info(self):
        info = self.fp.info()
        # store current position, must reset if in middle of read operation
        reset = self.tell()
        # reset to start
        self.seek(0)
        newsize = str(len(self.read()))
        # reset to original position
        self.seek(reset)
        info["Content-Length"] = newsize
        return info

class URLInfo(StringIO.StringIO):
    def __init__(self, fp):
        self.fp = fp
        self.geturl = fp.geturl

        StringIO.StringIO.__init__(self)
        self.write(fp.read())
        self.seek(0)

    def info(self):
        info = self.fp.info()
        # store current position, must reset if in middle of read operation
        reset = self.tell()
        # reset to start
        self.seek(0)
        newsize = str(len(self.read()))
        # reset to original position
        self.seek(reset)
        info["Content-Length"] = newsize
        return info

def open_compressed(fp):
    compressedfp = URLInfo(fp)
    newfp = DecompressFile(compressedfp)

    try:
    	newfp.info()
    	return newfp
    except IOError:
        compressedfp.seek(0)
        return compressedfp
        
class TemplateDecompress:
    def __init__(self, filename=None):
        self.handle = None
        self.buffer = ""
        if filename != None:
            self.open(filename)
        
    def open(self, filename):
        self.handle = open(filename, "rb")
        # read text comments first, then switch to binary data
        data = self.handle.readline()
        while data.strip() != "":
            data = self.handle.readline()
            
        return self.handle
        
    def read(self, size):
        while len(self.buffer) < size:
            self.buffer += self.get_chunk()
            
        buff = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return buff
    
    def get_chunk(self):
        typestr = self.handle.read(4)
        #print "type:", type
        length = int(binascii.hexlify(self.handle.read(6)[::-1]), 16)
        value = self.handle.read(length-10)
        
        if typestr == "BZIP":
            uncompressed = int(binascii.hexlify(value[:6][::-1]), 16)
            data = value[6:]
            data = bz2.decompress(data)
            assert(len(data) == uncompressed)
            return data
        elif typestr == "DATA":
            uncompressed = int(binascii.hexlify(value[:6][::-1]), 16)
            data = value[6:]
            data = zlib.decompress(data)
            assert(len(data) == uncompressed)
            return data
        else:
            print "Unexpected Jigdo template type %s." % type
        return ""
    
    def close(self):
        return self.handle.close()

class Jigdo(Metalink):
    def __init__(self):
        self.template = ""
        self.template_md5 = ""
        self.filename = ""
        self.mirrordict = {}
        self.compression_type = None
        Metalink.__init__(self)
        self.p = ParseINI()

    def parsefile(self, filename):
        handle = gzip.open(filename, "rb")
        self.parsehandle(handle)
        handle.close()

    def parsehandle(self, handle):
        # need to gunzip here if needed
        newhandle = open_compressed(handle)
        self.p.readfp(newhandle)

        self.decode(self.p)

    def parse(self, text):
        raise AssertionError, "Not implemented"

    def decode(self, configobj):
        serverdict = {}
        for item in configobj.items("Servers"):
            serverdict[item[0]] = [item[1].split(" ")[0].strip()]

        for item in configobj.items("Mirrorlists"):
            self.mirrordict[item[0]] = item[1].split(" ")[0]

            temp = []
            fp = urllib2.urlopen(self.mirrordict[item[0]])
            line = fp.readline()
            while line:
                if not line.startswith("#"):
                    temp.append(line.strip())
                line = fp.readline()
            serverdict[item[0]] = temp
            fp.close()
        
        for item in configobj.items("Image"):
            if item[0].lower() == "template":
                self.template = item[1]
            if item[0].lower() == "template-md5sum":
                self.template_md5 = binascii.hexlify(self.base64hash2bin(item[1]))
            if item[0].lower() == "filename":
                self.filename = item[1]
            if item[0].lower() == "shortinfo":
                self.identity = item[1]
            if item[0].lower() == "info":
                self.description = item[1]
                
        for item in configobj.items("Parts"):
            base64hash = item[0]
            binaryhash = self.base64hash2bin(base64hash)
            hexhash = binascii.hexlify(binaryhash)
            url = item[1]
            parts = url.split(":", 1)
            urls = []
            if len(parts) == 1:
                urls = [parts[0]]
                local = parts[0]
            else:
                for server in serverdict[parts[0]]:
                    urls.append(server + parts[1])
                local = parts[1]

            index = self.get_file_by_hash("md5", hexhash)
            if index == None:
                myfile = MetalinkFile(local)
                myfile.add_checksum("md5", hexhash)
                self.files.append(myfile)
                index = -1

            for url in urls:
                self.files[index].add_url(url)

    def base64hash2bin(self, base64hash):
        # need to pad hash out to multiple of both 6 (base 64) and 8 bits (1 byte characters)
        return base64.b64decode(base64hash + "AA", "-_")[:-2]

    def get_size(self, string):
        total = 0
        for i in range(len(string)):
            temp = ord(string[i]) << (8 * i)
            total += temp
        return total

    def mkiso(self):
        # go to the end to read the DESC section
        readhandle = open(os.path.basename(self.template), "rb")
        readhandle.seek(-6, 2)
        desclen = int(binascii.hexlify(readhandle.read(6)[::-1]), 16)
        readhandle.seek(-(desclen-10), 2)
        value = readhandle.read()
        
        # index DESC section into list
        chunks = []
        count= 0 
        while len(value) > 6:
            subtype = ord(value[0])
            #print "subtype: %x" % subtype
            sublength = int(binascii.hexlify(value[1:7][::-1]), 16)
            #print "sublength:", sublength
            value = value[7:]
            if subtype == 6:
                #rsync = value[:8]
                md5 = value[8:24]
                value = value[24:]
                chunks.append([6, sublength, binascii.hexlify(md5)])
            elif subtype == 5:
                filemd5 = value[:16]
                #blocklen = int(binascii.hexlify(value[16:20][::-1]), 16)
                value = value[20:]
            elif subtype == 2:
                chunks.append([2, sublength])
                count += 1
            else:
                print "Unknown DESC subtype %s." % subtype
                raise
        
        readhandle.close()
        
        handle = open(self.filename, "wb")
        
        templatedata = TemplateDecompress(os.path.basename(self.template))
            
        for chunk in chunks:
            chunktype = chunk[0]
            chunklen = chunk[1]
            if chunktype == 6:
                # read data from external files, errors if hash not found
                fileobj = self.files[self.get_file_by_hash('md5', chunk[2])]
                if chunklen != os.stat(fileobj.filename).st_size:
                    print "Warning: File size mismatch for %s." % fileobj.filename
                
                tempfile = open(fileobj.filename, "rb")
                filedata = tempfile.read(1024*1024)
                while filedata:
                    handle.write(filedata)
                    filedata = tempfile.read(1024*1024)
                tempfile.close()
                
            if chunktype == 2:
                # read from template file here
                handle.write(templatedata.read(chunklen))

        templatedata.close()
        handle.close()
        return binascii.hexlify(filemd5)

class ParseINI(dict):
    '''
    Similiar to what is available in ConfigParser, but case sensitive
    '''
    def __init__(self):
        pass

    def readfp(self, fp):
        line = fp.readline()
        section = None
        #print "Jigdo file contents"
        #print "-" * 79
        while line:
            #print line
            if not line.startswith("#") and line.strip() != "":
                if line.startswith("["):
                    section = line[1:-2]
                    self[section] = []
                else:
                    parts = line.split("=", 1)
                    self[section].append((parts[0], parts[1].strip()))
            line = fp.readline()
        #sys.exit()
    def items(self, section):
        try:
            return self[section]
        except KeyError:
            return []

def convert_4to3(metalinkobj4):
    metalinkobj3 = Metalink()
    
    for attr in ('generator', 'origin'):
        setattr(metalinkobj3, attr, getattr(metalinkobj4, attr))
    if metalinkobj4.dynamic.lower() == "true":
        metalinkobj3.type = 'dynamic'
        
    if metalinkobj4.published != "":
        metalinkobj3.pubdate = time.strftime(RFC822, rfc3339_parsedate(metalinkobj4.published))
    if metalinkobj4.updated != "":
        metalinkobj3.refreshdate = time.strftime(RFC822, rfc3339_parsedate(metalinkobj4.updated))
        
    for fileobj4 in metalinkobj4.files:
        fileobj3 = MetalinkFile(fileobj4.filename)
        # copy common attributes
        for attr in ('filename', 'pieces', 'piecelength', 'language', 'os', 'size'):
            setattr(fileobj3, attr, getattr(fileobj4, attr))
        setattr(fileobj3, "piecetype", getattr(fileobj4, "piecetype").replace("-", ""))
        for attr in ('description', 'version', 'identity', 'license_url', 'license_name', 'publisher_url', 'publisher_name'):
            setattr(metalinkobj3, attr, getattr(fileobj4, attr))
        # copy hashlist, change key names
        for key in fileobj4.hashlist.keys():
            fileobj3.hashlist[key.replace("-", "")] = fileobj4.hashlist[key]
        for res4 in fileobj4.resources:
            if res4.priority != "":
                fileobj3.add_url(res4.url, "", res4.location, str(101-int(res4.priority)))
            else:
                fileobj3.add_url(res4.url, "", res4.location)
        metalinkobj3.files.append(fileobj3)
    return metalinkobj3

def convert_3to4(metalinkobj3):
    metalinkobj4 = Metalink4()
    # copy common attributes
    for attr in ('origin', 'generator'):
        setattr(metalinkobj4, attr, getattr(metalinkobj3, attr))
    if getattr(metalinkobj3, 'type') == 'dynamic':
        setattr(metalinkobj4, 'dynamic', "true")
    else:
        setattr(metalinkobj4, 'dynamic', "false")

    if metalinkobj3.pubdate != "":
        metalinkobj4.published = time.strftime(RFC3339, rfc822.parsedate(metalinkobj3.pubdate))
    if metalinkobj3.refreshdate != "":
        metalinkobj4.updated = time.strftime(RFC3339, rfc822.parsedate(metalinkobj3.refreshdate))
        
    for fileobj3 in metalinkobj3.files:
        fileobj4 = MetalinkFile4(fileobj3.filename)
        # copy common attributes
        for attr in ('filename', 'pieces', 'piecelength', 'piecetype', 'language', 'os', 'size'):
            setattr(fileobj4, attr, getattr(fileobj3, attr))
        for attr in ('description', 'identity', 'version', 'license_url', 'license_name', 'publisher_url', 'publisher_name'):
            setattr(fileobj4, attr, getattr(metalinkobj3, attr))
        # copy hashlist, change key names
        for key in fileobj3.hashlist.keys():
            fileobj4.hashlist[hashlookup(key)] = fileobj3.hashlist[key]
        for res3 in fileobj3.resources:
            if res3.preference != "":
                fileobj4.add_url(res3.url, "", res3.location, str(101-int(res3.preference)))
            else:
                fileobj4.add_url(res3.url, "", res3.location)
        metalinkobj4.files.append(fileobj4)
    return metalinkobj4
    
def convert(metalinkobj, ver=4):
    ver = int(ver)
    if metalinkobj.ver == ver:
        return metalinkobj
    elif metalinkobj.ver == 3 and ver == 4:
        return convert_3to4(metalinkobj)
    elif metalinkobj.ver == 4 and ver == 3:
        return convert_4to3(metalinkobj)
    else:
        raise AssertionError, "Cannot do conversion %s to %s!" % (metalinkobj.ver, ver)

def rfc3339_parsedate(datestr):
    offset = "+00:00"
    if datestr.endswith("Z"):   
        datestr = datestr[:-1]
    else:
        offset = datestr[-6:]
        datestr = datestr[:-6]
    # remove milliseconds, strptime breaks otherwise
    datestr = datestr.split(".")[0]
    offset = __convert_offset(offset)
    # Convert to UNIX epoch time to add offset and then convert back to Python time tuple
    unixtime = calendar.timegm(time.strptime(datestr, "%Y-%m-%dT%H:%M:%S"))
    unixtime += offset
    return time.gmtime(unixtime)

def __convert_offset(offsetstr):
    '''
    Convert string offset of the form "-08:00" to an int of seconds for
    use with UNIX epoch time.
    '''
    offsetstr = offsetstr.replace(":", "")
    operator = offsetstr[0]
    hour = offsetstr[1:3]
    minute = offsetstr[3:5]
    offsetsecs = 0
    offsetsecs += int(hour) * 3600
    offsetsecs += int(minute) * 60
    if operator == "+":
        offsetsecs *= -1
    return offsetsecs

def parsefile(filename, ver=3):
    xml = Metalink4()
    try:
        xml.parsefile(filename)
    except AssertionError:
        xml = Metalink()
        xml.parsefile(filename)
    xml = convert(xml, ver)
    return xml
    
def parsehandle(handle, ver=3):
    text = handle.read()
    xml = Metalink4()
    try:
        xml.parse(text)
    except AssertionError:
        xml = Metalink()
        xml.parse(text)
    xml = convert(xml, ver)
    return xml


def read_sig(filename):
    '''
    Checks for signatures for the file.
    '''
    sig = read_asc_sig(filename)
    if sig != "":
        return sig
    return read_bin_sig(filename)

def read_bin_sig(filename):
    '''
    Converts a binary signature to ASCII
    '''
    header = "-----BEGIN PGP SIGNATURE-----\n\n"
    footer = "-----END PGP SIGNATURE-----\n"
    filename = filename + ".sig"
    if os.access(filename, os.R_OK):
        handle = open(filename, "rb")
        text = binascii.b2a_base64(handle.read())
        handle.close()
        text = header + text + footer
        return text    
    return ""

def read_asc_sig(filename):
    '''
    Reads a detached ASCII PGP signature from a file.
    '''
    filename = filename + ".asc"
    if os.access(filename, os.R_OK):
        handle = open(filename, "rb")
        text = handle.read()
        handle.close()
        return text
    return ""


def compute_ed2k(filename, size=None, ed2khash=None):
    '''
    Generates an ed2k link for a file on the local filesystem.
    '''
    if size == None:
        size = os.path.getsize(filename)
    if ed2khash == None:
        ed2khash = ed2k_hash(filename)

    return "ed2k://|file|%s|%s|%s|/" % (os.path.basename(filename), size, ed2khash)

def ed2k_hash(filename):    
    blocksize = 9728000
    size = os.path.getsize(filename)

    handle = open(filename, "rb")
    data = handle.read(blocksize)
    hashes = ""
    md4 = None
    
    while data:
        md4 = hashlib.new('md4')
        md4.update(data)
        hashes += md4.digest()
        data = handle.read(blocksize)

    # handle file size of zero
    if md4 == None:
        md4 = hashlib.new('md4')
    outputhash = md4.hexdigest()

    if size % blocksize == 0:
        md4 = hashlib.new('md4')
        md4.update("")
        hashes += md4.hexdigest()

    if size >= blocksize:
        md4 = hashlib.new('md4')
        md4.update(hashes)
        outputhash = md4.hexdigest()
        
    return outputhash

def file_hash(filename, hashtype):
    '''
    returns checksum as a hex string
    '''
    hashfunc = getattr(hashlib, hashtype)
    hashobj = hashfunc()
    return filehash(filename, hashobj)

def filehash(thisfile, filesha):
    '''
    First parameter, filename
    Returns sum as a string of hex digits
    '''
    try:
        filehandle = open(thisfile, "rb")
    except:
        return ""

    chunksize = 1024*1024
    data = filehandle.read(chunksize)
    while(data != ""):
        filesha.update(data)
        data = filehandle.read(chunksize)

    filehandle.close()
    return filesha.hexdigest()

def compute_magnet(filename, size = None, md5 = None, sha1 = None, ed2khash = None):
    if size == None:
        size = os.path.getsize(filename)
    if ed2khash == None:
        ed2khash = ed2k_hash(filename)
    if md5 == None:
        md5 = file_hash(filename, 'md5')
    if sha1 == None:
        sha1 = file_hash(filename, 'sha1')
    return "magnet:?dn=%s&amp;xl=%s&amp;xt=urn:sha1:%s&amp;xt=urn:md5:%s&amp;xt=urn:ed2k:%s" % (os.path.basename(filename), size, base64.b32encode(binascii.unhexlify(sha1)), md5.upper(), ed2khash.upper())

metalink = Dummy()
metalink.DecompressFile = DecompressFile
metalink.GENERATOR = GENERATOR
metalink.HASHMAP = HASHMAP
metalink.Jigdo = Jigdo
metalink.Metalink = Metalink
metalink.Metalink4 = Metalink4
metalink.MetalinkBase = MetalinkBase
metalink.MetalinkFile = MetalinkFile
metalink.MetalinkFile4 = MetalinkFile4
metalink.MetalinkFileBase = MetalinkFileBase
metalink.ParseINI = ParseINI
metalink.RFC3339 = RFC3339
metalink.RFC822 = RFC822
metalink.RSSAtom = RSSAtom
metalink.RSSAtomItem = RSSAtomItem
metalink.Resource = Resource
metalink.Resource4 = Resource4
metalink.TemplateDecompress = TemplateDecompress
metalink.URLInfo = URLInfo
metalink.XMLSEP = XMLSEP
metalink.XMLTag = XMLTag
metalink.compute_ed2k = compute_ed2k
metalink.compute_magnet = compute_magnet
metalink.convert = convert
metalink.convert_3to4 = convert_3to4
metalink.convert_4to3 = convert_4to3
metalink.ed2k_hash = ed2k_hash
metalink.file_hash = file_hash
metalink.filehash = filehash
metalink.get_first = get_first
metalink.hashlookup = hashlookup
metalink.open_compressed = open_compressed
metalink.parsefile = parsefile
metalink.parsehandle = parsehandle
metalink.read_asc_sig = read_asc_sig
metalink.read_bin_sig = read_bin_sig
metalink.read_sig = read_sig
metalink.rfc3339_parsedate = rfc3339_parsedate
#!/usr/bin/env python
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2009, Neil McNab
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
# Filename: $URL: https://metalinks.svn.sourceforge.net/svnroot/metalinks/checker/console.py $
# Last Updated: $Date: 2010-04-10 18:23:19 -0700 (Sat, 10 Apr 2010) $
# Version: $Rev: 637 $
# Author(s): Neil McNab
#
# Description:
#   Command line application that checks or downloads metalink files.  Requires
# Python 2.5 or newer.
#
# Instructions:
#   1. You need to have Python installed.
#   2. Run on the command line using: python checker.py
#
########################################################################




def translate():
    '''
    Setup translation path
    '''
    if __name__=="__main__":
        try:
            base = os.path.basename(__file__)[:-3]
            localedir = os.path.join(os.path.dirname(__file__), "locale")
        except NameError:
            base = os.path.basename(sys.executable)[:-4]
            localedir = os.path.join(os.path.dirname(sys.executable), "locale")
    else:
        temp = __name__.split(".")
        base = temp[-1]
        localedir = os.path.join("/".join(["%s" % k for k in temp[:-1]]), "locale")

    #print base, localedir
    localelang = locale.getdefaultlocale()[0]
    if localelang == None:
        localelang = "LC_ALL"
    t = gettext.translation(base, localedir, [localelang], None, 'en')
    return t.ugettext

_ = translate()

def run():
    '''
    Start a console version of this application.
    '''
    # Command line parser options.
    usage = "usage: %prog [-c|-d|-j|--convert|--rconvert] [options] arg1 arg2 ..."
    parser = optparse.OptionParser(version=checker.ABOUT, usage=usage)
    parser.add_option("--download", "-d", action="store_true", dest="download", help=_("Actually download the file(s) in the metalink"))
    parser.add_option("--check", "-c", action="store_true", dest="check", help=_("Check the metalink file URLs"))
    #parser.add_option("--file", "-f", dest="filevar", metavar="FILE", help=_("Metalink file to check or file to download"))
    parser.add_option("--timeout", "-t", dest="timeout", metavar="TIMEOUT", help=_("Set timeout in seconds to wait for response (default=10)"))
    parser.add_option("--os", "-o", dest="os", metavar="OS", help=_("Operating System preference"))
    parser.add_option("--no-segmented", "-s", action="store_true", dest="nosegmented", help=_("Do not use the segmented download method"))
    parser.add_option("--lang", "-l", dest="language", metavar="LANG", help=_("Language preference (ISO-639/3166)"))
    parser.add_option("--country", dest="country", metavar="LOC", help=_("Two letter country preference (ISO 3166-1 alpha-2)"))
    parser.add_option("--pgp-keys", "-k", dest="pgpdir", metavar="DIR", help=_("Directory with the PGP keys that you trust (default: working directory)"))
    parser.add_option("--pgp-store", "-p", dest="pgpstore", metavar="FILE", help=_("File with the PGP keys that you trust (default: ~/.gnupg/pubring.gpg)"))
    parser.add_option("--gpg-binary", "-g", dest="gpg", help=_("(optional) Location of gpg binary path if not in the default search path"))
    parser.add_option("--convert-jigdo", "-j", action="store_true", dest="jigdo", help=_("Convert Jigdo format file to Metalink"))
    parser.add_option("--port", dest="port", help=_("Streaming server port to use (default: No streaming server)"))
    parser.add_option("--html", dest="html", help=_("Extract links from HTML webpage"))
    parser.add_option("--convert", dest="convert", action="store_true", help="Conversion from 3 to 4 (IETF RFC)")
    parser.add_option("--rconvert", dest="rev", action="store_true", help="Reverses conversion from 4 (IETF RFC) to 3")
    parser.add_option("--output", dest="output", metavar="OUTFILE", help=_("Output conversion result to this file instead of screen"))
    parser.add_option("--rss", "-r", action="store_true", dest="rss", help=_("RSS/Atom Feed Mode, implies -d"))
    parser.add_option("-w", dest="writedir", default=os.getcwd(), help=_("Directory to write output files to (default: current directory)"))
    (options, args) = parser.parse_args()
    
    #if options.filevar != None:
    #   args.append(options.filevar)

    if len(args) == 0:
        parser.print_help()
        return

    socket.setdefaulttimeout(10)
    download.set_proxies()
    if options.os != None:
        download.OS = options.os
    if options.language != None:
        download.LANG = [].extend(options.language.lower().split(","))
    if options.country != None:
        download.COUNTRY = options.country
    if options.pgpdir != None:
        download.PGP_KEY_DIR = options.pgpdir
    if options.pgpstore != None:
        download.PGP_KEY_STORE = options.pgpstore
    if options.port != None:
        download.PORT = int(options.port)
    if options.gpg != None:
        GPG.DEFAULT_PATH.insert(0, options.gpg)
        
    if options.timeout != None:
        socket.setdefaulttimeout(int(options.timeout))

    if options.country != None and len(options.country) != 2:
        print _("Invalid country length, must be 2 letter code")
        return

    if options.jigdo:
        print download.convert_jigdo(args[0])
        return
        
    if options.convert:
        text = download.parse_metalink(args[0], ver=4).generate()
        if options.output:
            handle = open(options.output, "w")
            handle.write(text)
            handle.close()
        else:
            print text
        return
        
    if options.rev:
        text = download.parse_metalink(args[0], ver=3).generate()
        if options.output:
            handle = open(options.output, "w")
            handle.write(text)
            handle.close()
        else:
            print text
        return

    if options.html:
        handle = download.urlopen(options.html)
        text = handle.read()
        handle.close()

        page = checker.Webpage()
        page.set_url(options.html)
        page.feed(text)
        
        for item in page.urls:
            if item.endswith(".metalink"):
                print "=" * 79
                print item
                mcheck = checker.Checker()
                mcheck.check_metalink(item)
                results = mcheck.get_results()
                print_totals(results)
        return

    if options.check:
        for item in args:
            print "=" * 79
            print item
            mcheck = checker.Checker()
            mcheck.check_metalink(item)
            results = mcheck.get_results()
            print_totals(results)
        return
            
    if options.download:
        for item in args:
            progress = ProgressBar()
            result = download.get(item, options.writedir, handlers={"status": progress.download_update, "bitrate": progress.set_bitrate, "time": progress.set_time}, segmented = not options.nosegmented)
            progress.download_end()
            if not result:
                sys.exit(-1)
                
    if options.rss:
        for feed in args:
            progress = ProgressBar()
            result = download.download_rss(feed, options.writedir, handlers={"status": progress.download_update, "bitrate": progress.set_bitrate, "time": progress.set_time}, segmented = not options.nosegmented)
            progress.download_end()
            if not result:
                sys.exit(-1)
                        
    sys.exit(0)
    
def print_totals(results):
    for key in results.keys():
        print "=" * 79
        print _("Summary for file") + ":", key

        status_count = 0
        size_count = 0
        checksum_count = 0
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

            checksum = results[key][subkey][2]
            checksum_bool = False
            if checksum == "FAIL":
                checksum_bool = True
                
            redir = results[key][subkey][2]

            print "-" * 79
            print _("Checked") + ": %s" % subkey
            if redir != None:
                print _("Redirected") + ": %s" % redir
            print _("Response Code") + ": %s\t" % status + _("Size Check") + ": %s\t" % size + _("Checksum") + ": %s" % checksum
                
            if size_bool:
                size_count += 1
            if checksum_bool:
                checksum_count += 1
            if status_bool:
                status_count += 1
            if size_bool or status_bool or checksum_bool:
                error_count += 1

        print _("Download errors") + ": %s/%s" % (status_count, total)
        print _("Size check failures") + ": %s/%s" % (size_count, total)
        print _("Checksum failures") + ": %s/%s" % (checksum_count, total)
        print _("Overall failures") + ": %s/%s" % (error_count, total)

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


class ProgressBar:
    def __init__(self, length = 79):
        self.length = length
        self.bitrate = None
        self.time = None
        self.show_bitrate = True
        self.show_time = True
        self.show_bytes = True
        self.show_percent = True
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


        percenttxt = ""
        if self.show_percent:
            percenttxt = " %.0f%%" % percent

        bytes = ""
        if self.show_bytes:
            bytes = " %.2f/%.2f MB" % (current_bytes, total_bytes)
            
        bitinfo = ""
        if self.bitrate != None and self.show_bitrate:
            if self.bitrate > 1000:
                bitinfo = " %.2f Mbps" % (float(self.bitrate) / float(1000))
            else:
                bitinfo = " %.0f kbps" % self.bitrate

        timeinfo = ""
        if self.time != None and self.time != "" and self.show_time:
            timeinfo += " " + self.time
                
        length = self.length - 2 - len(percenttxt) - len(bytes) - len(bitinfo) - len(timeinfo)

        size = int(percent * length / 100)            
        bar = ("#" * size) + ("-" * (length - size))
        output = "[%s]" % bar
        output += percenttxt + bytes + bitinfo + timeinfo
        
        self.line_reset()
        sys.stdout.write(output)

    def set_bitrate(self, bitrate):
        self.bitrate = bitrate
        
    def set_time(self, time):
        self.time = time

    def update(self, count, total):
        if count > total:
            count = total
            
        try:
            percent = 100 * float(count) / total
        except ZeroDivisionError:
            percent = 0

        if total < 0:
            return

        percenttxt = ""
        if self.show_percent:
            percenttxt = " %.0f%%" % percent

        length = self.length - 2 - len(percenttxt)

        size = int(percent * length / 100)
        bar = ("#" * size) + ("-" * (length - size))
        output = "[%s]" % bar
        output += percenttxt
        
        self.line_reset()
        sys.stdout.write(output)

    def line_reset(self):
        
        sys.stdout.write("\b" * 80)
        if os.name != 'nt':
            sys.stdout.write("\n")
        
    def end(self):
        self.update(1, 1)
        print ""

    def download_end(self):
        self.download_update(1, self.total_size, self.total_size)
        print ""

if __name__ == "__main__":
    run()
console = Dummy()
console.ProgressBar = ProgressBar
console._ = _
console.print_totals = print_totals
console.run = run
console.translate = translate
