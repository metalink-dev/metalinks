# Copyright 2008 Hampus Wessman.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#   1. Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import copy
import codecs
import xml.sax
import xml.sax.handler
from xml.sax.saxutils import escape, unescape

class MetalinkException(Exception):
  def __init__(self, message):
    self._message = message
  def __str__(self):
    return self._message

class Metalink:
  """Data structure representing a metalink.
  
  All the variables are initialised to default values. In all cases, except for
  C{ml_type}, these values should be interpreted as "not specified".  Some
  variables begin with C{ml_}. This means that they describe the metalink file
  itself instead of the data contained in it."""
  def __init__(self):
    """Initialize data structure."""
    self.files = []
    """@ivar: This variable contains a list of L{MetalinkFile} objects,
    representing all the files described by the metalink.
    @type: list"""
    self.identity = ''
    """@ivar: This is the basic identity of the metalink. For OpenOffice.org 2.0,
    this would be: C{'OpenOffice.org'}.
    @type: str"""
    self.version = ''
    """@ivar: This is the version of the files described in the metalink. For
    OpenOffice.org 2.0, this would be: C{'2.0'}.
    @type: str"""
    self.description = ''
    """@ivar: This is a text description of the file.
    @type: str"""
    self.releasedate = ''
    """@ivar: This describes when the files were released (not when the metalink
    file was created).
    
    All Metalink datetimes conform to the Date and Time Specification of RFC 822,
    with the exception that the year may be expressed with two characters or four
    characters (four preferred). Example: C{'Mon, 15 May 2006 00:00:01 GMT'}
    @type: str"""
    self.tags = ''
    """@ivar: Tags that describe the file in a few words. Tags are separated by
    commas.
    @type: str"""
    self.publisher_name = ''
    """@ivar: The name of the publisher. This should be the publisher of all the
    files described in the metalink.
    @type: str"""
    self.publisher_url = ''
    """@ivar: The URL to the publisher's website. This should be the publisher of
    all the files described in the metalink.
    @type: str"""
    self.license_name = ''
    """@ivar: The license the files were released under. Such as: Shareware,
    Commercial, GNU GPL, BSD, Creative Commons, etc.
    @type: str"""
    self.license_url = ''
    """@ivar: A URL that points to a description of the license. For GNU GPL this
    would be: C{'http://www.gnu.org/licenses/gpl.html'}.
    @type: str"""
    self.ml_generator = ''
    """@ivar: The application used to generate the metalink file.
    @type: str"""
    self.ml_version = ''
    """@ivar: Specifies which version of the Metalink format a file uses. The
    current version is C{'3.0'}.
    @type: str"""
    self.ml_refreshdate = ''
    """@ivar: The date and time when a "dynamic" (see L{ml_type}) metalink file
    has been updated.
    
    All Metalink datetimes conform to the Date and Time Specification of RFC 822,
    with the exception that the year may be expressed with two characters or four
    characters (four preferred). Example: C{'Mon, 15 May 2006 00:00:01 GMT'}
    @type: str"""
    self.ml_pubdate = ''
    """@ivar: Original date and time of publishing of the metalink file.
    
    All Metalink datetimes conform to the Date and Time Specification of RFC 822,
    with the exception that the year may be expressed with two characters or four
    characters (four preferred). Example: C{'Mon, 15 May 2006 00:00:01 GMT'}
    @type: str"""
    self.ml_origin = ''
    """@ivar: The original location of this metalink file. If L{ml_type} is
    "dynamic" then this is the location where an updated version of the metalink
    file will be found.
    @type: str"""
    self.ml_type = 'static'
    """@ivar: "dynamic" or "static". Static metalink files are not updated.
    Dynamic metalinks can be expected to contain an updated list of mirrors or
    resources that the file is available from.
    @type: str"""
  def get_dict(self):
    """Return all the data as a dictionary. Used by L{__eq__}."""
    dict = copy.copy(self.__dict__)
    files = []
    for f in self.files:
      files.append(f.get_dict())
    dict['files'] = files
    return dict
  def __eq__(self, other):
    """Returns true if this object is equal to L{other}.
    @param other: The object to compare this object with.
    @type other: L{Metalink}
    @return: True if equal, otherwise False.
    @rtype: bool"""
    return self.get_dict() == other.get_dict()

class MetalinkFile:
  """Data structure representing a file in a metalink.
  
  All the variables are initialised to default values. In all cases, except for
  C{piece_type}, these values should be interpreted as "not specified"."""
  def __init__(self):
    self.name = ''
    """@ivar: The file name. This will be the file name created locally by the
    download client. This means it will be the output filename, and the names
    of files listed in the URLs do not need to be related to it. Directory
    information can also be contained in the metalink, as in:
    C{'debian-amd64/dists/sarge/Contents-amd64.gz'}. In this example, a
    subdirectory C{debian-amd64/dists/sarge/} will be created and a file named
    C{Contents-amd64.gz} will be created inside it.
    @type: str"""
    self.identity = ''
    """@ivar: This is the basic identity of the file. For OpenOffice.org 2.0,
    this would be: C{'OpenOffice.org'}.
    @type: str"""
    self.version = ''
    """@ivar: This is the version of the file. For OpenOffice.org 2.0, this
    would be: C{'2.0'}.
    @type: str"""
    self.size = -1
    """@ivar: This is the size of the file in bytes. If a mirror reports a file
    size that is different from the size reported in the metalink, it should
    not be used. If multiple sources are used, all file sizes should match.
    @type: int"""
    self.description = ''
    """@ivar: This is a text description of the file.
    @type: str"""
    self.copyright = ''
    """@ivar: A copyright notice for the file.
    @type: str"""
    self.changelog = ''
    """@ivar: This lists the changes between this version of the file and the
    last.
    @type: str"""
    self.logo = ''
    """@ivar: This is a location for a graphic logo for the file or program.
    @type: str"""
    self.tags = ''
    """@ivar: Tags that describe the file in a few words. Tags are separated by
    commas.
    @type: str"""
    self.language = ''
    """@ivar: The language the file is in, per ISO-639/3166. "en-US" for
    Standard American English, "en-GB" for British English, "fr" for French,
    "de" for German, "zh-Hans" for Chinese (Simplified), "zh-Hant" for Chinese
    (Traditional), etc. By default, a client will get all files listed in a
    metalink. In the future, they should only download files in the user's
    language (set as an option in the client or detected by it). But, there
    should be options for advanced users to download other files.
    @type: str"""
    self.os = ''
    """@ivar: This contains information on the required Operating System and
    architecture, if the file is an application. For example: Source, BSD-x86,
    BSD-x64, Linux-x86, Linux-x64, Linuxia64, Linux-alpha, Linux-arm,
    Linux-hppa, Linux-m68k, Linux-mips, Linux-mipsel, Linux-PPC, Linux-PPC64,
    Linux-s390, Linux-SPARC, MacOSX-PPC, MacOSX-Intel, MacOSX-UB,
    Solaris-SPARC, Solaris-x86, Windows-x86, Windows-x64, Windowsia64. By
    default, a client will download all files listed in a .metalink. In the
    future, they should only download files for the user's Operating System
    (set as an option in the client or detected by it). There should be options
    for advanced users to download other files though.
    @type: str"""
    self.mimetype = ''
    """@ivar: MIME type of the file.
    @type: str"""
    self.releasedate = ''
    """@ivar: This describes when the file was released (not when the metalink
    file was created).
    
    All Metalink datetimes conform to the Date and Time Specification of RFC
    822, with the exception that the year may be expressed with two characters
    or four characters (four preferred). Example: C{'Mon, 15 May 2006 00:00:01
    GMT'}
    @type: str"""
    self.upgrade = ''
    """@ivar: The action to be performed when a previous version is already
    installed. Some programs need older versions uninstalled before installing
    new ones, and some do not. Could be C{'install'}, C{'uninstall, reboot,
    install'}, or C{'uninstall, install'}.
    @type: str"""
    self.screenshot = ''
    """@ivar: URL which points to a screenshot of the application.
    @type: str"""
    self.publisher_name = ''
    """@ivar: The name of the file's publisher.
    @type: str"""
    self.publisher_url = ''
    """@ivar: The URL to the publisher's website.
    @type: str"""
    self.license_name = ''
    """@ivar: The license the file was released under. Such as: Shareware,
    Commercial, GNU GPL, BSD, Creative Commons, etc.
    @type: str"""
    self.license_url = ''
    """@ivar: A URL that points to a description of the license. For GNU GPL
    this would be: C{'http://www.gnu.org/licenses/gpl.html'}.
    @type: str"""
    self.hashes = []
    """@ivar: A list of L{MetalinkHash} objects. These are used to validate the
    integrity of the whole file.
    @type: list"""
    self.piece_hashes = []
    """@ivar: A list of piece hashes, as text strings. These are used to
    validate parts of the file. The first piece hash is used to verify the
    first L{piece_length} number of bytes in the file, the second piece hash is
    used to verify the next first L{piece_length} number of bytes and so on.
    @type: list"""
    self.piece_length = -1
    """@ivar: Specifies how large each 'piece' is. Without this piece of
    informationen we wouldn't know what parts of the file to compare against the
    piece hashes.
    @type: int"""
    self.piece_type = 'sha1'
    """@ivar: The hash type of the L{piece_hashes}. 'sha1' is the default type.
    You should seldomly
    need to change this.
    @type: str"""
    self.urls = []
    """@ivar: A list of URLs (L{MetalinkUrl} from which the file can be
    retrieved.
    @type: list"""
    self.maxconnections = -1
    """@ivar: The maximum number of connections that are allowed at once for the
    transfer of this file.
    @type: int"""
  def get_dict(self):
    """Return all the data as a dictionary. Used by L{__eq__}."""
    dict = copy.copy(self.__dict__)
    hashes = []
    for x in self.hashes:
      hashes.append(x.get_dict())
    dict['hashes'] = hashes
    urls = []
    for x in self.urls:
      urls.append(x.get_dict())
    dict['urls'] = urls
    return dict
  def __eq__(self, other):
    """Returns true if this object is equal to L{other}.
    @param other: The object to compare this object with.
    @type other: L{MetalinkFile}
    @return: True if equal, otherwise False.
    @rtype: bool"""
    return self.get_dict() == other.get_dict()

class MetalinkHash:
  """Data structure for a hash."""
  def __init__(self, type='', hash=''):
    self.type = type
    """@ivar: The hash type. Valid types are: 'md4', 'md5', 'sha1', 'sha256',
    'sha384', 'sha512', 'rmd160', 'tiger', 'crc32'.
    @type: str"""
    self.hash = hash
    """@ivar: The actual hash, as a lowercase hexadecimal value.
    @type: str"""
  def get_dict(self):
    """Return all the data as a dictionary. Used by L{__eq__}."""
    return copy.copy(self.__dict__)
  def __eq__(self, other):
    """Returns true if this object is equal to L{other}.
    @param other: The object to compare this object with.
    @type other: L{MetalinkHash}
    @return: True if equal, otherwise False.
    @rtype: bool"""
    return self.get_dict() == other.get_dict()

class MetalinkUrl:
  """Data structure describing a URL in a metalink.
  
  It's a good idea, in most circumstances, to specify a L{url} and a L{type}.
  The rest of the variables are completely optional."""
  def __init__(self, url='', type=''):
    self.url = url
    """@ivar: This is a standard URL. Example:
    C{'http://example-server.com/file.ext'}.
    @type: str"""
    self.type = type
    """@ivar: Describes the type of protocol this URL uses. Possible values are:
    C{'ftp'}, C{'ftps'}, C{'http'}, C{'https'}, C{'rsync'}, C{'bittorrent'},
    C{'magnet'} and C{'ed2k'}.
    
    If no type is specified the client should try to figure it out, by looking at
    the URL. By scanning the beginning of the URL, it can be determined if it is
    FTP (ftp://), HTTP (http://), rsync (rsync://), magnet (magnet:), ed2k
    (ed2k://). By examining the end of the URL, you can tell if it is for
    BitTorrent (.torrent).
    @type: str"""
    self.location = ''
    """@ivar: Two-letter country code for the location of the mirror.
    Example: C{'uk'}.
    @type: str"""
    self.preference = -1
    """@ivar: Priority from C{1} to C{100}, with C{100} being used first and C{1}
    last. Different URLs can have the same preference, i.e. ten mirrors could
    have C{100} as preference.
    @type: int"""
    self.maxconnections = -1
    """@ivar: The maximum number of connections to this URL.
    @type: int"""
  def get_dict(self):
    """Return all the data as a dictionary. Used by L{__eq__}."""
    return copy.copy(self.__dict__)
  def __eq__(self, other):
    """Returns true if this object is equal to L{other}.
    @param other: The object to compare this object with.
    @type other: L{MetalinkUrl}
    @return: True if equal, otherwise False.
    @rtype: bool"""
    return self.get_dict() == other.get_dict()

class MetalinkHandler(xml.sax.handler.ContentHandler):
  """A content handler that is used to parse metalinks with SAX."""
  def __init__(self, metalink):
    """Initialize the content handler.
    
    @param metalink: Usually an empty Metalink object. All data that is loaded
    will be added to this object.
    @type metalink: L{Metalink}"""
    self._metalink = metalink 
    """The metalink object where all the loaded data will be saved."""

  def startDocument(self):
    self._elements = []
    """A list of all the elements we are "inside". The root element will be
    first in the list and the current element last."""
    self._attrs = []
    """The attributes for the elements in the L{elements<self._elements>}
    list."""
    self._content = ''
    """Temporary storage for the content of the current element."""
    self._file = None
    """The file that is currently being parsing (before it is added to the
    metalink)."""
    self._pieces = {}
    """Temporary storage of piece checksums. When all have been read they are
    sorted and added to the metalink."""
  
  def endDocument(self):
    pass
  
  def startElement(self, name, attrs):
    # Update the element list and content variable
    self._elements.append(name.lower())
    self._attrs.append(attrs)
    self._content = ''
    # Some elements are processed here (most after the end element, see below)
    if self._elements == ['metalink']:
      if attrs.has_key('version'):
        self._metalink.ml_version = attrs['version']
      if attrs.has_key('generator'):
        self._metalink.ml_generator = attrs['generator']
      if attrs.has_key('refreshdate'):
        self._metalink.ml_refreshdate = attrs['refreshdate']
      if attrs.has_key('pubdate'):
        self._metalink.ml_pubdate = attrs['pubdate']
      if attrs.has_key('origin'):
        self._metalink.ml_origin = attrs['origin']
      if attrs.has_key('type'):
        self._metalink.ml_type = attrs['type']
    elif self._elements == ['metalink', 'files', 'file']:
      self._file = MetalinkFile()
      if attrs.has_key('name'):
        self._file.name = attrs['name']
    elif self._elements == ['metalink', 'files', 'file', 'resources']:
      if attrs.has_key('maxconnections'):
        try:
          self._file.maxconnections = int(attrs['maxconnections'])
        except:
          pass # Ignore this if it can't be parsed
    elif self._elements == ['metalink', 'files', 'file',
                            'verification', 'pieces']:
      if attrs.has_key('type'):
        self._file.piece_type = attrs['type']
      if attrs.has_key('length'):
        try:
          self._file.piece_length = int(attrs['length'])
        except:
          pass # Ignore this if it isn't a number
      self._pieces = {}
  
  def endElement(self, name):
    # Collect and update data
    attrs = self._attrs.pop()
    content = unescape(self._content.strip())
    self._content = '' # Next end element shouldn't see this data
    # Process elements. They have to be processed here if they need the
    # element's content.
    if self._elements == ['metalink', 'identity']:
      self._metalink.identity = content
    elif self._elements == ['metalink', 'version']:
      self._metalink.version = content
    elif self._elements == ['metalink', 'description']:
      self._metalink.description = content
    elif self._elements == ['metalink', 'releasedate']:
      self._metalink.releasedate = content
    elif self._elements == ['metalink', 'tags']:
      self._metalink.tags = content
    elif self._elements == ['metalink', 'publisher', 'name']:
      self._metalink.publisher_name = content
    elif self._elements == ['metalink', 'publisher', 'url']:
      self._metalink.publisher_url = content
    elif self._elements == ['metalink', 'license', 'name']:
      self._metalink.license_name = content
    elif self._elements == ['metalink', 'license', 'url']:
      self._metalink.license_url = content
    elif self._elements == ['metalink', 'files', 'file']:
      self._metalink.files.append(self._file)
    elif self._elements == ['metalink', 'files', 'file', 'resources', 'url']:
      url = MetalinkUrl()
      url.url = content
      if attrs.has_key('type'): url.type = attrs['type']
      if attrs.has_key('location'): url.location = attrs['location']
      if attrs.has_key('maxconnections'):
        try:
          url.maxconnections = int(attrs['maxconnections'])
        except:
          pass # Ignore this if it's not a number
      if attrs.has_key('preference'):
        try:
          url.preference = int(attrs['preference'])
        except:
          pass # Ignore this if it's not a number
      self._file.urls.append(url)
    elif self._elements == ['metalink', 'files', 'file', 'identity']:
      self._file.identity = content
    elif self._elements == ['metalink', 'files', 'file', 'version']:
      self._file.version = content
    elif self._elements == ['metalink', 'files', 'file', 'size']:
      try:
        self._file.size = int(content)
      except:
        pass # Ignore this if it can't be parsed
    elif self._elements == ['metalink', 'files', 'file', 'description']:
      self._file.description = content
    elif self._elements == ['metalink', 'files', 'file', 'logo']:
      self._file.logo = content
    elif self._elements == ['metalink', 'files', 'file', 'tags']:
      self._file.tags = content
    elif self._elements == ['metalink', 'files', 'file', 'language']:
      self._file.language = content
    elif self._elements == ['metalink', 'files', 'file', 'os']:
      self._file.os = content
    elif self._elements == ['metalink', 'files', 'file', 'mimetype']:
      self._file.mimetype = content
    elif self._elements == ['metalink', 'files', 'file', 'releasedate']:
      self._file.releasedate = content
    elif self._elements == ['metalink', 'files', 'file', 'changelog']:
      self._file.changelog = content
    elif self._elements == ['metalink', 'files', 'file', 'copyright']:
      self._file.copyright = content
    elif self._elements == ['metalink', 'files', 'file', 'upgrade']:
      self._file.upgrade = content
    elif self._elements == ['metalink', 'files', 'file', 'screenshot']:
      self._file.screenshot = content
    elif self._elements == ['metalink', 'files', 'file', 'license', 'name']:
      self._file.license_name = content
    elif self._elements == ['metalink', 'files', 'file', 'license', 'url']:
      self._file.license_url = content
    elif self._elements == ['metalink', 'files', 'file',
                            'publisher', 'name']:
      self._file.publisher_name = content
    elif self._elements == ['metalink', 'files', 'file', 'publisher', 'url']:
      self._file.publisher_url = content
    elif self._elements == ['metalink', 'files', 'file',
                            'verification', 'hash']:
      # The hash must have a type, otherwise it will be ignored.
      if attrs.has_key('type'):
        hash = MetalinkHash()
        hash.type = attrs['type']
        hash.hash = content
        self._file.hashes.append(hash)
    elif self._elements == ['metalink', 'files', 'file', 'verification',
                            'pieces', 'hash']:
      if attrs.has_key('piece'):
        self._pieces[attrs['piece']] = content
    elif self._elements == ['metalink', 'files', 'file',
                            'verification', 'pieces']:
      # Add all the pieces in the right order (starting at index "0")
      for i in range(len(self._pieces)):
        # If this piece is missing, then skip all the pieces
        if not self._pieces.has_key(str(i)):
          self._file.piece_hashes = []
          break
        # If it does exist, then add it
        self._file.piece_hashes.append(self._pieces[str(i)])
      self._pieces = {} # Empty the temporary list
    # Remove this element from the list
    self._elements.pop()
  
  def characters(self, content):
    self._content += content # Save these characters for later

def load_file(filename):
  """Loads a metalink file.
  
  This function loads and parses the file, specified by L{filename}.
  A new L{Metalink} object is created and then filled with the data
  from the file. The parsing of the file is done by L{MetalinkHandler},
  which is a SAX C{ContentHandler}. The L{MetalinkHandler} object fills
  the L{Metalink} object with the data it receives from the SAX parser.
  The resulting L{Metalink} object is then returned.
  
  @param filename: the name of the file to be loaded.
  @type filename: str
  @return: Metalink object, with the data from the file.
  @rtype: L{Metalink}
  """
  try:
    metalink = Metalink()
    xml.sax.parse(filename, MetalinkHandler(metalink))
    return metalink
  except xml.sax.SAXParseException:
    raise MetalinkException('Failed to parse xml-file.')
  except IOError:
    raise MetalinkException('Failed to read file.')

def parse_string(text):
  """Creates a metalink object from a text string.
  
  This function parses a text string. A new L{Metalink} object is
  created and then filled with the parsed data. The parsing is done
  by L{MetalinkHandler}, which is a SAX C{ContentHandler}. The
  L{MetalinkHandler} object fills the L{Metalink} object with the
  data it receives from the SAX parser. The resulting L{Metalink}
  object is then returned.
  
  @param text: a text string containing an xml representation of the metalink.
  @type text: str
  @return: Metalink object, with the data from the text string.
  @rtype: L{Metalink}
  """
  try:
    metalink = Metalink()
    xml.sax.parseString(text, MetalinkHandler(metalink))
    return metalink
  except xml.sax.SAXParseException:
    raise MetalinkException('Failed to parse xml-data.')

def generate_xml(metalink):
  """Generates an xml document from a L{Metalink} object.
  @param metalink: The Metalink object to be converted into xml.
  @type metalink: L{Metalink}
  @return: A text string with the L{metalink} in xml format.
  @rtype: str"""
  # Begin with the metalink element
  attrs = ' version="3.0"'
  attrs += ' generator="%s"' % ('Metalink Editor version ' + __version__)
  attrs += ' type="%s"' % metalink.ml_type
  if metalink.ml_origin != '':
    attrs += ' origin="%s"' % metalink.ml_origin
  if metalink.ml_pubdate != '':
    attrs += ' pubdate="%s"' % metalink.ml_pubdate
  if metalink.ml_refreshdate != '':
    attrs += ' refreshdate="%s"' % metalink.ml_refreshdate
  attrs += ' xmlns="http://www.metalinker.org/"'
  xml_data = '<?xml version="1.0" encoding="utf-8"?>\n'
  xml_data += '<metalink'+attrs+'>\n'
  # Add some metalink properties
  if metalink.identity != '':
    xml_data += '  <identity>'+escape(metalink.identity)+'</identity>\n'
  if metalink.version != '':
    xml_data += '  <version>'+escape(metalink.version)+'</version>\n'
  if metalink.description != '':
    xml_data += '  <description>'+escape(metalink.description)+ \
                '</description>\n'
  if metalink.releasedate != '':
    xml_data += '  <releasedate>'+escape(metalink.releasedate)+ \
                '</releasedate>\n'
  if metalink.tags != '':
    xml_data += '  <tags>'+escape(metalink.tags)+'</tags>\n'
  # Publisher data
  if metalink.publisher_name != '' or metalink.publisher_url != '':
    xml_data += '  <publisher>\n'
    if metalink.publisher_name:
      xml_data += '    <name>'+escape(metalink.publisher_name)+'</name>\n'
    if metalink.publisher_url:
      xml_data += '    <url>'+escape(metalink.publisher_url)+'</url>\n'
    xml_data += '  </publisher>\n'
  # License data
  if metalink.license_name != '' or metalink.license_url != '':
    xml_data += '  <license>\n'
    if metalink.license_name:
      xml_data += '    <name>'+escape(metalink.license_name)+'</name>\n'
    if metalink.license_url:
      xml_data += '    <url>'+escape(metalink.license_url)+'</url>\n'
    xml_data += '  </license>\n'
  # Generate xml for the files
  xml_data += '  <files>\n'
  for file in metalink.files:
    xml_data += '    <file name="%s">\n' % file.name
    if file.identity != '':
      xml_data += '      <identity>'+escape(file.identity)+'</identity>\n'
    if file.version != '':
      xml_data += '      <version>'+escape(file.version)+'</version>\n'
    if file.size >= 0:
      xml_data += '      <size>'+str(file.size)+'</size>\n'
    if file.description != '':
      xml_data += '      <description>'+escape(file.description)+ \
                  '</description>\n'
    if file.copyright != '':
      xml_data += '      <copyright>'+escape(file.copyright)+'</copyright>\n'
    if file.changelog != '':
      xml_data += '      <changelog>'+escape(file.changelog)+'</changelog>\n'
    if file.logo != '':
      xml_data += '      <logo>'+escape(file.logo)+'</logo>\n'
    if file.tags != '':
      xml_data += '      <tags>'+escape(file.tags)+'</tags>\n'
    if file.language != '':
      xml_data += '      <language>'+escape(file.language)+'</language>\n'
    if file.os != '':
      xml_data += '      <os>'+escape(file.os)+'</os>\n'
    if file.mimetype != '':
      xml_data += '      <mimetype>'+escape(file.mimetype)+'</mimetype>\n'
    if file.releasedate != '':
      xml_data += '      <releasedate>'+escape(file.releasedate)+ \
                  '</releasedate>\n'
    if file.upgrade != '':
      xml_data += '      <upgrade>'+escape(file.upgrade)+'</upgrade>\n'
    if file.screenshot != '':
      xml_data += '      <screenshot>'+escape(file.screenshot)+ \
                  '</screenshot>\n'
    # Publisher data
    if file.publisher_name != '' or file.publisher_url != '':
      xml_data += '      <publisher>\n'
      if file.publisher_name:
        xml_data += '        <name>'+escape(file.publisher_name)+'</name>\n'
      if file.publisher_url:
        xml_data += '        <url>'+escape(file.publisher_url)+'</url>\n'
      xml_data += '      </publisher>\n'
    # License data
    if file.license_name != '' or file.license_url != '':
      xml_data += '      <license>\n'
      if file.license_name:
        xml_data += '        <name>'+escape(file.license_name)+'</name>\n'
      if file.license_url:
        xml_data += '        <url>'+escape(file.license_url)+'</url>\n'
      xml_data += '      </license>\n'
    # Verification
    if len(file.hashes) > 0 or len(file.piece_hashes) > 0:
      xml_data += '      <verification>\n'
      for hash in file.hashes:
        xml_data += '        <hash type="%s">' % hash.type
        xml_data += escape(hash.hash)
        xml_data += '</hash>\n'
      if len(file.piece_hashes) > 0:
        xml_data += '        <pieces type="%s" length="%d">\n' % \
            (file.piece_type, file.piece_length)
        for i in range(len(file.piece_hashes)):
          xml_data += '          <hash piece="%d">' % i
          xml_data += escape(file.piece_hashes[i])
          xml_data += '</hash>\n'
        xml_data += '        </pieces>\n'
      xml_data += '      </verification>\n'
    xml_data += '    </file>\n'
  xml_data += '  </files>\n'
  xml_data += '</metalink>'
  return xml_data

def save_file(metalink, filename):
  """Saves the L{metalink} object as a metalink file called 'L{filename}'.
  
  This function calls L{generate_xml} to generate the xml data to save in the
  file. Then it saves this data in 'L{filename}', overwriting the current file
  if there is one.
  @param metalink: The Metalink object to be saved.
  @type metalink: L{Metalink}
  @param filename: The file name to save the metalink as.
  @type filename: str
  @return: Nothing"""
  xml = generate_xml(metalink)
  fp = codecs.open(filename, 'wb', 'utf-8')
  fp.write(xml)
  fp.close()


