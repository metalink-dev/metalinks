#!/usr/bin/env python
########################################################################
#
# Project: Metalink Checker
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
# Filename: $URL: https://metalinks.svn.sourceforge.net/svnroot/metalinks/checker/console.py $
# Last Updated: $Date: 2009-06-06 13:06:52 -0700 (Sat, 06 Jun 2009) $
# Version: $Rev: 322 $
# Author(s): Neil McNab
#
# Description:
#   Interface for Java GUI APIs.  Requires Jython 2.5 or newer.
#
########################################################################

import jyinterface.Downloader

import socket

import download
import xmlutils
import JDownload


class JDownloader(jyinterface.Downloader):
    def __init__(self):
        timeout=10
        self.nosegmented = False
        # Command line parser options.
        download.USER_AGENT = "DLApplet/4.3 +http://www.nabber.org/projects/"
        self.filelist = []

        #download.set_proxies()
        
        #    download.OS = os
#            download.LANG = [].extend(language.lower().split(","))
        if timeout != None:
            socket.setdefaulttimeout(int(timeout))
            
    #            download.COUNTRY = country
    
    def start(self, src, path):
        metalink = None
        # assume metalink if ends with .metalink
        if src.endswith(".metalink"):
            metalink = download.parse_metalink(src)
        else:
            # not all servers support HEAD where GET is also supported
            # also a WindowsError is thrown if a local file does not exist
            try:
                # add head check for metalink type, if MIME_TYPE or application/xml? treat as metalink
                if download.urlhead(src, metalink=True)["content-type"].startswith(download.MIME_TYPE):
                    print _("Metalink content-type detected.")
                    metalink = download.parse_metalink(src)
            except:
                pass
                
        if metalink == None:
            # assume normal file download here
            # parse out filename portion here
            metalink = xmlutils.Metalink()
            metalink.add_url(src)
            
        for filenode in metalink.files:
            temp = JDownload.JDownload()
            temp.start(filenode, path, not self.nosegmented)
            self.filelist.append(temp)
            
    def get_managers(self):
        return self.filelist