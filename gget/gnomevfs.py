#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Neil McNab <neil@nabber.org>

# This file is part of GGet for Windows.  It fakes gnomevfs calls as that is not supported on Windows in Python.

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

import urlparse

def make_uri_from_shell_arg(uri):
    return uri
    
def get_uri_scheme(uri):
    return urlparse.urlparse(uri).scheme
    
def get_file_mime_type(filename):
    return "/"