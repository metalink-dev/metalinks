#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (C) 2008 Johan Svedberg <johan@svedberg.com>

# This file is part of GGet.

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
import os.path

PYTHON_DIR = "@PYTHONDIR@"

# Try to determine if we run from source or install and fix path accordingly
# def _check(path):
    # return os.path.exists(path) and os.path.isdir(path) and \
           # os.path.isfile(path + "/AUTHORS")

# name = os.path.join(os.path.dirname(__file__), "..")
# if _check(name):
    # sys.path.insert(0, os.path.abspath(name))
# elif PYTHON_DIR not in sys.path:
    # sys.path.insert(0, os.path.abspath(PYTHON_DIR))

from gget.application import Application

if __name__ == "__main__":
    application = Application()
    application.run()

# vim: set sw=4 et sts=4 tw=79 fo+=l:
