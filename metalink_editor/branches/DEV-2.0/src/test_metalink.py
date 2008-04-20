#!/usr/bin/python
# encoding: utf-8
#
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

import unittest
import os
import os.path

__docformat__ = 'epytext'
__all__ = ['run_tests']

__doc__ = """Unit tests for the L{metalink} module.

The tests are run automatically when the script is executed."""

class TestMetalinkClasses(unittest.TestCase):
  """Class used to test that the data structures work as expected. This class
  contains unit tests for the L{metalink} module."""
  def test_metalink(self):
    """Tests L{Metalink <metalink.Metalink>}.
    @return: Nothing"""
    import metalink
    a = metalink.Metalink()
    b = metalink.Metalink()
    self.assertEqual(a == b, True,
      'Compared equal objects. Comparison failed!')
    a.identity = 'Something else'
    self.assertEqual(a == b, False,
      'Compared unequal objects. Comparision failed!')
  def test_metalink_file(self):
    """Tests L{MetalinkFile <metalink.MetalinkFile>}.
    @return: Nothing"""
    import metalink
    a = metalink.Metalink()
    b = metalink.Metalink()
    a.files.append(metalink.MetalinkFile())
    b.files.append(metalink.MetalinkFile())
    self.assertEqual(a == b, True,
      'Compared equal objects. Comparison failed!')
    a.files[0].identity = 'Something else'
    self.assertEqual(a == b, False,
      'Compared unequal objects. Comparision failed!')

class TestMetalinkLoad(unittest.TestCase):
  """Class used to test the loading of metalinks. This class contains unit
  tests for the L{metalink} module."""
  def test_load_file(self):
    """Tries to load the file 'test.metalink'. It then examines the returned
    data to make sure that it was parsed correctly.
    @return: Nothing"""
    import metalink
    ml = metalink.load_file('test.metalink')
    self.assertEqual(ml.identity, u'Test identity')
    self.assertEqual(ml.version, u'1.0.0')
    self.assertEqual(ml.description, u'This is my description, with an & in' +
                    u' it and some Swedish letters: åäö.')
    self.assertEqual(ml.releasedate, u'2008-01-05')
    self.assertEqual(ml.tags, u'example, metalink, unittest')
    self.assertEqual(ml.publisher_name, u'The publisher')
    self.assertEqual(ml.publisher_url, u'http://www.the-publisher.com/')
    self.assertEqual(ml.license_name, u'GNU GPL')
    self.assertEqual(ml.license_url, u'http://www.gnu.org/licenses/gpl.html')
    self.assertEqual(ml.ml_version, u'3.0')
    self.assertEqual(ml.ml_generator, u'example generator')
    self.assertEqual(ml.ml_type, u'dynamic')
    self.assertEqual(ml.ml_origin, u'http://test.com/test.metalink')
    self.assertEqual(ml.ml_pubdate, u'test-date32')
    self.assertEqual(ml.ml_refreshdate, u'refresh48')
    self.assertEqual(len(ml.files), 1)
    file = ml.files[0]
    self.assertEqual(file.identity, u'File identity')
    self.assertEqual(file.version, u'1.1.0')
    self.assertEqual(file.size, 4512266)
    self.assertEqual(file.description, u'File description.')
    self.assertEqual(file.copyright, u'Copyright statement')
    self.assertEqual(file.changelog, u'Changelog text...')
    self.assertEqual(file.logo, u'http://test.com/logo.png')
    self.assertEqual(file.tags, u'file, metalink, unittest')
    self.assertEqual(file.language, u'en-US')
    self.assertEqual(file.os, u'Windows-x86')
    self.assertEqual(file.mimetype, u'text/html')
    self.assertEqual(file.releasedate, u'2007-10-23')
    self.assertEqual(file.upgrade, u'install')
    self.assertEqual(file.screenshot, u'http://test.com/screenshot.php?id=87')
    self.assertEqual(file.publisher_name, u'The file publisher')
    self.assertEqual(file.publisher_url,
                    u'http://www.the-file-publisher.com/')
    self.assertEqual(file.license_name, u'My own license')
    self.assertEqual(file.license_url, u'')
    self.assertEqual(file.maxconnections, 7)
    self.assertEqual(len(file.urls), 2)
    self.assertEqual(file.urls[0].url,
                    u'http://file-server.com/files/test-1.0.0.exe')
    self.assertEqual(file.urls[0].location, u'')
    self.assertEqual(file.urls[0].preference, -1)
    self.assertEqual(file.urls[0].maxconnections, 2)
    self.assertEqual(file.urls[1].url,
                    u'http://file-server.se/pub/test/test-1.0.0.exe')
    self.assertEqual(file.urls[1].location, u'se')
    self.assertEqual(file.urls[1].preference, 97)
    self.assertEqual(file.urls[1].maxconnections, 1)
    self.assertEqual(file.hashes[0].type, u'md5')
    self.assertEqual(file.hashes[0].hash, u'1798e7aa4bf190563c6c680a2bd6599e')
    self.assertEqual(file.hashes[1].type, u'sha1')
    self.assertEqual(file.hashes[1].hash,
                    u'fa721e4157b25de49fca263af7e4b0a866118e51')
    self.assertEqual(file.piece_type, u'sha1')
    self.assertEqual(file.piece_length, 262144)
    self.assertEqual(file.piece_hashes[0],
                    u'c9e34e616c69715020eadd58e58aab14352f2426')
    self.assertEqual(file.piece_hashes[1],
                    u'4444bc23698ec235cbcc1906092793e7c8ef5863')
    self.assertEqual(file.piece_hashes[2],
                    u'90fc9469cff5493bfc421c7bf268ee6fbbed5086')
  
  def test_load_empty(self):
    """Tries to load the file ''. L{metalink.load_file} must raise a
    L{metalink.MetalinkException} to pass the test.
    @return: Nothing"""
    import metalink
    self.assertRaises(metalink.MetalinkException, metalink.load_file, '')
  
  def test_parse_empty(self):
    """Tries to parse an empty string. L{metalink.parse_string} must raise a
    L{metalink.MetalinkException} to pass the test.
    @return: Nothing"""
    import metalink
    self.assertRaises(metalink.MetalinkException, metalink.parse_string, '')

class TestMetalinkSaveLoad(unittest.TestCase):
  """Class used to test the saving and loading of metalinks. This class
  contains unit tests for the L{metalink} module."""
  def tearDown(self):
    """Cleans up after the tests. Deletes 'test.tmp'."""
    #if os.path.exists('test.tmp'): os.remove('test.tmp') # Remove tmp file
  
  def test_generate_xml(self):
    """Constructs a L{Metalink} object and then tries to generate xml based on
    it. Checks that the generated xml is not an empty text string.
    @return: Nothing"""
    import metalink
    ml = metalink.Metalink() # Create empty metalink object
    xml_data = metalink.generate_xml(ml)
    self.failIfEqual(xml_data, '', 'The generated xml equals "".')
  
  def test_save_load(self):
    """Constructs a L{Metalink} object, saves it and then loads it again.
    The loaded metalink and the original metalink are then compared.
    @return: Nothing"""
    import metalink
    # Create metalink
    ml = metalink.Metalink()
    ml.identity = u'Test1'
    ml.version = u'42.2'
    ml.description = u'Test6993 åäö'
    ml.releasedate = u'date'
    ml.tags = u'test, metalink, saving'
    ml.publisher_name = u'publisher342'
    ml.publisher_url = u'http://url3386.com/'
    ml.license_name = u'license8237'
    ml.license_url = u'http://url7394.com/'
    # Add a file
    file = metalink.MetalinkFile()
    file.name = u'test-1.0.tar.gz'
    file.identity = u'Test1632'
    file.version = u'5.2.0'
    file.size = 5683287
    file.description = u'Test description... &åäö'
    file.changelog = u'Changelog45528'
    file.logo = u'http://test332.com/logo.png'
    file.tags = u'tag1, tag2, 345'
    file.language = u'sv-SE'
    file.os = u'Windows-x86'
    file.mimetype = u'text/xml'
    file.releasedate = u'testdate'
    file.upgrade = u'uninstall, install'
    file.screenshot = u'http://test.com/screenshot.php?id=37'
    file.publisher_name = u'publisher32'
    file.publisher_url = u'http://url336.com/'
    file.license_name = u'license827'
    file.license_url = u'http://url794.com/'
    hash = metalink.MetalinkHash('md5', '1798e7aa4bf190563c6c680a2bd6599e')
    file.hashes.append(hash)
    file.piece_length = 124430
    file.piece_type = 'sha1'
    file.piece_hashes.append('c9e34e616c69715020eadd58e58aab14352f2426')
    ml.files.append(file)
    if os.path.exists('test.tmp'): os.remove('test.tmp') # Remove tmp file
    metalink.save_file(ml, 'test.tmp')
    self.failUnless(os.path.exists('test.tmp'),
      '"test.tmp" was not saved. The file does not exist!')
    ml2 = metalink.load_file('test.tmp')
    # Clear some properties, which are modified when the file is saved.
    ml2.ml_version = ''
    ml2.ml_generator = ''
    #print ml.get_dict()
    #print ml2.get_dict()
    self.assertEqual(ml, ml2,
      'The saved and the loaded metalink is not equal!')

def run_tests():
  """Run all unit tests in this module.
  
  This function is automatically called if you run the python file.
  @return: Nothing"""
  unittest.main()

if __name__ == '__main__':
  run_tests()