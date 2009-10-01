#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Project: Metalink
# URL: http://www.nabber.org/projects/
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
# Last Updated: $Date$
# Author(s): Neil McNab
#
# Description:
#   Convert Metalink 3.0 files into Metalink RFC
#
########################################################################

import xmlutils
import optparse
import os

def run():
    # Command line parser options.
    parser = optparse.OptionParser(usage = "usage: %prog [options] file.metalink")
    parser.add_option("-r", dest="rev", action="store_true", help="Reverses conversion to 4 (RFC) to 3")

    (options, args) = parser.parse_args()

    if len(args) <= 0:
        print "ERROR: Specify a file."
        parser.print_help()
        return
        
    convert = 4
    if options.rev != None:
        convert = 3

    #for filename in os.listdir(args[0]):
    filename = args[0]
    if filename.endswith(".metalink") or filename.endswith(".metalink4"):
        fullname = os.path.join(os.path.dirname(__file__), filename)
        xml = xmlutils.metalink_parsefile(fullname, convert)
        print xml.generate()

            
if __name__=="__main__":
    run()