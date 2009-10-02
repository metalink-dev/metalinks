#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2009, Hampus Wessman, Neil McNab
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
# Filename: $URL: https://metalinks.svn.sourceforge.net/svnroot/metalinks/checker/xmlutils.py $
# Last Updated: $Date: 2009-06-06 13:06:52 -0700 (Sat, 06 Jun 2009) $
# Author(s): Hampus Wessman, Neil McNab
#
# Description:
#   Functions for accessing XML formatted data.
#
########################################################################

import os
import os.path
import md5
import sha
import re
import math
import time
import rfc822
import calendar
import xml.parsers.expat

# for jigdo only
import gzip

# handle missing module in jython
try: import bz2
except ImportError: pass

import base64
import StringIO
import binascii
import zlib

current_version = "1.1.0"

RFC3339 = "%Y-%m-%dT%H:%M:%SZ"
RFC822 = "%a, %d %b %Y %H:%M:%S +0000"

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
    def __init__(self, filename, attrs = {}):
        self.filename = filename
        self.errors = []
        self.hashlist = {}
        self.pieces = []
        self.piecelength = 0
        self.piecetype = ""
        self.resources = []
        self.language = ""
        self.os = ""
        self.size = 0
        
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

    def validate_url(self, url):
        if url.endswith(".torrent"):
            type = "bittorrent"
        else:
            chars = url.find(":")
            type = url[:chars]
        allowed_types = ["ftp", "ftps", "http", "https", "rsync", "bittorrent", "magnet", "ed2k"]
        if not type in allowed_types:
            return False
        elif type in ['http', 'https', 'ftp', 'ftps', 'bittorrent']:
            m = re.search(r'\w+://.+\..+/.*', url)
            if m == None:
                return False
        return True

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
        md5hash = md5.new()
        sha1hash = sha.new()
        sha256hash = None
        # Try to use hashlib
        try:
            import hashlib
            md5hash = hashlib.md5()
            sha1hash = hashlib.sha1()
            sha256hash = hashlib.sha256()
        except:
            print "Hashlib not available. No support for SHA-256."
        piecehash = sha.new()
        piecenum = 0
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
                    if get_first(result) == False:
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
                        piecehash = sha.new()
                        length = 0
        if use_chunks:
            if length > 0:
                print "Done with piece hash", len(self.pieces)
                self.pieces.append(piecehash.hexdigest())
                piecehash = sha.new()
            print "Total number of pieces:", len(self.pieces)
        fp.close()
        self.hashlist["md5"] = md5hash.hexdigest()
        self.hashlist["sha1"] = sha1hash.hexdigest()
        if sha256hash != None:
            self.hashlist["sha256"] = sha256hash.hexdigest()
        if len(self.pieces) < 2: self.pieces = []
        # Convert to strings
        #self.size = str(self.size)
        #self.piecelength = str(self.piecelength)
        print "done"
        if progresslistener: progresslistener.Update(100)
        return True

class MetalinkFile4(MetalinkFileBase):
    def __init__(self, filename, attrs = {}):
        self.description = ""
        self.identity = ""
        self.license_name = ""
        self.license_url = ""
        self.publisher_name = ""
        self.publisher_url = ""
        self.version = ""
        self.logo = ""
        MetalinkFileBase.__init__(self, filename, attrs)

    def compare_checksums(self, checksums):
        for key in ("sha-512","sha-384","sha-256","sha-1","md5"):
            try:
                if self.hashlist[key].lower() == checksums[key].lower():
                    return True
            except KeyError: pass
        return False
        
    def add_url(self, url, type="", location="", preference="", attrs={}):
        self.resources.append(Resource4(url, type, location, preference, attrs))
    
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
        if self.size != 0:
            text += '      <size>'+str(self.size)+'</size>\n'
        if self.language.strip() != "":
            text += '      <language>'+self.language+'</language>\n'
        if self.os.strip() != "":
            text += '      <os>'+self.os+'</os>\n'
        # Verification
        for key in self.hashlist.keys():
            text += '      <hash type="%s">' % hashlookup(key) + self.hashlist[key].lower() + '</hash>\n'
        if len(self.pieces) > 1:
            text += '      <pieces type="'+hashlookup(self.piecetype)+'" length="'+self.piecelength+'">\n'
            for id in range(len(self.pieces)):
                text += '        <hash>'+self.pieces[id]+'</hash>\n'
            text += '      </pieces>\n'
        # File list
        for res in self.resources:
            text += res.generate()
        text += '  </file>\n'
        return text
        
class MetalinkFile(MetalinkFileBase):
    def __init__(self, filename, attrs = {}):
        self.maxconnections = ""
        MetalinkFileBase.__init__(self, filename, attrs)

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
        if self.size != 0:
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
                text += '        <hash type="%s">' % key + self.hashlist[key].lower() + '</hash>\n'
            if len(self.pieces) > 1:
                text += '        <pieces type="'+self.piecetype+'" length="'+self.piecelength+'">\n'
                for id in range(len(self.pieces)):
                    text += '          <hash piece="'+str(id)+'">'+self.pieces[id]+'</hash>\n'
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
        self.origin = ""
        self.type = ""

        self.p = xml.parsers.expat.ParserCreate()
        self.parent = []

        self.p.StartElementHandler = self.start_element
        self.p.EndElementHandler = self.end_element
        self.p.CharacterDataHandler = self.char_data
            
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
        self.type = ""
        self.upgrade = ""
        self.tags = ""
        self.pubdate = ""
        self.refreshdate = ""
        MetalinkBase.__init__(self)
        
    def generate(self):
        text = '<?xml version="1.0" encoding="utf-8"?>\n'
        origin = ""
        if self.origin.strip() != "":
            origin = 'origin="'+self.origin+'" '
        typetext = ""
        if self.type.strip() != "":
            typetext = 'type="'+self.type+'" '
        text += '<metalink version="3.0" '+origin + typetext +'generator="Metalink Editor version '+current_version+'" xmlns="http://www.metalinker.org/">\n'
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
        tag = self.parent.pop()

        try:
            if name == "url" and self.parent[-1].name == "resources":
                fileobj = self.files[-1]
                fileobj.add_url(self.data.strip(), attrs=tag.attrs)
            elif name == "tags" and self.parent[-1].name != "file":
                setattr(self, "tags", self.data.strip())
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
        self.generator=""
        self.origin=""
        self.published=""
        self.updated=""
        MetalinkBase.__init__(self)

    def generate(self):
        text = '<?xml version="1.0" encoding="utf-8"?>\n'
        text += '<metalink xmlns="urn:ietf:params:xml:ns:metalink">\n'
        if self.origin.strip() != "":
            text += '<origin>'+self.origin+'</origin>\n'
        if self.dynamic.lower() == "true":
            text += '<dynamic>true</dynamic>\n'
       
        for fileobj in self.files:
            text += fileobj.generate_file()
        text += '</metalink>'
        try:
            return text.encode('utf-8')
        except:
            return text.decode('latin1').encode('utf-8')
        
    # handler functions
    def start_element(self, name, attrs):
        xmlns = ""
        self.data = ""
        self.parent.append(XMLTag(name, attrs))
        if name == "file":
            fileobj = MetalinkFile4(attrs["name"], attrs)
            self.files.append(fileobj)
            
        if name == "metalink":
            try:
                xmlns = attrs["xmlns"]
            except KeyError: pass
            if xmlns != "urn:ietf:params:xml:ns:metalink":
                raise AssertionError, "Not a valid Metalink 4 (RFC) file."
        
    def end_element(self, name):
        tag = self.parent.pop()

        try:
            if name in ("dynamic", "generator", "origin", "published", "updated"):
                setattr(self, name, self.data.strip())
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
            try:
                import download
                temp = []
                fp = download.urlopen(self.mirrordict[item[0]])
                line = fp.readline()
                while line:
                    if not line.startswith("#"):
                        temp.append(line.strip())
                    line = fp.readline()
                serverdict[item[0]] = temp
            except ImportError: pass
        
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

    def temp2iso(self):
        '''
        load template into string in memory
        '''
        handle = open(os.path.basename(self.template), "rb")
        
        # read text comments first, then switch to binary data
        data = handle.readline()
        while data.strip() != "":
            data = handle.readline()

        data = handle.read(1024*1024)
        text = ""

        #decompress = bz2.BZ2Decompressor()
        #zdecompress = zlib.decompressobj()
        bzip = False
        gzip = False
        while data:
            if data.startswith("BZIP"):
                bzip = True
                self.compression_type = "BZIP"
                data = data[16:]
            if data.startswith("DATA"):
                gzip = True
                self.compression_type = "GZIP"
                #print self.get_size(data[4:10])
                #print self.get_size(data[10:16])
                data = data[16:]
            if data.startswith("DESC"):
                gzip = False
                bzip = False

            if bzip or gzip:
                #newdata = decompress.decompress(data)
                text += data
                data = handle.read(1024*1024)
            else:
                data = handle.readline()
        handle.close()
        #print text
        return text

    def get_size(self, string):
        total = 0
        for i in range(len(string)):
            temp = ord(string[i]) << (8 * i)
            total += temp
        return total

    def mkiso(self):
        text = self.temp2iso()

        found = {}
        for fileobj in self.files:
            hexhash = fileobj.get_checksums()["md5"]
            loc = text.find(binascii.unhexlify(hexhash))
            if loc != -1:
                if fileobj.filename.find("dists") != -1:
                    print "FOUND:", fileobj.filename
                found[loc] = fileobj.filename

        decompressor = None
        if self.compression_type == "BZIP":
            decompressor = bz2.BZ2Decompressor()
        elif self.compression_type == "GZIP":
            decompressor = zlib.decompressobj()

        handle = open(self.filename, "wb")

        keys = found.keys()
        keys.sort()
        start = 0
        for loc in keys:
            #print start, loc, found[loc]
            #print "Adding %s to image..." % found[loc]
            #sys.stdout.write(".")
            lead = decompressor.decompress(text[start:loc])
            if found[loc].find("dists") != -1:
                print "Writing:", found[loc]
            filedata = open(found[loc], "rb").read()
            handle.write(lead + filedata)
            start = loc + 16

        handle.close()

class ParseINI(dict):
    '''
    Similiar to what is available in ConfigParser, but case sensitive
    '''
    def __init__(self):
        pass

    def readfp(self, fp):
        line = fp.readline()
        section = None
        while line:
            if not line.startswith("#") and line.strip() != "":
                if line.startswith("["):
                    section = line[1:-2]
                    self[section] = []
                else:
                    parts = line.split("=", 1)
                    self[section].append((parts[0], parts[1].strip()))
            line = fp.readline()

    def items(self, section):
        try:
            return self[section]
        except KeyError:
            return []

def convert_4to3(metalinkobj4):
#
# TODO:
#   Detect and convert date formats properly.
    metalinkobj3 = Metalink()
    
    setattr(metalinkobj3, 'origin', getattr(metalinkobj4, 'origin'))
    if getattr(metalinkobj4, 'dynamic').lower() == "true":
        setattr(metalinkobj3, 'type', 'dynamic')
        
    if metalinkobj4.published != "":
        metalinkobj3.pubdate = time.strftime(RFC822, rfc3339_parsedate(metalinkobj4.published))
    if metalinkobj4.updated != "":
        metalinkobj3.refreshdate = time.strftime(RFC822, rfc3339_parsedate(metalinkobj4.updated))
        
    for fileobj4 in metalinkobj4.files:
        fileobj3 = MetalinkFile(fileobj4.filename)
        # copy common attributes
        for attr in ('filename', 'pieces', 'piecelength', 'piecetype', 'language', 'os', 'size'):
            setattr(fileobj3, attr, getattr(fileobj4, attr))
        for attr in ('description', 'identity', 'license_url', 'license_name', 'publisher_url', 'publisher_name'):
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
    setattr(metalinkobj4, 'origin', getattr(metalinkobj3, 'origin'))
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
        for attr in ('description', 'identity', 'license_url', 'license_name', 'publisher_url', 'publisher_name'):
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
    xml = Metalink4()
    try:
        xml.parsehandle(handle)
    except AssertionError:
        handle.seek(0)
        xml = Metalink()
        xml.parsefile(handle)
    xml = convert(xml, ver)
    return xml

#for test in ("2009-05-15T18:30:02Z", "2009-05-15T18:30:02.25Z", "2009-05-15T18:30:02-04:00", "2009-05-15T18:30:02.25-08:00"):
#    run = time.strftime(RFC822, rfc3339_parsedate(test))
#    print test, run
