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

import fnmatch
import os
import os.path
import time
from datetime import timedelta
from gettext import gettext as _

import gnomevfs
import dbus
import dbus.glib

import config

def runned_from_source():
    path = os.path.join(os.path.dirname(__file__), "..")
    return os.path.exists(path) and os.path.isdir(path) and \
           os.path.isfile(path + "/AUTHORS")

__data_dir = None
def get_data_dir():
    global __data_dir
    if __data_dir is None:
        if runned_from_source():
            __data_dir = os.sep.join([os.path.dirname(__file__), "..",
                "data"])
        else:
            try:
                import gget
                __data_dir = gget.DATA_DIR
            except:
                __data_dir = "./data"
    return __data_dir

__images_dir = None
def get_images_dir():
    global __images_dir
    if __images_dir is None:
        if runned_from_source():
            __images_dir = os.path.join(get_data_dir(), "images")
        else:
            try:
                import gget
                __images_dir = gget.IMAGES_DIR
            except:
                __images_dir = "./data/images"
    return __images_dir

def get_readable_size(bits):
    if bits is None:
        return ""
    for unit in ['bytes','KB','MB','GB','TB']:
        if float(bits) < 1024.0:
            return "%3.1f %s" % (bits, unit)
        bits = float(bits)
        bits /= 1024.0

def get_readable_speed(bitrate):
    if bitrate > 1000:
        return "%.2f MB/s" % (float(bitrate) / float(1000))
    return "%.0f kB/s" % bitrate

def get_readable_eta(size, bitrate):
    seconds = 0
    try:
        seconds = int(size / bitrate / 1024)
    except ZeroDivisionError:
        seconds = 0

    return secs_to_human(seconds)

def secs_to_human(secs):
    days = secs / 86400
    secs %= 86400
    hours = secs / 3600
    secs %= 3600
    mins = secs / 60
    secs %= 60

    if days:
        return "%dd %dh %dm %ds" % (days, hours, mins, secs)
    elif hours:
        return "%dh %dm %ds" % (hours, mins, secs)
    elif mins:
        return "%dm %ds" % (mins, secs)
    else:
        return "%ds" % secs

def debug_print(message):
    cfg = config.Configuration()
    if cfg.debug:
        print("[%s] %s" % (time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()),
              message))

def get_folder_for_extension(uri):
    cfg = config.Configuration()
    if cfg.check_extensions:
        for extension, folder in zip(cfg.extensions, cfg.extension_folders):
            if fnmatch.fnmatch(os.path.basename(uri), extension):
                return folder
    return None

def indent(element, level=0):
    """Indents a xml.ElementTree starting from element."""
    i = "\n" + level*"  "
    if len(element):
        if not element.text or not element.text.strip():
            element.text = i + "  "
        for element in element:
            indent(element, level+1)
        if not element.tail or not element.tail.strip():
            element.tail = i
    else:
        if level and (not element.tail or not element.tail.strip()):
            element.tail = i

def is_supported_uri(uri):
    if not uri:
        return False
    uri = gnomevfs.make_uri_from_shell_arg(uri)
    scheme = gnomevfs.get_uri_scheme(uri)
    # If the scheme is a file check if the file exists
    if scheme == "file":
        try:
            local_path = gnomevfs.get_local_path_from_uri(uri)
            return os.path.isfile(local_path)
        except Exception, e:
            return False
    return scheme in ["http", "https", "ftp"]

def take_dbus_name(name, replace=False, on_name_lost=None, bus=None):
    target_bus = bus or dbus.Bus()
    proxy = bus_proxy(bus=target_bus)
    flags = 1 | 4 # allow replacement | do not queue
    if replace:
        flags = flags | 2 # replace existing
    if not proxy.RequestName(name, dbus.UInt32(flags)) in (1,4):
        raise DBusNameExistsException("Couldn't get D-BUS name %s: Name exists")
    if on_name_lost:
        proxy.connect_to_signal('NameLost', on_name_lost)

def bus_proxy(bus=None):
    target_bus = bus or dbus.Bus()
    return target_bus.get_object('org.freedesktop.DBus',
            '/org/freedesktop/DBus')

class DBusNameExistsException(Exception):
    pass

# vim: set sw=4 et sts=4 tw=79 fo+=l:
