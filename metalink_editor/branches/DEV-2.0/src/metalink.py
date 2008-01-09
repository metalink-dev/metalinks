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
'load_string', 'MetalinkException']

__doc__ = """Module for handling metalinks.

This module contains data structures (classes) to represent metalinks
and functions to  load, save and process these in different ways."""

class MetalinkException(Exception):
  """Class used for all exceptions in the metalink module."""
  def __init__(self, message):
    """Initialize exception object and save a message for later.
    @param message: A message describing why the exception was thrown.
    @type message: str"""
    self.message = message
  def __str__(self):
    """Return a string representation of the exception object.
    @returns: The message specified when the object was created.
    @rtype: str"""
    return self.msg

class Metalink:
  """Data structure representing a metalink.
  
  All the variables are initialised to default values. In all cases, except for C{ml_type},
  these values should be interpreted as \"not specified\".  Some variables begin with C{ml_}.
  This means that they describe the metalink file itself instead of the data contained in it."""
  files = []
  """@ivar: This variable contains a list of L{MetalinkFile} objects, representing the
  different files described by the metalink."""
  identity = ''
  version = ''
  description = ''
  releasedate = ''
  tags = ''
  publisher_name = ''
  publisher_url = ''
  license_name = ''
  license_url = ''
  ml_generator = ''
  ml_version = ''
  ml_refreshdate = ''
  ml_pubdate = ''
  ml_origin = ''
  ml_type = 'static'

class MetalinkFile:
  """Data structure representing a file in a metalink.
  
  All the variables are initialised to default values. In all cases, except for
  C{piece_type}, these values should be interpreted as \"not specified\"."""
  name = ''
  identity = ''
  version = ''
  size = -1
  description = ''
  copyright = ''
  changelog = ''
  logo = ''
  tags = ''
  language = ''
  os = ''
  mimetype = ''
  releasedate = ''
  upgrade = ''
  screenshot = ''
  publisher_name = ''
  publisher_url = ''
  license_name = ''
  license_url = ''
  hashes = []
  piece_hashes = []
  piece_length = -1
  piece_type = 'sha1'
  urls = []
  maxconnections = -1

class MetalinkHash:
  type = type
  hash = hash

class MetalinkUrl:
  url = ''
  type = ''
  location = ''
  preference = -1
  maxconnections = -1

# This class handles the parsing of metalinks
class MetalinkHandler(xml.sax.handler.ContentHandler):
  """A content handler that is used to parse metalinks with SAX."""
  def __init__(self, metalink):
    """Initialize the content handler.
    
    @param metalink: Usually an empty Metalink object. All data that is loaded will be added to this object.
    @type metalink: L{Metalink}"""
    self.metalink = metalink
  
  def startDocument(self):
    self.elements = [] # A list of all the elements we are "inside". The root element will be first in the list.
    self.attrs = []    # The attributes for the elements in the list above.
    self.content = ''  # Temporary storage for the content of the current element.
    self.file = None  # The file that is currently being parsing (before it is added to the metalink).
    self.pieces = {}
  
  def endDocument(self):
    pass
  
  def startElement(self, name, attrs):
    # Update the element list and content variable
    self.elements.append(name.lower())
    self.attrs.append(attrs)
    self.content = ''
    # Some elements are processed here (most after the end element, see below)
    if self.elements == ['metalink']:
      if not (attrs.has_key('version') and attrs['version'] == '3.0'):
        raise MetalinkException('The metalink must be of version 3.0.')
      else:
        self.metalink.ml_version = attrs['version']
      if attrs.has_key('generator'):
        self.metalink.ml_generator = attrs['generator']
      if attrs.has_key('refreshdate'):
        self.metalink.ml_refreshdate = attrs['refreshdate']
      if attrs.has_key('pubdate'):
        self.metalink.ml_pubdate = attrs['pubdate']
      if attrs.has_key('origin'):
        self.metalink.ml_origin = attrs['origin']
      if attrs.has_key('type'):
        self.metalink.ml_type = attrs['type']
    elif self.elements == ['metalink', 'files', 'file']:
      self.file = MetalinkFile()
      if attrs.has_key('name'):
        self.file.name = attrs['name']
    elif self.elements == ['metalink', 'files', 'file', 'resources']:
      if attrs.has_key('maxconnections'):
        try:
          self.file.maxconnections = int(attrs['maxconnections'])
        except:
          pass # Ignore this if it can't be parsed
    elif self.elements == ['metalink', 'files', 'file', 'verification', 'pieces']:
      if attrs.has_key('type'):
        self.file.piece_type = attrs['type']
      if attrs.has_key('length'):
        try:
          self.file.piece_length = int(attrs['length'])
        except:
          pass # Ignore this if it isn't a number
      self.pieces = {}
  
  def endElement(self, name):
    # Collect and update data
    attrs = self.attrs.pop()
    content = xml.sax.saxutils.unescape(self.content.strip()) # Get the data, as unescaped text.
    self.content = '' # Next end element shouldn't see this data
    # Process elements. They can only be processed here if they need the element's content.
    if self.elements == ['metalink', 'identity']:
      self.metalink.identity = content
    elif self.elements == ['metalink', 'version']:
      self.metalink.version = content
    elif self.elements == ['metalink', 'description']:
      self.metalink.description = content
    elif self.elements == ['metalink', 'releasedate']:
      self.metalink.releasedate = content
    elif self.elements == ['metalink', 'tags']:
      self.metalink.tags = content
    elif self.elements == ['metalink', 'publisher', 'name']:
      self.metalink.publisher_name = content
    elif self.elements == ['metalink', 'publisher', 'url']:
      self.metalink.publisher_url = content
    elif self.elements == ['metalink', 'license', 'name']:
      self.metalink.license_name = content
    elif self.elements == ['metalink', 'license', 'url']:
      self.metalink.license_url = content
    elif self.elements == ['metalink', 'files', 'file']:
      self.metalink.files.append(self.file)
    elif self.elements == ['metalink', 'files', 'file', 'resources', 'url']:
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
      self.file.urls.append(url)
    elif self.elements == ['metalink', 'files', 'file', 'identity']:
      self.file.identity = content
    elif self.elements == ['metalink', 'files', 'file', 'version']:
      self.file.version = content
    elif self.elements == ['metalink', 'files', 'file', 'size']:
      try:
        self.file.size = int(content)
      except:
        pass # Ignore this if it can't be parsed
    elif self.elements == ['metalink', 'files', 'file', 'description']:
      self.file.description = content
    elif self.elements == ['metalink', 'files', 'file', 'logo']:
      self.file.logo = content
    elif self.elements == ['metalink', 'files', 'file', 'tags']:
      self.file.tags = content
    elif self.elements == ['metalink', 'files', 'file', 'language']:
      self.file.language = content
    elif self.elements == ['metalink', 'files', 'file', 'os']:
      self.file.os = content
    elif self.elements == ['metalink', 'files', 'file', 'mimetype']:
      self.file.mimetype = content
    elif self.elements == ['metalink', 'files', 'file', 'releasedate']:
      self.file.releasedate = content
    elif self.elements == ['metalink', 'files', 'file', 'changelog']:
      self.file.changelog = content
    elif self.elements == ['metalink', 'files', 'file', 'copyright']:
      self.file.copyright = content
    elif self.elements == ['metalink', 'files', 'file', 'upgrade']:
      self.file.upgrade = content
    elif self.elements == ['metalink', 'files', 'file', 'screenshot']:
      self.file.screenshot = content
    elif self.elements == ['metalink', 'files', 'file', 'license', 'name']:
      self.file.license_name = content
    elif self.elements == ['metalink', 'files', 'file', 'license', 'url']:
      self.file.license_url = content
    elif self.elements == ['metalink', 'files', 'file', 'publisher', 'name']:
      self.file.publisher_name = content
    elif self.elements == ['metalink', 'files', 'file', 'publisher', 'url']:
      self.file.publisher_url = content
    elif self.elements == ['metalink', 'files', 'file', 'verification', 'hash']:
      # The hash must have a type, otherwise it will be ignored.
      if attrs.has_key('type'):
        hash = MetalinkHash(attrs['type'], content)
        self.file.hashes.append(hash)
    elif self.elements == ['metalink', 'files', 'file', 'verification', 'pieces', 'hash']:
      if attrs.has_key('piece'):
        self.pieces[attrs['piece']] = content
    elif self.elements == ['metalink', 'files', 'file', 'verification', 'pieces']:
      # Add all the pieces in the right order (starting at index "0")
      for i in range(len(self.pieces)):
        # If this piece is missing, then skip all the pieces
        if not self.pieces.has_key(str(i)):
          self.file.piece_hashes = []
          break
        # If it does exist, then add it
        self.file.piece_hashes.append(self.pieces[str(i)])
      self.pieces = {} # Empty the temporary list
    # Remove this element from the list
    self.elements.pop()
  
  def characters(self, content):
    self.content += content # Save these characters for later

def load_file(filename):
  """Loads a metalink file.
  
  @param filename: the name of the file to be loaded.
  @type filename: str
  @returns: Metalink object, with the data from the file.
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

def load_string(text):
  """Creates a metalink object from a text string.
  
  @param text: a text string containing an xml representation of the metalink.
  @type text: str
  @returns: Metalink object, with the data from the text string.
  @rtype: L{Metalink}
  """
  try:
    metalink = Metalink()
    xml.sax.parseString(text, MetalinkHandler(metalink))
    return metalink
  except xml.sax.SAXParseException:
    raise MetalinkException('Failed to parse xml-data.')
