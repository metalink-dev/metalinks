#!/usr/bin/env python
########################################################################
#
# Project: Metalink Checker
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2007-2008, Hampus Wessman, Neil McNab
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
import xml.parsers.expat

# for jigdo only
import gzip
#import ConfigParser
import base64
import StringIO

current_version = "1.1.0"

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

class MetalinkFile:
    def __init__(self, filename, attrs = {}):
        self.filename = filename
        self.errors = []
#        self.hash_md5 = ""
#        self.hash_sha1 = ""
#        self.hash_sha256 = ""
        self.hashlist = {}
        self.pieces = []
        self.piecelength = 0
        self.piecetype = ""
        self.resources = []
        self.language = ""
        self.os = ""
        self.size = 0
        self.maxconnections = ""
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

    def compare_checksums(self, checksums):
        for key in ("sha512","sha384","sha256","sha1","md5"):
            try:
                if self.hashlist[key].lower() == checksums[key].lower():
                    return True
            except KeyError: pass
        return False

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
        
    def add_url(self, url, type="default", location="", preference="", conns="", attrs={}):
        self.resources.append(Resource(url, type, location, preference, conns, attrs))
    
    def add_res(self, res):
        self.resources.append(res)

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
            #if self.hashlist["md5"].strip() != "":
            #    text += '        <hash type="md5">'+self.hashlist["md5"].lower()+'</hash>\n'
            #if self.hashlist["sha1"].strip() != "":
            #    text += '        <hash type="sha1">'+self.hashlist["sha1"].lower()+'</hash>\n'
            #if self.self.hashlist["sha256"].strip() != "":
            #    text += '        <hash type="sha256">'+self.hashlist["sha256"].lower()+'</hash>\n'
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
            details = ''
            if res.location.strip() != "":
                details += ' location="'+res.location.lower()+'"'
            if res.preference.strip() != "": details += ' preference="'+res.preference+'"'
            if res.maxconnections.strip() != ""and res.maxconnections.strip() != "-" : details += ' maxconnections="'+res.maxconnections+'"'
            text += '        <url type="'+res.type+'"'+details+'>'+res.url+'</url>\n'
        text += '      </resources>\n'
        text += '    </file>\n'
        return text

class XMLTag:
    def __init__(self, name, attrs={}):
        self.name = name
        self.attrs = attrs

    def get_attr(self, name):
        return self.attrs[name]

class Metalink:
    def __init__(self):
        self.errors = []
        self.files = []
        self.identity = ""
        self.publisher_name = ""
        self.publisher_url = ""
        self.copyright = ""
        self.description = ""
        self.license_name = ""
        self.license_url = ""
        self.version = ""
        self.origin = ""
        self.type = ""
        self.upgrade = ""
        self.tags = ""

        self.p = xml.parsers.expat.ParserCreate()
        self.parent = []

        self.p.StartElementHandler = self.start_element
        self.p.EndElementHandler = self.end_element
        self.p.CharacterDataHandler = self.char_data
    
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
            try:
                self.origin = attrs["origin"]
            except KeyError: pass
            try:
                self.type = attrs["type"]
            except KeyError: pass
        
    def end_element(self, name):
        tag = self.parent.pop()

        try:
            if name == "url" and self.parent[-1].name == "resources":
                fileobj = self.files[-1]
                fileobj.add_url(self.data, attrs=tag.attrs)
            elif name == "tags" and self.parent[-1].name != "file":
                setattr(self, "tags", self.data)
            elif name in ("name", "url"):
                setattr(self, self.parent[-1].name + "_" + name, self.data)
            elif name in ("identity", "copyright", "description", "version", "upgrade"):
                setattr(self, name, self.data)
            elif name == "hash" and self.parent[-1].name == "verification":
                hashtype = tag.attrs["type"]
                fileobj = self.files[-1]
                #setattr(fileobj, "hash_" + hashtype, self.data)
                fileobj.hashlist[hashtype] = self.data
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
                fileobj.pieces.append(self.data)
            elif name in ("os", "language", "tags"):
                fileobj = self.files[-1]
                setattr(fileobj, name, self.data)
            elif name in ("size"):
                fileobj = self.files[-1]
                if self.data != "":
                    setattr(fileobj, name, int(self.data))
        except IndexError: pass
            
    def char_data(self, data):
        self.data += data.strip()

    def parsefile(self, filename):
        handle = open(filename, "rb")
        self.parsehandle(handle)
        handle.close()

    def parsehandle(self, handle):
        return self.p.ParseFile(handle)

    def parse(self, text):
        self.p.Parse(text)

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

    def download_size(self):
        total = 0
        for fileobj in self.files:
            total += fileobj.get_size()
        return total

############### Jigdo ######################

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


class Jigdo(Metalink):
    def __init__(self):
        self.template = ""
        self.template_md5 = ""
        self.filename = ""
        Metalink.__init__(self)
        self.p = ParseINI()

    def parsefile(self, filename):
        handle = gzip.open(filename, "rb")
        self.parsehandle(handle)
        handle.close()

    def parsehandle(self, handle):
        # need to gunzip here
        try:
            newhandle = DecompressFile(handle)
            self.p.readfp(newhandle)
        except IOError:
            # file not gzipped
            self.p.readfp(handle)

        self.decode(self.p)

    def parse(self, text):
        raise AssertionError, "Not implemented"

    def decode(self, configobj):
        serverdict = {}
        for item in configobj.items("Servers"):
            serverdict[item[0]] = item[1].split(" ")[0]
        
        for item in configobj.items("Image"):
            if item[0].lower() == "template":
                self.template = item[1]
            if item[0].lower() == "template-md5sum":
                self.template_md5 = self.bin2hex(self.base64hash2bin(item[1]))
            if item[0].lower() == "filename":
                self.filename = item[1]
            if item[0].lower() == "shortinfo":
                self.identity = item[1]
            if item[0].lower() == "info":
                self.description = item[1]
                
        for item in configobj.items("Parts"):
            base64hash = item[0]
            binaryhash = self.base64hash2bin(base64hash)
            url = item[1]
            parts = url.split(":", 1)
            if len(parts) == 1:
                url = parts[0]
                local = parts[0]
            else:
                url = serverdict[parts[0]] + parts[1]
                local = parts[1]
            myfile = MetalinkFile(local)
            myfile.add_url(url)
            #print self.bin2hex(binaryhash)
            myfile.add_checksum("md5", self.bin2hex(binaryhash))
            self.files.append(myfile)

    def base64hash2bin(self, base64hash):
        # need to pad hash out to multiple of both 6 (base 64) and 8 bits (1 byte characters)
        return base64.b64decode(base64hash + "AA", "-_")[:-2]
    
    def bin2hex(self, string):
        text = ""
        for char in string:
            text += "%.2x" % ord(char)
        return text

class ParseINI(dict):
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
                    self[section].append((parts[0], parts[1]))
            line = fp.readline()

    def items(self, section):
        return self[section]
