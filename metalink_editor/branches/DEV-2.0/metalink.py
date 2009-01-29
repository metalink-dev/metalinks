#    Copyright (c) 2007 Hampus Wessman, Sweden.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os, os.path, md5, sha, re, math, time
import xml.parsers.expat

current_version = "1.2.0"

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
        self.hash_md5 = ""
        self.hash_sha1 = ""
        self.hash_sha256 = ""
        self.pieces = []
        self.piecelength = 0
        self.piecetype = ""
        self.resources = []
        self.language = ""
        self.os = ""
        self.size = ""
        self.maxconnections = ""
        for attr in attrs:
            setattr(self, attr, attrs[attr])
    
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
        self.size = os.stat(filename).st_size
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
        self.hash_md5 = md5hash.hexdigest()
        self.hash_sha1 = sha1hash.hexdigest()
        if sha256hash != None:
            self.hash_sha256 = sha256hash.hexdigest()

        # automatically add an ed2k url here
        self.ed2k = compute_ed2k(filename)
        if self.ed2k != "":
            self.add_url(self.ed2k)

        self.sig = read_sig(filename)
            
        if len(self.pieces) < 2: self.pieces = []
        # Convert to strings
        self.size = str(self.size)
        self.piecelength = str(self.piecelength)
        print "done"
        if progresslistener: progresslistener.Update(100)
        return True

    def validate(self):
        valid = True
        if len(self.resources) == 0:
            self.errors.append("You need to add at least one URL!")
            valid = False
        if self.hash_md5.strip() != "":
            m = re.search(r'[^0-9a-fA-F]', self.hash_md5)
            if len(self.hash_md5) != 32 or m != None:
                self.errors.append("Invalid md5 hash.")                    
                valid = False
        if self.hash_sha1.strip() != "":
            m = re.search(r'[^0-9a-fA-F]', self.hash_sha1)
            if len(self.hash_sha1) != 40 or m != None:
                self.errors.append("Invalid sha-1 hash.")
                valid = False
        if self.size.strip() != "":
            try:
                size = int(self.size)
                if size < 0:
                    self.errors.append("File size must be at least 0, not " + self.size + '.')
                    valid = False
            except:
                self.errors.append("File size must be an integer, not " + self.size + ".")
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
        if self.size.strip() != "":
            text += '      <size>'+self.size+'</size>\n'
        if self.language.strip() != "":
            text += '      <language>'+self.language+'</language>\n'
        if self.os.strip() != "":
            text += '      <os>'+self.os+'</os>\n'
        # Verification
        if self.hash_md5.strip() != "" or self.hash_sha1.strip() != "":
            text += '      <verification>\n'
            if self.sig.strip() != "":
                text += '        <signature type="pgp">\n'+self.sig+'        </signature>\n'
            if self.hash_md5.strip() != "":
                text += '        <hash type="md5">'+self.hash_md5.lower()+'</hash>\n'
            if self.hash_sha1.strip() != "":
                text += '        <hash type="sha1">'+self.hash_sha1.lower()+'</hash>\n'
            if self.hash_sha256.strip() != "":
                text += '        <hash type="sha256">'+self.hash_sha256.lower()+'</hash>\n'
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
        return text

    # 3 handler functions
    def start_element(self, name, attrs):
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
        if name == "url" and self.parent[-1].name == "resources":
            fileobj = self.files[-1]
            fileobj.add_url(self.data, attrs=tag.attrs)
        elif name in ("name", "url"):
            setattr(self, self.parent[-1].name + "_" + name, self.data)
        elif name in ("identity", "copyright", "description", "version"):
            setattr(self, name, self.data)
        elif name == "hash" and self.parent[-1].name == "verification":
            hashtype = tag.attrs["type"]
            fileobj = self.files[-1]
            setattr(fileobj, "hash_" + hashtype, self.data)
        elif name == "pieces":
            fileobj = self.files[-1]
            fileobj.piecetype = tag.attrs["type"]
            fileobj.piecelength = tag.attrs["length"]
        elif name == "hash" and self.parent[-1].name == "pieces":
            fileobj = self.files[-1]
            fileobj.pieces.append(self.data)
        elif name in ("os", "size", "language"):
            fileobj = self.files[-1]
            setattr(fileobj, name, self.data)
            
    def char_data(self, data):
        self.data = data.strip()

    def parsefile(self, filename):
        handle = open(filename, "rb")
        self.p.ParseFile(handle)
        handle.close()

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

#### These should eventually be removed ###

    def clear_res(self, *args):
        fileobj = self.files[0]
        return fileobj.clear_res(*args)

    def add_url(self, *args):
        fileobj = self.files[0]
        return fileobj.add_url(*args)

    def scan_file(self, *args):
        try:
            fileobj = self.files[0]
        except IndexError:
            fileobj = MetalinkFile(args[0])
            self.files.append(fileobj)
        
        return fileobj.scan_file(*args)

    def load_file(self, filename):
        return self.parsefile(filename)


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


def compute_ed2k(filename):
    '''
    Generates an ed2k link for a file on the local filesystem.
    '''
    try:
        import hashlib
    except ImportError:
        return ""
    
    blocksize = 9728000
    size = os.path.getsize(filename)

    handle = open(filename, "rb")
    data = handle.read(blocksize)
    hashes = ""
    
    while data:
        md4 = hashlib.new('md4')
        md4.update(data)
        hashes += md4.digest()
        data = handle.read(blocksize)
        
    outputhash = md4.hexdigest()

    if size % blocksize == 0:
        md4 = hashlib.new('md4')
        md4.update("")
        hashes += md4.hexdigest()

    if size >= blocksize:
        md4 = hashlib.new('md4')
        md4.update(hashes)
        outputhash = md4.hexdigest()

    return "ed2k://|file|%s|%s|%s|/" % (os.path.basename(filename), size, outputhash)
