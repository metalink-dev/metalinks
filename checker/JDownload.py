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

import jyinterface.Download

import socket
import thread

import download
import xmlutils

class JDownload(jyinterface.Download):
    #DOWNLOADING = 0
    #PAUSED = 1
    #COMPLETE = 2
    #CANCELLED = 3
    #ERROR = 4
    #STATUSES = ["Downloading", "Paused", "Complete", "Cancelled", "Error"];
    def __init__(self):
        self._status = self.DOWNLOADING
        self._progress = 0
        self._paused = False
        self._cancelled = False
        
    def start(self, filenode, path, segmented):
        self.filenode = filenode
        handlers = {"status": self._set_status, 
                    "pause": self.get_pause, 
                    "cancel": self.get_cancel,
                    }
        # make this a thread            
        thread.start_new_thread(download.download_file_node, (filenode, path, True, handlers, segmented))
        
    def _set_status(self, block_count, block_size, total_size):
        self._progress = (block_count * block_size) / total_size * 100
        
    def getSize(self):
        return self.filenode.get_size()
        
    def getProgress(self):
        return self._progress
    
    def getStatus(self):
        return self._status
    
    def get_pause(self):
        return self._paused

    def get_cancel(self):
        return self._cancelled
        
    def pause(self):
        self._status = self.PAUSED
        self._paused = True
        
    def resume(self):
        self._status = self.DOWNLOADING
        self._paused = False

    def cancel(self):
        self._status = self.CANCELLED
        self._cancelled = True

    def error(self):
        self._status = self.ERROR
        
    def displayFileName(self):
        return self.filenode.get_filename()
        
    def addObserver(self, observer):
        pass
    
    def deleteObserver(self, observer):
        pass
        