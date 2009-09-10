#!/usr/bin/env python
########################################################################
#
# Project: Metalink
# URL: http://www.metamirrors.nl/node/59
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2009, Neil McNab
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
#   Converts a .metalink file into Apache directives for mod_headers and mod_setenvif based on RFC draft.
# http://tools.ietf.org/html/draft-bryan-metalinkhttp
#
########################################################################

import optparse
import os
import binascii

import xmlutils

def run():
    # Command line parser options.
    parser = optparse.OptionParser(usage = "usage: %prog [options] directory")
    #parser.add_option("-o", dest="output", metavar="FILE", help=_("Apache style access file to"))

    (options, args) = parser.parse_args()

    if len(args) <= 0:
        print "ERROR: Specify a directory."
        parser.print_help()
        return

    text = ""
    for filename in os.listdir(args[0]):
        if filename.endswith(".metalink"):
            fullname = os.path.join(args[0], filename)
            xml = xmlutils.Metalink()
            xml.parsefile(fullname)
            
            for fileobj in xml.files:
                text += "SetEnvIf Request_URI \"/%s$\" %s\n" % (fileobj.filename.replace(".","\."), fileobj.filename.replace(".", "_"))
                i = 1
                for res in fileobj.resources:
                    text += "SetEnvIf Request_URI \"/%s$\" link%d=%s\n" % (fileobj.filename.replace(".","\."), i, res.url)
                    text += "Header onsuccess add Link \"<%%{link%d}e>; rel=\\\"duplicate\\\";\" env=%s\n" % (i, fileobj.filename.replace(".", "_"))
                    i += 1
                text += "SetEnvIf Request_URI \"/%s$\" md5=%s\n" % (fileobj.filename.replace(".","\."), binascii.b2a_base64(binascii.unhexlify(fileobj.hashlist["md5"])))
                text += "SetEnvIf Request_URI \"/%s$\" sha1=%s\n" % (fileobj.filename.replace(".","\."), binascii.b2a_base64(binascii.unhexlify(fileobj.hashlist["sha1"])))
                text += "Header onsuccess set Content-MD5 %%{md5}e env=%s\n" % fileobj.filename.replace(".", "_")
                text += "Header onsuccess set Digest md5=%%{md5}e,sha=%%{md5}e env=%s\n\n" % fileobj.filename.replace(".", "_")
            
    print text

if __name__=="__main__":
    run()
