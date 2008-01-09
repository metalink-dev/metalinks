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

class MetalinkException(Exception):
  def __init__(self, message):
    self.msg = message
  def __str__(self):
    return self.msg

# This class handles the parsing of metalinks
class MetalinkHandler(xml.sax.handler.ContentHandler):
  
  def __init__(self, metalink):
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
        raise MetalinkException('Wrong version. The metalink must be of version 3.0.')
    elif self.elements == ['metalink', 'files', 'file']:
      if not attrs.has_key('name'):
        raise MetalinkException('Missing attribute: <file> elements must have an attribute called "name".')
      self.file = MetalinkFile()
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
    content = self.content.strip() # Remove unintended white space from the beginning and end.
    self.content = '' # Next end element shouldn't see this data
    # Process elements. They can only be processed here if they need the element's content.
    if self.elements == ['metalink', 'publisher', 'name']:
      self.metalink.publisher_name = content
    elif self.elements == ['metalink', 'publisher', 'url']:
      self.metalink.publisher_url = content
    elif self.elements == ['metalink', 'license', 'name']:
      self.metalink.license_name = content
    elif self.elements == ['metalink', 'license', 'url']:
      self.metalink.license_url = content
    elif self.elements == ['metalink', 'identity']:
      self.metalink.identity = content
    elif self.elements == ['metalink', 'version']:
      self.metalink.version = content
    elif self.elements == ['metalink', 'description']:
      self.metalink.description = content
    elif self.elements == ['metalink', 'logo']:
      self.metalink.logo = content
    elif self.elements == ['metalink', 'tags']:
      self.metalink.tags = content
    elif self.elements == ['metalink', 'relations']:
      self.metalink.relations = content
    elif self.elements == ['metalink', 'releasedate']:
      self.metalink.releasedate = content
    elif self.elements == ['metalink', 'changelog']:
      self.metalink.changelog = content
    elif self.elements == ['metalink', 'copyright']:
      self.metalink.copyright = content
    elif self.elements == ['metalink', 'screenshot']:
      self.metalink.screenshot = content
    elif self.elements == ['metalink', 'files', 'file']:
      self.metalink.files.append(self.file)
    elif self.elements == ['metalink', 'files', 'file', 'resources', 'url']:
      url = MetalinkUrl()
      url.url = content
      if attrs.has_key('type'): url.type = attrs['type']
      if attrs.has_key('preference'): url.preference = attrs['preference']
      if attrs.has_key('location'): url.location = attrs['location']
      if attrs.has_key('maxconnections'): url.maxconnections = attrs['maxconnections']
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
    elif self.elements == ['metalink', 'files', 'file', 'relations']:
      self.file.relations = content
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
  try:
    metalink = Metalink()
    xml.sax.parse(filename, MetalinkHandler(metalink))
    return metalink
  except xml.sax.SAXParseException:
    raise MetalinkException('Failed to parse xml-file.')
  except IOError:
    raise MetalinkException('Failed to read file.')

class Metalink:
  def __init__(self):
    self.files = []
    # Properties for the whole metalink. These will be the default values
    # for the files and will be used if they don't specify their own.
    self.identity = ''
    self.version = ''
    self.description = ''
    self.screenshot = ''
    self.logo = ''
    self.tags = ''
    self.relations = ''
    self.releasedate = ''
    self.changelog = ''
    self.copyright = ''
    self.publisher_name = ''
    self.publisher_url = ''
    self.license_name = ''
    self.license_url = ''

class MetalinkFile:
  def __init__(self):
    self.name = ''
    self.identity = ''
    self.version = ''
    self.size = -1
    self.description = ''
    self.logo = ''
    self.tags = ''
    self.language = ''
    self.os = ''
    self.mimetype = ''
    self.relations = ''
    self.releasedate = ''
    self.changelog = ''
    self.publisher_name = ''
    self.publisher_url = ''
    self.copyright = ''
    self.license_name = ''
    self.license_url = ''
    self.upgrade = ''
    self.screenshot = ''
    self.hashes = []
    self.piece_hashes = []
    self.piece_length = -1
    self.piece_type = 'sha1'
    self.urls = []
    self.maxconnections = -1

class MetalinkHash:
  def __init__(self, type='', hash=''):
    self.type = type
    self.hash = hash
  def __str__(self):
    return self.hash

class MetalinkUrl:
  def __init__(self):
    self.url = ''
    self.type = ''
    self.location = ''
    self.preference = ''
    self.maxconnections = -1
  def __str__(self):
    return self.url
