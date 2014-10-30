#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Neil McNab <neil@nabber.org>

# This file is part of GGet for Windows.

# GGet is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# GGet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with GGet; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

import sys
import os
import imp

def runned_from_source():
    return True

def main_is_frozen():
    return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
    if main_is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0])

import gget.utils
    
gget.utils.runned_from_source = runned_from_source
gget.utils.__data_dir = os.path.join(get_main_dir(), "data")
gget.utils.__images_dir = os.path.join(gget.utils.__data_dir, "images")

PYTHON_DIR = "@PYTHONDIR@"

from gget.application import Application

if __name__ == "__main__":
    application = Application()
    application.run()

    application.config.client.write_config()
# vim: set sw=4 et sts=4 tw=79 fo+=l:
