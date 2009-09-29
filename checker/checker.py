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
# Filename: $URL$
# Last Updated: $Date$
# Version: $Rev$
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

import optparse
import urllib2
import urlparse
import os.path
import random
import sys
import re
import socket
import base64
import hashlib
import httplib
import ftplib
import threading
import time
import binascii

import xmlutils
import download

import locale
import gettext

NAME="Metalink Checker"
VERSION="4.3"

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

import HTMLParser

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
            # add head check for metalink type, if MIME_TYPE or application/xml? treat as metalink
            myheaders = download.urlhead(src, metalink=True)
            if myheaders["link"]:
                # Metalink HTTP Link headers implementation
                # TODO support metalink describedby type
                # TODO support openpgp describedby type
                # TODO this should be more robust and ignore commas in <> for urls
                links = myheaders['link'].split(",")
                fileobj = xmlutils.MetalinkFile(os.path.basename(src))
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
                    type = ""
                    try:
                        type = mydict["type"]
                    except KeyError: pass
                    try:
                        if mydict['rel'] == '"duplicate"':
                            fileobj.add_url(parts[0].strip(" <>"), preference=pri)
                        elif mydict['rel'] == '"describedby"' and type == "application/metalink4+xml":
                            self.check_metalink(parts[0].strip(" <>"))
                        elif type == "application/pgp-signature":
                            pass
                        elif mydict['rel'] == '"describedby"':
                            fileobj.add_url(parts[0].strip(" <>"), preference=pri)
                    except KeyError: pass
                try:
                    hashes = myheaders['digest'].split(",")
                    for hash in hashes:
                        parts = hash.split("=", 1)
                        if parts[0].strip() == 'sha':
                            fileobj.hashlist['sha1'] = binascii.hexlify(binascii.a2b_base64(parts[1].strip()))
                        else:
                            fileobj.hashlist[parts[0].strip().replace("-", "")] = binascii.hexlify(binascii.a2b_base64(parts[1]).strip())
                except KeyError: pass
                print _("Using Metalink HTTP Link headers.")
                metalink = xmlutils.Metalink()
                metalink.files.append(fileobj)
        except KeyError:
            datasource = urllib2.urlopen(src)
            try:
                metalink = xmlutils.Metalink()
                metalink.parsehandle(datasource)
            except:
                print _("ERROR parsing XML.")
                raise
            datasource.close()
        
        if metalink.type == "dynamic":
            origin = metalink.origin
            if origin != src and origin != "":
                try:
                    result = self.check_metalink(origin)
                    self.running = True
                    return result
                except:
                    print "Error downloading from origin %s, not using." % origin
        
        urllist = metalink.files
        if len(urllist) == 0:
            print _("No urls to download file from.")
            self.running = False
            return False

        #results = {}
        for filenode in urllist:
            size = filenode.size
            name = filenode.filename
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
                type = ""
                if name.lower() == "sha":
                    type = "sha1"
                elif name.lower() == "md5":
                    type = "md5"
                    
                if type != "" and checksum == "?":
                    try:
                        if binascii.hexlify(binascii.a2b_base64(value)).lower() == checksums[type].lower():
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
