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
#import xml.dom.minidom
import random
import sys
import re
import socket
import base64
import hashlib
import httplib
import ftplib

import xmlutils
import download

import locale
import gettext

MAX_REDIRECTS = 20

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
    t = gettext.translation(base, localedir, [locale.getdefaultlocale()[0]], None, 'en')
    return t.ugettext

_ = translate()

def check_metalink(src):
    '''
    Decode a metalink file, can be local or remote
    First parameter, file to download, URL or file path to download from
    Returns the results of the check in a dictonary
    '''
    src = download.complete_url(src)
    datasource = urllib2.urlopen(src)
    try:
        #dom2 = xml.dom.minidom.parse(datasource)   # parse an open file
        metalink = xmlutils.Metalink()
        metalink.parsehandle(datasource)
    except:
        print _("ERROR parsing XML.")
        raise
    datasource.close()
    
##    metalink_node = xmlutils.get_subnodes(dom2, ["metalink"])
##    try:
##        metalink_type = get_attr_from_item(metalink_node, "type")
##    except:
##        metalink_type = None

    if metalink.type == "dynamic":
        #origin = get_attr_from_item(metalink_node, "origin")
        origin = metalink.origin
        if origin != src:
            return check_metalink(origin)
    
    #urllist = xmlutils.get_subnodes(dom2, ["metalink", "files", "file"])
    urllist = metalink.files
    if len(urllist) == 0:
        print _("No urls to download file from.")
        return False

    results = {}
    for filenode in urllist:
        size = filenode.size
##        try:
##            size = xmlutils.get_xml_tag_strings(filenode, ["size"])[0]
##        except:
##            size = None
        #name = xmlutils.get_attr_from_item(filenode, "name")
        name = filenode.filename
        print "=" * 79
        print _("File") + ": %s " % name + _("Size") + ": %s" % size
        results[name] = check_file_node(filenode)

    return results

def check_process(headers, filesize):
    size = "?"
    
    sizeheader = get_header(headers, "Content-Length")

    if sizeheader != None and filesize != None:
        if sizeheader == filesize:
            size = _("OK")
        else:
            size = _("FAIL")

    response_code = _("OK")
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
##    try:
##        size = get_xml_tag_strings(item, ["size"])[0]
##    except:
##        size = None
    size = item.size
    #urllist = xmlutils.get_subnodes(item, ["resources", "url"])
    urllist = item.resources
    if len(urllist) == 0:
        print _("No urls to download file from.")
        return False
            
    number = 0
    filename = {}

    count = 1
    result = {}
    while (count <= len(urllist)):
        filename = urllist[number].url
        print "-" *79
        print _("Checking") + ": %s" % filename
        checker = URLCheck(filename)
        headers = checker.info()
        result[checker.geturl()] = check_process(headers, size)
        print _("Response Code") + ": %s\t" % result[checker.geturl()][0] + _("Size Check") + ": %s" % result[checker.geturl()][1]
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
                self.infostring += _("Response") + ": " + _("Bad URL") + "\r\n"
                return
    
            conn = download.HTTPConnection(urlparts.hostname, port)
            try:
                conn.request("HEAD", url)
            except socket.error, error:
                self.infostring += _("Response") + ": " + _("Connection Error") + "\r\n"
                return
                
            resp = conn.getresponse()
            
            # handle redirects here and set self.url
            count = 0
            while (resp.status == httplib.MOVED_PERMANENTLY or resp.status == httplib.FOUND) and count < MAX_REDIRECTS:
                url = resp.getheader("location")
                print _("Redirected") + ": %s" % url
                conn.close()
                urlparts = urlparse.urlparse(url)
                # need to set default port here
                port = httplib.HTTP_PORT
                if urlparts.port != None:
                    port = urlparts.port
                
                conn = download.HTTPConnection(urlparts.hostname, urlparts.port)
                conn.request("HEAD", url)
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
                conn.request("HEAD", url)
            except socket.error, error:
                #dir(error)
                self.infostring += _("Response") + ": " + _("Connection Error") + "\r\n"
                return
                
            resp = conn.getresponse()
            
            # handle redirects here and set self.url
            count = 0
            while (resp.status == httplib.MOVED_PERMANENTLY or resp.status == httplib.FOUND) and count < MAX_REDIRECTS:
                url = resp.getheader("location")
                print _("Redirected") + ": %s" % url
                conn.close()
                urlparts = urlparse.urlparse(url)
                # need to set default port here
                port = httplib.HTTPS_PORT
                if urlparts.port != None:
                    port = urlparts.port
                
                conn = download.HTTPSConnection(urlparts.hostname, urlparts.port)
                conn.request("HEAD", url)
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

            try:
                ftpobj.login(username, password)
            except (ftplib.error_perm), error:
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
