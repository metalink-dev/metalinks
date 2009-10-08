#!/usr/bin/env python
########################################################################
#
# Project: Metalink Editor
# URL: http://www.metamirrors.nl/node/59
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2008-2009 Neil McNab
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
# Last Updated: $Date: 2008-06-08 14:16:24 -0700 (Sun, 08 Jun 2008) $
# Author(s): Neil McNab
#
# Description:
#   Core application functions.
#
########################################################################

import metalink
import urllib
import optparse
import os.path
import sys

metalink.GENERATOR = "Metalink Editor version 1.3"

# This value is used by the ProgressBar class. Set it to False if the
# current console doesn't support \b
CONSOLE_SUPPORTS_BACKSPACE = True
if os.name != 'nt':
    CONSOLE_SUPPORTS_BACKSPACE = False

def xml_encode(data):
    tempstr = ""
    for char in data:
        #print char
        if char in ("&"):
            tempstr += "&#%i;" % ord(char.encode('utf8'))
        else:
            tempstr += char
    return tempstr

def build(xml, urls, output=None, localfile=None, download=True, do_ed2k=True, do_magnet=False, v4=False):
    '''
    urls - RFC 2396 encoded urls
    '''

    if len(urls) > 0:
        url = urls[0]

        if localfile == None:
            localfile = os.path.basename(url)

        if download:
            print "Downloading file..."
            # download file here
            progress = ProgressBar(55)
            #print url, localfile
            urllib.urlretrieve(url, localfile, progress.download_update)
            progress.download_end()

    xmlfile = metalink.MetalinkFile(localfile, do_ed2k=do_ed2k, do_magnet=do_magnet)
    xml.files.append(xmlfile)
    xmlfile.scan_file(localfile)
    for item in urls:
        xmlfile.add_url(item)

    if not xml.validate():
        for line in xml.errors:
            print line
        return

    print "Generating XML..."
    if output == None:
        output = localfile + ".metalink"
    
    if output.endswith(".meta4") or v4:
        xml = metalink.convert(xml, 4)
    handle = open(output, "wb")
    handle.write(xml.generate())
    handle.close()
    return xml
    #print xml.generate()

def merge(master, args, v4=False):
    '''
    A master Metalink object with no <files> information and a list of files to merge together.
    '''
    master = metalink.convert(master, 3)
    master.files = []
    for item in args:
        xml = metalink.parsefile(item)
        for fileobj in xml.files:
            master.files.append(fileobj)
    
    if v4:
        master = metalink.convert(master, 4)
        return master.generate()
    return master.generate()

def run():
    # Command line parser options.
    parser = optparse.OptionParser(usage = "usage: %prog [options] urls")
    parser.add_option("--open", dest="open", help="Metalink file to open and modify")
    parser.add_option("-o", dest="output", help="Binary file name")
    parser.add_option("-d", dest="download", action="store_true", help="Don't download the file again")
    parser.add_option("--merge", "-m", dest="merge", action="store_true", help="Use merge mode, urls are .metalink files to merge")
    parser.add_option("--clear_urls", dest="clear_urls", action="store_true", help="Remove any existing urls when opening a file")
    parser.add_option("-4", dest="v4", action="store_true", help="Force output to Metalink v4")    
    parser.add_option("-i", dest="identity", help="Identity")
    parser.add_option("-v", dest="version", help="Version Number")
    #parser.add_option("--os", dest="os", help="Operating System")
    parser.add_option("--publisher-name", dest="publisher_name", help="Publisher Name")
    parser.add_option("--publisher-url", dest="publisher_url", help="Publisher URL")
    parser.add_option("-c", "--copyright", dest="copyright", help="Copyright")
    parser.add_option("--description", dest="description", help="Description")
    parser.add_option("--license-name", dest="license_name", help="License Name")
    parser.add_option("--license-url", dest="license_url", help="License URL")
    parser.add_option("--magnet", dest="magnet", action="store_false", help="Do not add a magnet URL")
    parser.add_option("--ed2k", dest="ed2k", action="store_false", help="Do not add a ed2k URL")
    #parser.add_option("-l", "--language", dest="language", help="The language the file is in, per ISO-639/3166. \"en-US\" for Standard American English")
    #parser.add_option("--maxconn", dest="maxconn_total", help="Maximum number of connections for downloading")    
    parser.add_option("--origin", dest="origin", help="URL for the finished metalink file to check for updates")
    #parser.add_option("--logo", dest="logo", help="URL for a related logo")
    #parser.add_option("-d", dest="pubdate", action="store_true", help="Set publication date to now")
        
    #parser.add_option("-s", "--size", dest="size", help="File size")

    parser.set_defaults(identity=None,version=None,os=None,publisher_name=None,publisher_url=None,copyright=None,description=None,license_name=None,license_url=None,language=None,maxconn_total=None,origin=None,v4=False)
    (options, args) = parser.parse_args()
    if len(args) <= 0:
        print "ERROR: Specify a URL."
        parser.print_help()
        return

    #if options.pubdate:
        # RFC 822 format
    #    options.pubdate = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

    xml = metalink.Metalink()
    #options.ed2k, options.magnet)

    if options.open != None:
        xml = metalink.parsefile(options.open)
        if options.clear_urls:
            xml.clear_res()

    for option in dir(options):
        if not option.startswith("_") and getattr(options, option) != None:
            try:
                getattr(xml, option)
            except AttributeError: continue
            setattr(xml, option, getattr(options, option))

    if options.merge != None:
        if len(args) < 2:
            print "ERROR: You should specify at least two files to merge."
            parser.print_help()
            return

        print merge(xml, args, options.v4)
        return

    download = True
    if options.download:
        download = False
    
    build(xml, args, None, options.output, download, options.v4)

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
        if CONSOLE_SUPPORTS_BACKSPACE:
            sys.stdout.write("\b" * 80)
        else:
            sys.stdout.write(u'\r')
        #if os.name != 'nt':
        #    sys.stdout.write("\n")
        
    def end(self):
        self.update(1, 1)
        print ""

    def download_end(self):
        self.download_update(1, self.total_size, self.total_size)
        print ""


if __name__=="__main__":
    run()
