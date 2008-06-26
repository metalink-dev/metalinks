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
########################################################################
import logging

#import utils
import urllib2
import urlparse
import hashlib
import os.path
import xml.dom.minidom
import xmlutils
import locale
import threading
import time
import copy
import socket
import ftplib
import httplib
import GPG
#import logging
import base64
import sys
import gettext

USER_AGENT = "Metalink Checker/4.0 +http://www.nabber.org/projects/"

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

# Protocols to use for segmented downloads
PROTOCOLS=("http","https","ftp")
#PROTOCOLS=("ftp")

# See http://www.poeml.de/transmetalink-test/README
MIME_TYPE = "application/metalink+xml"

if os.environ.has_key('http_proxy') and HTTP_PROXY == "":
    HTTP_PROXY=os.environ['http_proxy']
if os.environ.has_key('ftp_proxy') and FTP_PROXY == "":
    HTTP_PROXY=os.environ['ftp_proxy']
if os.environ.has_key('https_proxy') and HTTPS_PROXY == "":
    HTTP_PROXY=os.environ['https_proxy']

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

class URL:
    def __init__(self, url, location = "", preference = "", maxconnections = ""):
        if preference == "":
            preference = 1
        if maxconnections == "":
            maxconnections = 1
        
        self.url = url
        self.location = location
        self.preference = int(preference)
        self.maxconnections = int(maxconnections)

import StringIO
import gzip

class DecompressFile(gzip.GzipFile):
    def __init__(self, fp):
        self.fp = fp
        self.geturl = fp.geturl

        compressed = StringIO.StringIO(fp.read())
        gzip.GzipFile.__init__(self, fileobj=compressed)
    
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
    
def urlopen(url, data = None, metalink=False):
    #print "URLOPEN:", url
    url = complete_url(url)
    req = urllib2.Request(url, data)
    req.add_header('User-agent', USER_AGENT)
    req.add_header('Cache-Control', "no-cache")
    req.add_header('Pragma', "no-cache")
    req.add_header('Accept-Encoding', 'gzip')
    if metalink:
        req.add_header('Accept', MIME_TYPE + ", */*")

    fp = urllib2.urlopen(req)
    try:
        if fp.headers['Content-Encoding'] == "gzip":
            return DecompressFile(fp)
    except KeyError: pass
    #print fp.info()
    #print fp.read()
    return fp

def urlhead(url, metalink=False):
    '''
    raise IOError for example if the URL does not exist
    '''
    url = complete_url(url)
    req = urllib2.Request(url, None)
    req.add_header('User-agent', USER_AGENT)
    req.add_header('Cache-Control', "no-cache")
    req.add_header('Pragma', "no-cache")
    if metalink:
        req.add_header('Accept', MIME_TYPE + ", */*")

    req.get_method = lambda: "HEAD"
    logging.debug(url)
    fp = urllib2.urlopen(req)
    headers = fp.headers
    fp.close()
    return headers

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

def get(src, path, checksums = {}, force = False, handler = None, segmented = SEGMENTED):
    '''
    Download a file, decodes metalinks.
    First parameter, file to download, URL or file path to download from
    Second parameter, file path to save to
    Third parameter, optional, expected MD5SUM
    Fourth parameter, optional, expected SHA1SUM
    Fifth parameter, optional, force a new download even if a valid copy already exists
    Sixth parameter, optional, progress handler callback
    Returns list of file paths if download(s) is successful
    Returns False otherwise (checksum fails)
    raise socket.error e.g. "Operation timed out"
    '''
    # assume metalink if ends with .metalink
    if src.endswith(".metalink"):
        return download_metalink(src, path, force, handler, segmented)
    else:
        # not all servers support HEAD where GET is also supported
        # also a WindowsError is thrown if a local file does not exist
        try:
            # add head check for metalink type, if MIME_TYPE or application/xml? treat as metalink
            if urlhead(src, metalink=True)["content-type"].startswith(MIME_TYPE):
                print _("Metalink content-type detected.")
                return download_metalink(src, path, force, handler, segmented)
        except IOError, e:
            pass
        except WindowsError, e:
            pass
            
    # assume normal file download here
    # parse out filename portion here
    filename = os.path.basename(src)
    result = download_file(src, os.path.join(path, filename), 
            0, checksums, force, handler, segmented = segmented)
    if result:
        return [result]
    return False
    
def download_file(url, local_file, size=0, checksums={}, force = False, 
        handler = None, segmented = SEGMENTED, chunksums = {}, chunk_size = None):
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
    urllist = {}
    urllist[url] = URL(url)
    return download_file_urls(urllist, local_file, size, checksums, force, handler, segmented, chunksums, chunk_size)
    
    
#class Download:
    #def __init__(self, urllist, local_file, size=0, checksums={}, force = False, 
            #handler = None, segmented = SEGMENTED, chunksums = {}, chunk_size = None):
        #pass
    
    #def set_cancel_callback(self, callback):
        #self.cancel_callback(self, 
    
def download_file_urls(urllist, local_file, size=0, checksums={}, force = False, 
            handler = None, segmented = SEGMENTED, chunksums = {}, chunk_size = None):
    '''
    Download a file.
    urllist {string->URL} file to download, URL or file path to download from
    Second parameter, file path to save to
    Third parameter, optional, expected file size
    Fourth parameter, optional, expected checksum dictionary
    Fifth parameter, optional, force a new download even if a valid copy already exists
    Sixth parameter, optional, progress handler callback
    Returns file path if download is successful
    Returns False otherwise (checksum fails)    
    '''
    assert isinstance(urllist, dict)
    
    print ""
    print _("Downloading to %s.") % local_file
        
    if os.path.exists(local_file) and (not force) and len(checksums) > 0:
        checksum = verify_checksum(local_file, checksums)
        if checksum:
            actsize = size
            if actsize == 0:
                actsize = os.stat(local_file).st_size
            if actsize != 0:
                if handler != None:
                    handler(1, actsize, actsize)
                return local_file
        else:
            print _("Checksum failed, retrying download of %s.") % os.path.basename(local_file)

    directory = os.path.dirname(local_file)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    if chunk_size == None:
        chunk_size = DEFAULT_CHUNK_SIZE

    seg_result = False
    if segmented:
        manager = Segment_Manager(urllist, local_file, size, checksums = checksums, chunksums = chunksums, chunk_size = int(chunk_size))
        manager.set_status_callback(handler)
        seg_result = manager.run()
        
        if not seg_result:
            #seg_result = verify_checksum(local_file, checksums)
            print "\n" + _("Could not download all segments of the file, trying one mirror at a time.")

    if (not segmented) or (not seg_result):
        manager = NormalManager(urllist, local_file, size, checksums = checksums, chunksums = chunksums, chunk_size = int(chunk_size))
        manager.set_status_callback(handler)
        manager.run()
        
    if manager.get_status():
        return local_file
    return False
            
class Manager:
    def __init__(self):
        self.cancel_handler = None
        self.pause_handler = None
        self.status_handler = None
        self.status = True
        self.end_bitrate()
        
    def set_cancel_callback(self, handler):
        self.cancel_handler = handler
        
    def set_pause_callback(self, handler):
        self.pause_handler = handler
        
    def set_status_callback(self, handler):
        self.status_handler = handler

    def run(self, wait=None):
        result = True
        while result:
            if self.pause_handler != None and self.pause_handler():
                self.end_bitrate()
                time.sleep(1)
            else:
                if wait != None:
                    time.sleep(wait)
                result = self.cycle()
            
        return self.get_status()
         
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
        if self.oldtime != None:
            return ((bytes - self.oldsize) * 8 / 1024)/(time.time() - self.oldtime)
        return None
            
class NormalManager(Manager):
    def __init__(self, urllist, local_file, size, checksums, chunksums, chunk_size):
        Manager.__init__(self)
        self.local_file = local_file
        self.size = size
        self.chunksums = chunksums
        self.checksums = checksums
        self.urllist = start_sort(urllist)
        self.start_number = 0
        self.number = 0
        self.count = 1

    def random_start(self):
        # do it the old way
        # choose a random url tag to start with
        #urllist = list(urllist)
        #number = int(random.random() * len(urllist))
        self.start_number = int(random.random() * len(self.urllist))
        self.number = self.start_number
        
    def cycle(self):
        try:
            self.status = True
            remote_file = complete_url(self.urllist[self.number])

            manager = URLManager(remote_file, self.local_file, self.checksums)
            manager.set_status_callback(self.status_handler)
            manager.set_cancel_callback(self.cancel_handler)
            manager.set_pause_callback(self.pause_handler)
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
    def __init__(self, remote_file, filename, checksums = {}):
        '''
        modernized replacement for urllib.urlretrieve() for use with proxy
        '''
        Manager.__init__(self)
        self.filename = filename
        self.checksums = checksums
        self.block_size = 1024
        self.counter = 0
        self.temp = urlopen(remote_file)
        headers = self.temp.info()
        
        try:
            self.size = int(headers['Content-Length'])
        except KeyError:
            self.size = 0
    
        self.data = open(filename, 'wb')

    ### FIXME need to check contents from previous download here
        self.resume = FileResume(filename + ".temp")
        self.resume.add_block(0)
        
    def close_handler(self):
        self.resume.complete()
        self.data.close()
        self.temp.close()
        if self.status:
            self.status = filecheck(self.filename, self.checksums, self.size)
            
    def cycle(self):
        if self.oldtime == None:
            self.start_bitrate(self.counter * self.block_size)
        if self.cancel_handler != None and self.cancel_handler():
            self.close_handler()
            return False
        
        block = self.temp.read(self.block_size)
        self.data.write(block)
        self.counter += 1

        self.resume.set_block_size(self.counter * self.block_size)
                        
        if self.status_handler != None:
            self.status_handler(self.counter, self.block_size, self.size)

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

def download_metalink(src, path, force = False, handler = None, segmented = SEGMENTED):
    '''
    Decode a metalink file, can be local or remote
    First parameter, file to download, URL or file path to download from
    Second parameter, file path to save to
    Third parameter, optional, force a new download even if a valid copy already exists
    Fouth parameter, optional, progress handler callback
    Returns list of file paths if download(s) is successful
    Returns False otherwise (checksum fails)
    '''
    src = complete_url(src)
    try:
        datasource = urlopen(src, metalink=True)
    except:
        return False
    dom2 = xml.dom.minidom.parse(datasource)   # parse an open file
    datasource.close()

    metalink_node = xmlutils.get_subnodes(dom2, ["metalink"])
    try:
        metalink_type = xmlutils.get_attr_from_item(metalink_node[0], "type")
    except AttributeError:
        metalink_type = None

    if metalink_type == "dynamic":
        origin = xmlutils.get_attr_from_item(metalink_node[0], "origin")
        if origin != src and origin != "":
            print _("Downloading update from %s") % origin
            return download_metalink(origin, path, force, handler, segmented)
    
    urllist = xmlutils.get_subnodes(dom2, ["metalink", "files", "file"])
    if len(urllist) == 0:
        print _("No urls to download file from.")
        return False

    results = []
    for filenode in urllist:
        ostag = xmlutils.get_xml_tag_strings(filenode, ["os"])
        langtag = xmlutils.get_xml_tag_strings(filenode, ["language"])
            
        if OS == None or len(ostag) == 0 or ostag[0].lower() == OS.lower():
            if "any" in LANG or len(langtag) == 0 or langtag[0].lower() in LANG:
                result = download_file_node(filenode, path, force, handler, segmented)
                if result:
                    results.append(result)
    if len(results) == 0:
        return False
    
    return results

def download_file_node(item, path, force = False, handler = None, segmented=SEGMENTED):
    '''
    Downloads a specific version of a program
    First parameter, file XML node
    Second parameter, file path to save to
    Third parameter, optional, force a new download even if a valid copy already exists
    Fouth parameter, optional, progress handler callback
    Returns list of file paths if download(s) is successful
    Returns False otherwise (checksum fails)
    raise socket.error e.g. "Operation timed out"
    '''

    # unused: urllist = xmlutils.get_xml_tag_strings(item, ["resources", "url"])
    urllist = {}
    for node in xmlutils.get_subnodes(item, ["resources", "url"]):
        url = xmlutils.get_xml_item_strings([node])[0]
        location = xmlutils.get_attr_from_item(node, "location")
        preference = xmlutils.get_attr_from_item(node, "preference")
        maxconnections = xmlutils.get_attr_from_item(node, "maxconnections")
        urllist[url] = URL(url, location, preference, maxconnections)
        
    if len(urllist) == 0:
        print _("No urls to download file from.")
        return False
            
    hashlist = xmlutils.get_subnodes(item, ["verification", "hash"])
    try:
        size = xmlutils.get_xml_tag_strings(item, ["size"])[0]
    except:
        size = 0
    
    hashes = {}
    for hashitem in hashlist:
        hashes[xmlutils.get_attr_from_item(hashitem, "type")] = hashitem.firstChild.nodeValue.strip()

    sigs = xmlutils.get_subnodes(item, ["verification", "signature"])
    for sig in sigs:
        hashes[xmlutils.get_attr_from_item(sig, "type")] = sig.firstChild.nodeValue.strip()

    local_file = xmlutils.get_attr_from_item(item, "name")
    localfile = path_join(path, local_file)

    #extract chunk checksum information
    try:
        chunksize = int(xmlutils.get_attr_from_item(xmlutils.get_subnodes(item, ["verification", "pieces"])[0], "length"))
    except IndexError:
        chunksize = None

    chunksums = {}
    for piece in xmlutils.get_subnodes(item, ["verification", "pieces"]):
        hashtype = xmlutils.get_attr_from_item(piece, "type")
        chunksums[hashtype] = []
        for chunk in xmlutils.get_xml_tag_strings(piece, ["hash"]):
            chunksums[hashtype].append(chunk)

    return download_file_urls(urllist, localfile, size, hashes, force, handler, segmented, chunksums, chunksize)

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

def urlretrieve(url, filename, reporthook = None):
    '''
    modernized replacement for urllib.urlretrieve() for use with proxy
    '''
    block_size = 1024
    i = 0
    counter = 0
    temp = urlopen(url)
    headers = temp.info()
    
    try:
        size = int(headers['Content-Length'])
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
    def __init__(self, urls, localfile, size=0, checksums = {}, chunk_size = DEFAULT_CHUNK_SIZE, chunksums = {}):
        assert isinstance(urls, dict)
        Manager.__init__(self)
                
        self.sockets = []
        self.chunks = []
        self.limit_per_host = LIMIT_PER_HOST
        self.host_limit = HOST_LIMIT
        self.size = int(size)
        self.orig_urls = urls
        self.urls = urls
        self.chunk_size = int(chunk_size)
        self.chunksums = chunksums
        self.checksums = checksums
        self.localfile = localfile
        self.filter_urls()
        
        self.status = True
        self.cancel_callback = None
        
        # Open the file.
        try:
            self.f = ThreadSafeFile(localfile, "rb+")
        except IOError:
            self.f = ThreadSafeFile(localfile, "wb+")
            
        self.resume = FileResume(localfile + ".temp")

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
            
    def run(self):
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
            
        return Manager.run(self, 0.1)
        

    def cycle(self):
        '''
        Runs one cycle
        Returns True if still downloading, False otherwise
        '''
        try:
            bytes = self.byte_total()
            if self.oldtime == None:
                self.start_bitrate(bytes)
                
            # cancel was pressed here
            if self.cancel_callback != None and self.cancel_callback():
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
        next = self.next_url()
        
        if next == None:
            return
        
        index = self.get_chunk_index()
        if index != None:
            if self.status_handler != None:
                self.status_handler(int(self.byte_total()/self.chunk_size), self.chunk_size, self.size)
            
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

        #try:
        size = os.stat(self.localfile).st_size
        if size == 0:
            os.remove(self.localfile)
            os.remove(self.localfile + ".temp")
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
        #lock = threading.Lock()
        #lock.acquire()

        self.mem.acquire()
        self.mem.seek(self.byte_start, 0)
        chunkstring = self.mem.read(self.byte_count)
        self.mem.release()

        return verify_chunk_checksum(chunkstring, self.checksums)

    def close(self):
        if self.error != None:
            self.host.close()

        self.host.set_active(False)

    def end(self):
        if not self.checksum():
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

            #lock = threading.Lock()
            #lock.acquire()
            self.mem.acquire()
            self.mem.seek(self.byte_start, 0)
            self.mem.write(tempbuffer)
            self.mem.flush()

            self.mem.release()
        
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
                self.host.conn.request("GET", self.url, "", {"Range": "bytes=%lu-%lu\r\n" % (self.byte_start, self.byte_end - 1)})
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

        self.mem.acquire()
        self.mem.seek(self.byte_start + self.bytes, 0)
        self.mem.write(body)
        self.mem.flush()
        self.mem.release()
        
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

