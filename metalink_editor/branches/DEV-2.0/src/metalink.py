# Copyright (c) 2008 Hampus Wessman, Sweden.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import xml.sax
import xml.sax.handler
import xml.sax.saxutils

__version__ = '2.0'
__author__ = 'Hampus Wessman <hw@vox.nu>'
__copyright__ = 'Copyright (c) 2008 Hampus Wessman, Sweden.'
__license__ = 'MIT license (see license.txt).'
__docformat__ = 'epytext'
__all__ = ['__version__', '__copyright__', '__license__', '__author__', '__url__',
'Metalink', 'MetalinkFile', 'MetalinkHash', 'MetalinkUrl', 'load_file',
'parse_string', 'MetalinkException']

__doc__ = """Module for handling metalinks.

This module contains data structures (classes) to represent metalinks
and functions to  load, save and process these in different ways."""

class MetalinkException(Exception):
  """Class used for all exceptions in the metalink module."""
  def __init__(self, message):
    """Initialize exception object and save a message for later.
    @param message: A text string explaining why the exception was thrown.
    @type message: str"""
    self._message = message
    """A text string explaining why the exception was thrown.
    @type: str"""
  def __str__(self):
    """Returns a string representation of the exception object.
    @return: The message specified when the object was created.
    @rtype: str"""
    return self._message

class Metalink:
  """Data structure representing a metalink.
  
  All the variables are initialised to default values. In all cases, except for C{ml_type},
  these values should be interpreted as "not specified".  Some variables begin with C{ml_}.
  This means that they describe the metalink file itself instead of the data contained in it."""
  files = []
  """@ivar: This variable contains a list of L{MetalinkFile} objects, representing
  all the files described by the metalink.
  @type: list"""
  identity = ''
  """@ivar: This is the basic identity of the metalink. For OpenOffice.org 2.0,
  this would be: C{'OpenOffice.org'}.
  @type: str"""
  version = ''
  """@ivar: This is the version of the files described in the metalink. For OpenOffice.org 2.0, this would be: C{'2.0'}.
  @type: str"""
  description = ''
  """@ivar: This is a text description of the file.
  @type: str"""
  releasedate = ''
  """@ivar: This describes when the files were released (not when the metalink file was created).
  
  All Metalink datetimes conform to the Date and Time Specification of RFC 822, with the exception
  that the year may be expressed with two characters or four characters (four preferred).
  Example: C{'Mon, 15 May 2006 00:00:01 GMT'}
  @type: str"""
  tags = ''
  """@ivar: Tags that describe the file in a few words. Tags are separated by commas.
  @type: str"""
  publisher_name = ''
  """@ivar: The name of the publisher. This should be the publisher of all the files described in the metalink.
  @type: str"""
  publisher_url = ''
  """@ivar: The URL to the publisher's website. This should be the publisher of all the files described in the metalink.
  @type: str"""
  license_name = ''
  """@ivar: The license the files were released under. Such as: Shareware, Commercial, GNU GPL, BSD, Creative Commons, etc.
  @type: str"""
  license_url = ''
  """@ivar: A URL that points to a description of the license. For GNU GPL this would be: C{'http://www.gnu.org/licenses/gpl.html'}.
  @type: str"""
  ml_generator = ''
  """@ivar: The application used to generate the metalink file.
  @type: str"""
  ml_version = ''
  """@ivar: Specifies which version of the Metalink format a file uses. The current version is C{'3.0'}.
  @type: str"""
  ml_refreshdate = ''
  """@ivar: The date and time when a "dynamic" (see L{ml_type}) metalink file has been updated.
  
  All Metalink datetimes conform to the Date and Time Specification of RFC 822, with the exception
  that the year may be expressed with two characters or four characters (four preferred).
  Example: C{'Mon, 15 May 2006 00:00:01 GMT'}
  @type: str"""
  ml_pubdate = ''
  """@ivar: Original date and time of publishing of the metalink file.
  
  All Metalink datetimes conform to the Date and Time Specification of RFC 822, with the exception
  that the year may be expressed with two characters or four characters (four preferred).
  Example: C{'Mon, 15 May 2006 00:00:01 GMT'}
  @type: str"""
  ml_origin = ''
  """@ivar: The original location of this metalink file. If L{ml_type} is "dynamic" then this is the
  location where an updated version of the metalink file will be found.
  @type: str"""
  ml_type = 'static'
  """@ivar: "dynamic" or "static". Static metalink files are not updated. Dynamic metalinks can
  be expected to contain an updated list of mirrors or resources that the file is available from.
  @type: str"""

class MetalinkFile:
  """Data structure representing a file in a metalink.
  
  All the variables are initialised to default values. In all cases, except for
  C{piece_type}, these values should be interpreted as "not specified"."""
  name = ''
  """@ivar: The file name. This will be the file name created locally by the
  download client. This means it will be the output filename, and the names
  of files listed in the URLs do not need to be related to it. Directory
  information can also be contained in the metalink, as in:
  C{'debian-amd64/dists/sarge/Contents-amd64.gz'}. In this example, a
  subdirectory C{debian-amd64/dists/sarge/} will be created and a file named
  C{Contents-amd64.gz} will be created inside it.
  @type: str"""
  identity = ''
  """@ivar: This is the basic identity of the file. For OpenOffice.org 2.0,
  this would be: C{'OpenOffice.org'}.
  @type: str"""
  version = ''
  """@ivar: This is the version of the file. For OpenOffice.org 2.0, this would be: C{'2.0'}.
  @type: str"""
  size = -1
  """@ivar: This is the size of the file in bytes. If a mirror reports a file
  size that is different from the size reported in the metalink, it should not
  be used. If multiple sources are used, all file sizes should match.
  @type: int"""
  description = ''
  """@ivar: This is a text description of the file.
  @type: str"""
  copyright = ''
  """@ivar: A copyright notice for the file.
  @type: str"""
  changelog = ''
  """@ivar: This lists the changes between this version of the file and the last.
  @type: str"""
  logo = ''
  """@ivar: This is a location for a graphic logo for the file or program.
  @type: str"""
  tags = ''
  """@ivar: Tags that describe the file in a few words. Tags are separated by commas.
  @type: str"""
  language = ''
  """@ivar: Tags that describe the file in a few words. Tags are separated by commas.
  @type: str"""
  os = ''
  """@ivar: The language the file is in, per ISO-639/3166. "en-US" for Standard American English,
  "en-GB" for British English, "fr" for French, "de" for German, "zh-Hans" for Chinese
  (Simplified), "zh-Hant" for Chinese (Traditional), etc. By default, a client will get all files
  listed in a metalink. In the future, they should only download files in the user's language
  (set as an option in the client or detected by it). But, there should be options for advanced
  users to download other files.
  @type: str"""
  mimetype = ''
  """@ivar: MIME type of the file.
  @type: str"""
  releasedate = ''
  """@ivar: This describes when the file was released (not when the metalink file was created).
  
  All Metalink datetimes conform to the Date and Time Specification of RFC 822, with the exception
  that the year may be expressed with two characters or four characters (four preferred).
  Example: C{'Mon, 15 May 2006 00:00:01 GMT'}
  @type: str"""
  upgrade = ''
  """@ivar: The action to be performed when a previous version is already installed. Some programs
  need older versions uninstalled before installing new ones, and some do not. Could be
  C{'install'}, C{'uninstall, reboot, install'}, or C{'uninstall, install'}.
  @type: str"""
  screenshot = ''
  """@ivar: URL which points to a screenshot of the application.
  @type: str"""
  publisher_name = ''
  """@ivar: The name of the file's publisher.
  @type: str"""
  publisher_url = ''
  """@ivar: The URL to the publisher's website.
  @type: str"""
  license_name = ''
  """@ivar: The license the file was released under. Such as: Shareware, Commercial, GNU GPL, BSD, Creative Commons, etc.
  @type: str"""
  license_url = ''
  """@ivar: A URL that points to a description of the license. For GNU GPL this would be: C{'http://www.gnu.org/licenses/gpl.html'}.
  @type: str"""
  hashes = []
  """@ivar: A list of L{MetalinkHash} objects. These are used to validate the integrity of the whole file.
  @type: list"""
  piece_hashes = []
  """@ivar: A list of piece hashes, as text strings. These are used to validate parts of the file.
  The first piece hash is used to verify the first L{piece_length} number of bytes in the file, the
  second piece hash is used to verify the next first L{piece_length} number of bytes and so on.
  @type: list"""
  piece_length = -1
  """@ivar: Specifies how large each 'piece' is. Without this piece of informationen we wouldn't
  know what parts of the file to compare against the piece hashes.
  @type: int"""
  piece_type = 'sha1'
  """@ivar: The hash type of the L{piece_hashes}. 'sha1' is the default type. You should seldomly
  need to change this.
  @type: str"""
  urls = []
  """@ivar: A list of URLs (L{MetalinkUrl} from which the file can be retrieved.
  @type: list"""
  maxconnections = -1
  """@ivar: The maximum number of connections that are allowed at once for the
  transfer of this file.
  @type: int"""

class MetalinkHash:
  """Data structure for a hash."""
  type = ''
  """@ivar: The hash type. Valid types are: 'md4', 'md5', 'sha1', 'sha256', 'sha384',
  'sha512', 'rmd160', 'tiger', 'crc32'.
  @type: str"""
  hash = ''
  """@ivar: The actual hash, as a lowercase hexadecimal value.
  @type: str"""

class MetalinkUrl:
  """Data structure describing a URL in a metalink.
  
  It's a good idea, in most circumstances, to specify a L{url} and a L{type}. The rest
  of the variables are completely optional."""
  url = ''
  """@ivar: This is a standard URL. Example: C{'http://example-server.com/file.ext'}.
  @type: str"""
  type = ''
  """@ivar: Describes the type of protocol this URL uses. Possible values are: C{'ftp'},
  C{'ftps'}, C{'http'}, C{'https'}, C{'rsync'}, C{'bittorrent'}, C{'magnet'} and C{'ed2k'}.
  
  If no type is specified the client should try to figure it out, by looking at the URL.
  By scanning the beginning of the URL, it can be determined if it is FTP (ftp://), HTTP
  (http://), rsync (rsync://), magnet (magnet:), ed2k (ed2k://). By examining the end of
  the URL, you can tell if it is for BitTorrent (.torrent).
  @type: str"""
  location = ''
  """@ivar: Two-letter country code for the location of the mirror.
  Example: C{'uk'}.
  @type: str"""
  preference = -1
  """@ivar: Priority from C{1} to C{100}, with C{100} being used first and C{1} last.
  Different URLs can have the same preference, i.e. ten mirrors could have C{100} as
  preference.
  @type: int"""
  maxconnections = -1
  """@ivar: The maximum number of connections to this URL.
  @type: int"""

class MetalinkHandler(xml.sax.handler.ContentHandler):
  """A content handler that is used to parse metalinks with SAX."""
  def __init__(self, metalink):
    """Initialize the content handler.
    
    @param metalink: Usually an empty Metalink object. All data that is loaded will be added to this object.
    @type metalink: L{Metalink}"""
    self._metalink = metalink #: The metalink object where all the loaded data will be saved.
  
  def startDocument(self):
    self._elements = [] #: A list of all the elements we are "inside". The root element will be first in the list and the current element last.
    self._attrs = []    #: The attributes for the elements in the L{elements<self._elements>} list.
    self._content = ''  #: Temporary storage for the content of the current element.
    self._file = None  #: The file that is currently being parsing (before it is added to the metalink).
    self._pieces = {}  #: Temporary storage of piece checksums. When all have been read they are sorted and added to the metalink.
  
  def endDocument(self):
    pass
  
  def startElement(self, name, attrs):
    # Update the element list and content variable
    self._elements.append(name.lower())
    self._attrs.append(attrs)
    self._content = ''
    # Some elements are processed here (most after the end element, see below)
    if self._elements == ['metalink']:
      if not (attrs.has_key('version') and attrs['version'] == '3.0'):
        raise MetalinkException('The metalink must be of version 3.0.')
      else:
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
    elif self._elements == ['metalink', 'files', 'file', 'verification', 'pieces']:
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
    content = xml.sax.saxutils.unescape(self._content.strip()) # Get the data, as unescaped text.
    self._content = '' # Next end element shouldn't see this data
    # Process elements. They can only be processed here if they need the element's content.
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
    elif self._elements == ['metalink', 'files', 'file', 'publisher', 'name']:
      self._file.publisher_name = content
    elif self._elements == ['metalink', 'files', 'file', 'publisher', 'url']:
      self._file.publisher_url = content
    elif self._elements == ['metalink', 'files', 'file', 'verification', 'hash']:
      # The hash must have a type, otherwise it will be ignored.
      if attrs.has_key('type'):
        hash = MetalinkHash()
        hash.type = attrs['type']
        hash.hash = content
        self._file.hashes.append(hash)
    elif self._elements == ['metalink', 'files', 'file', 'verification', 'pieces', 'hash']:
      if attrs.has_key('piece'):
        self._pieces[attrs['piece']] = content
    elif self._elements == ['metalink', 'files', 'file', 'verification', 'pieces']:
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
