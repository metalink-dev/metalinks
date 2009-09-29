#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

# set to "always" or "onsuccess" as described in the apache manual for mod_headers
HTTPSTATUS="always"

HASHMAP = { "sha256": "sha-256", 
            "sha1": "sha",
            "sha-512": "sha-512",
            "sha224": "sha-224",
            "sha384": "sha-384",
            }

def lookup(text):
    try:
        return HASHMAP[text]
    except KeyError:
        return text

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
                    if res.url.split(":")[0] in ("http", "ftp", "https", "ftps", "resync") and res.url.rsplit(".")[-1] != "torrent":
                        pri = ""
                        if res.preference != "":
                            pri = "; pri=%s" % res.preference
                        text += "Header %s add Link \"<%%{link%d}e>; rel=\\\"duplicate\\\"%s\" env=%s\n" % (HTTPSTATUS, i, pri, fileobj.filename.replace(".", "_"))
                    else:
                        text += "Header %s add Link \"<%%{link%d}e>; rel=\\\"describedby\\\"\" env=%s\n" % (HTTPSTATUS, i, fileobj.filename.replace(".", "_"))
                    i += 1
                keys = []
                for key in fileobj.hashlist.keys():
                    keys.append(key)
                    text += "SetEnvIf Request_URI \"/%s$\" %s=%s\n" % (fileobj.filename.replace(".","\."), key.replace("-", ""), binascii.b2a_base64(binascii.unhexlify(fileobj.hashlist[key])))
                    
                #if "md5" in keys:
                #    text += "Header %s set Content-MD5 %%{md5}e env=%s\n" % (HTTPSTATUS, fileobj.filename.replace(".", "_"))
                    
                if len(keys) != 0:
                    hashtext = ""
                    for key in keys:
                        hashtext += "%s=%%{%s}e," % (lookup(key), key.replace("-",""))
                    hashtext = hashtext[:-1]
                    text += "Header %s set Digest %s env=%s\n\n" % (HTTPSTATUS, hashtext, fileobj.filename.replace(".", "_"))
            
    print text
    
if __name__=="__main__":
    run()
