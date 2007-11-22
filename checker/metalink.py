#!/usr/bin/env python
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007, Neil McNab
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
#   Command line application that checks or downloads metalink files.
#
# Instructions:
#   1. You need to have Python installed.
#   2. Run on the command line using: python metalink.py
#
#   usage: metalink.py [options]
#
#   options:
#     -h, --help            show this help message and exit
#     -d, --download        Actually download the file(s) in the metalink
#     -f FILE, --file=FILE  Metalink file to check
#     -t TIMEOUT, --timeout=TIMEOUT
#                           Set timeout in seconds to wait for response
#                           (default=10)
#
# CHANGELOG:
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
########################################################################

import optparse
import urllib2
import urlparse
import sha
import md5
import os.path
import xml.dom.minidom
import random
import sys
import httplib
import re
import socket

VERSION="Metalink Checker Version 1.3.1"

def run():
    '''
    Start a console version of this application.
    '''
    # Command line parser options.
    parser = optparse.OptionParser(version=VERSION)
    parser.add_option("--download", "-d", action="store_true", dest="download", help="Actually download the file(s) in the metalink")
    parser.add_option("--file", "-f", dest="filevar", metavar="FILE", help="Metalink file to check")
    parser.add_option("--timeout", "-t", dest="timeout", metavar="TIMEOUT", help="Set timeout in seconds to wait for response (default=10)")
    
    (options, args) = parser.parse_args()

    if options.filevar == None:
        parser.print_help()
        return

    socket.setdefaulttimeout(10)
    if options.timeout != None:
        socket.setdefaulttimeout(int(options.timeout))
    
    if options.download:
        progress = ProgressBar(55)
        download_metalink(options.filevar, os.getcwd(), handler=progress.download_update)
        progress.download_end()
    else:
        results = check_metalink(options.filevar)
        print_totals(results)

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
    '''
    src = complete_url(src)
    datasource = urllib2.urlopen(src)
    try:
        dom2 = xml.dom.minidom.parse(datasource)   # parse an open file
    except:
        print "ERROR parsing XML."
        raise
    datasource.close()
    
    urllist = get_subnodes(dom2, ["metalink", "files", "file"])
    if len(urllist) == 0:
        print "No urls to download file from."
        return False

    results = {}
    for filenode in urllist:
        try:
            size = get_xml_tag_strings(filenode, ["size"])[0]
        except:
            size = None
        name = get_attr_from_item(filenode, "name")
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
        if line.startswith(name + ": "):
            result = line.split(name + ": ")
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
    urllist = get_subnodes(item, ["resources", "url"])
    if len(urllist) == 0:
        print "No urls to download file from."
        return False
            
    number = 0
    filename = {}
    
    #error = True
    count = 1
    result = {}
    while (count <= len(urllist)):
        filename = urllist[number].firstChild.nodeValue.strip()
        print "-" *79
        print "Checking %s..." % filename
        headers = check_urlretrieve(filename)
        result[filename] = check_process(headers, size)
        print "Response Code: %s\tSize Check: %s" % (result[filename][0], result[filename][1])   
        #error = not result
        number = (number + 1) % len(urllist)
        count += 1
        
    return result

def check_urlretrieve(url):
    '''
    modernized replacement for urllib.urlretrieve() for use with proxy
    '''
    try:
        temp = urllib2.urlopen(url)
    except urllib2.HTTPError, error:
        return "Response: %s" % error.code
    except (urllib2.URLError, httplib.InvalidURL):
        if url.startswith("rsync://"):
            return "Response: ?"
        return "Response: Bad URL"
    except IOError, error:
        if error.errno == "ftp error":
            code = error.strerror
            result = re.compile("^([0-9]+)").search(str(error.strerror))
            if result != None:
		code = result.group(1)
            result = re.compile("^\(([0-9]+)").search(str(error.strerror))
            if result != None:
		if result.group(1) == "110":
                    code = "timed out"
            return "Response: %s" % code
    headers = temp.info()
    temp.close()

    return headers

#########################################

############# download functions #############

def download(src, path, filemd5="", filesha1="", force = False, handler = None):
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
    '''

    if src.endswith(".metalink"):
        return download_metalink(src, path, force, handler)
    else:
        # parse out filename portion here
        filename = os.path.basename(src)
        result = download_file(src, os.path.join(path, filename), filemd5, filesha1, force, handler)
        if result:
            return [result]
        return False

def download_file(remote_file, local_file, filemd5="", filesha1="", force = False, handler = None):
    '''
    Download a file.
    First parameter, file to download, URL or file path to download from
    Second parameter, file path to save to
    Third parameter, optional, expected MD5SUM
    Fourth parameter, optional, expected SHA1SUM
    Fifth parameter, optional, force a new download even if a valid copy already exists
    Sixth parameter, optional, progress handler callback
    Returns file path if download is successful
    Returns False otherwise (checksum fails)
    '''
    if os.path.exists(local_file) and (not force) and verify_checksum(local_file, filemd5, filesha1):
        return local_file

    remote_file = complete_url(remote_file)

    directory = os.path.dirname(local_file)
    if not os.path.isdir(directory):
        os.makedirs(directory)
                
    #print "Downloading: %s" % remote_file
    
    try:
        urlretrieve(remote_file, local_file, handler)
    except:
        #print "WARNING: Downloading file %s failed." % local_file
        return False

    if verify_checksum(local_file, filemd5, filesha1):
        return local_file
    
    return False

def download_metalink(src, path, force = False, handler = None):
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
    datasource = urllib2.urlopen(src)
    dom2 = xml.dom.minidom.parse(datasource)   # parse an open file
    datasource.close()
    
    urllist = get_subnodes(dom2, ["metalink", "files", "file"])
    if len(urllist) == 0:
        #print "No urls to download file from."
        return False

    results = []
    for filenode in urllist:
        result = download_file_node(filenode, path, force, handler)
        if result:
            results.append(result)

    return results

def download_file_node(item, path, force = False, handler = None):
    '''
    Downloads a specific version of a program
    First parameter, file XML node
    Second parameter, file path to save to
    Third parameter, optional, force a new download even if a valid copy already exists
    Fouth parameter, optional, progress handler callback
    Returns list of file paths if download(s) is successful
    Returns False otherwise (checksum fails)
    '''

    urllist = get_subnodes(item, ["resources", "url"])
    if len(urllist) == 0:
        print "No urls to download file from."
        return False
            
    hashlist = get_subnodes(item, ["verification", "hash"])
    
    hashes = {}
    hashes['md5'] = ""
    hashes['sha1'] = ""
    for hashitem in hashlist:
        hashes[get_attr_from_item(hashitem, "type")] = hashitem.firstChild.nodeValue.strip()
##        for i in range(hashitem.attributes.length):
##            if hashitem.attributes.item(i).name == "type":
##                hashes[hashitem.attributes.item(i).value] = hashitem.firstChild.nodeValue.strip()

    local_file = get_attr_from_item(item, "name")
    localfile = path_join(path, local_file)
    # choose a random url tag to start with
    number = int(random.random() * len(urllist))
    
    error = True
    count = 1   
    while (error and (count <= len(urllist))):
        result = download_file(urllist[number].firstChild.nodeValue.strip(), localfile, hashes['md5'], hashes['sha1'], force, handler)
        error = not result
        number = (number + 1) % len(urllist)
        count += 1
        
    return result

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
    block_size = 4096
    i = 0
    counter = 0
    temp = urllib2.urlopen(url)
    headers = temp.info()
    
    try:
        size = int(headers['Content-Length'])
    except KeyError:
        size = 0

    data = open(filename, 'wb')
    block = True
    
    while block:
        block = temp.read(block_size)
        data.write(block)
        i += block_size
        counter += 1
        if reporthook != None:
            #print counter, block_size, size
            reporthook(counter, block_size, size)
            
    data.close()
    temp.close()

    return (filename, headers)

def verify_checksum(local_file, filemd5="", filesha1=""):
    '''
    Verify the checksum of a file
    First parameter, filename
    Second parameter, optional, expected MD5SUM
    Third parameter, optional, expected SHA1SUM
    Returns True if first checksum provided is valid
    Returns True if no checksums are provided
    Returns False otherwise
    '''
    if filesha1 != "":
        if sha1sum(local_file) == filesha1.lower():
            return True
    elif filemd5 != "":
        if md5sum(local_file) == filemd5.lower():
            return True
    else:
        # No checksum provided, assume OK
        return True
    
    # checksum failed here
    print "ERROR: checksum failed for %s." % local_file
    return False

def remote_or_local(name):
    '''
    Returns if the file path is a remote file or a local file
    First parameter, file path
    Returns "REMOTE" or "LOCAL" based on the file path
    '''
    #transport = urlparse.urlparse(name).scheme
    transport = get_transport(name)
        
    if transport != "":
        return "REMOTE"
    return "LOCAL"

def get_transport(url):
    '''
    Gets transport type.  This is more accurate than the urlparse module which
    just does a split on colon.
    First parameter, url
    Returns the transport type
    '''
    result = url.split("://", 1)
    if len(result) == 1:
        transport = ""
    else:
        transport = result[0]
    return transport

def sha1sum(thisfile):
    '''
    First parameter, filename
    Returns SHA1 sum as a string of hex digits
    '''
    filehandle = open(thisfile, "rb")
    filesha = sha.new()

    data = filehandle.read()
    while(data != ""):
        filesha.update(data)
        data = filehandle.read()

    filehandle.close()
    return filesha.hexdigest()

def md5sum(thisfile):
    '''
    First parameter, filename
    Returns MD5 sum as a string of hex digits
    '''
    filehandle = open(thisfile, "rb")
    filemd5 = md5.new()

    data = filehandle.read()
    while(data != ""):
        filemd5.update(data)
        data = filehandle.read()

    filehandle.close()
    return filemd5.hexdigest()

def path_join(first, second):
    '''
    A function that is called to join two paths, can be URLs or filesystem paths
    Parameters, two paths to be joined
    Returns new URL or filesystem path
    '''
    if first == "":
        return second
    if remote_or_local(second) == "REMOTE":
        return second

    if remote_or_local(first) == "REMOTE":
        if remote_or_local(second) == "LOCAL":
            return urlparse.urljoin(first, second)
        return second

    return os.path.normpath(os.path.join(first, second))

############ XML calls ###########################

def get_child_nodes(rootnode, subtag):
    '''
    Extract specific child tag names.
    First parameter, XML node
    Second parameter, name (string) of child node(s) to look for
    Returns a list of child nodes
    '''
    children = []
    for childnode in rootnode.childNodes:
        if childnode.nodeName == subtag:
            children.append(childnode)
            
    return children

def get_subnodes(rootnode, subtags):
    '''
    First parameter, XML node
    Second parameter, tree in array form for names (string) of child node(s) to look for
    Returns a list of child nodes (searched recursively)
    '''
    children = []
    child_nodes = get_child_nodes(rootnode, subtags[0])
    if (len(subtags) == 1):
        return child_nodes
    
    for child in child_nodes:
        child_nodes = get_subnodes(child, subtags[1:])
        children.extend(child_nodes)
        
    return children

def get_texttag_values(xmlfile, tag):
    '''
    Get values for selected tags in an XML file
    First parameter, XML file to parse
    Second parameter, tag to search for in XML file
    Returns a list of text values found
    '''
    looking_for = []
    try:
        datasource = open(xmlfile)
    except IOError:
        return looking_for

    dom2 = xml.dom.minidom.parse(datasource)   # parse an open file
    datasource.close()
    return get_xml_tag_strings(dom2, tag)

def get_tags(xmlfile, tag):
    looking_for = []
    try:
        datasource = open(xmlfile)
    except IOError:
        return looking_for

    dom2 = xml.dom.minidom.parse(datasource)   # parse an open file
    datasource.close()
    return get_subnodes(dom2, tag)

def get_xml_tag_strings(item, tag):
    '''
    Converts an XML node to a list of text for specified tag
    First parameter, XML node object
    Second parameter, tag tree names to search for
    Returns a list of text value for this tag
    '''   
    return get_xml_item_strings(get_subnodes(item, tag))

def get_xml_item_strings(items):
    '''
    Converts XML nodes to text
    First parameter, list of XML Node objects
    Returns, list of strings as extracted from text nodes in items
    '''
    stringlist = []
    for myitem in items:
        stringlist.append(myitem.firstChild.nodeValue.strip())
    return stringlist

def get_attr_from_item(item, name):
    '''
    Extract the attribute from the XML node
    First parameter, item XML node
    Returns value of the attribute
    '''
    local_file = ""

    for i in range(item.attributes.length):
        if item.attributes.item(i).name == name:
            local_file = item.attributes.item(i).value
            
    return local_file

###################################################

class ProgressBar:
    def __init__(self, length = 68):
        self.length = length
        self.update(0, 0)
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
        print ""

    def download_end(self):
        self.download_update(1, self.total_size, self.total_size)
        print ""

if __name__ == "__main__":
    run()
