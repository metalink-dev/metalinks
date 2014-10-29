# -*- coding: utf-8 -*-

# Copyright (C) 2004-2007 Johan Svedberg <johan@svedberg.com>

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

import os.path
from gettext import gettext as _

import gtk
import gtk.gdk
import gtk.glade
import gnomevfs
import gnome.ui

import utils
from gget import NAME, LOCALE_DIR

gtk.glade.bindtextdomain(NAME.lower(), LOCALE_DIR)

glade_file = os.path.join(utils.get_data_dir(), "gget.glade")

icon_theme = gtk.icon_theme_get_default()

def get_icon_list(sizes):
    icon_list = []
    for size in sizes:
        icon_list.append(load_icon(NAME.lower(), size, size))
    return icon_list

def load_icon(icon, width=48, height=48):
    pixbuf = None
    if icon != None and icon != "":
        try:
            icon_file = os.path.join(utils.get_images_dir(), icon)
            if os.path.exists(icon_file):
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icon_file, width,
                                                              height)
            elif icon.startswith("/"):
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icon, width,
                                                              height)
            else:
                pixbuf = icon_theme.load_icon(os.path.splitext(icon)[0], width,
                                              gtk.ICON_LOOKUP_USE_BUILTIN)
        except Exception, msg1:
            try:
                pixbuf = icon_theme.load_icon(icon, width,
                                              gtk.ICON_LOOKUP_USE_BUILTIN)
            except Exception, msg2:
                print 'Error:load_icon:Icon Load Error:%s (or %s)' % (msg1,
                                                                      msg2)

    return pixbuf

# Register our icon with the icon theme if running from source
if utils.runned_from_source():
    for size in [16, 22, 24, 32]:
        icon_dir = "%sx%s" % (size, size)
        icon_file = os.path.join(icon_dir, "gget.png")
        pixbuf = load_icon(icon_file, size, size)
        gtk.icon_theme_add_builtin_icon(NAME.lower(), size, pixbuf)

def load_icon_from_mime_type(mime_type, size=48):
    """Loads an icon from a mime type string. This is ugly and error prone,
    there must be a better way to do this."""
    pixbuf = None
    l = mime_type.split("/")
    mime = "%s-%s" % (l[0], l[1])
    try:
        pixbuf = icon_theme.load_icon(mime, size, gtk.ICON_LOOKUP_USE_BUILTIN)
    except Exception, msg1:
        try:
            mime = "gnome-mime-%s" % mime
            pixbuf = icon_theme.load_icon(mime, size,
                    gtk.ICON_LOOKUP_USE_BUILTIN)
        except Exception, msg2:
            pass
    return pixbuf

def queue_resize(treeview):
    columns = treeview.get_columns()
    for column in columns:
        column.queue_resize()

def get_selected_value(treeview):
    selection = treeview.get_selection()
    (model, iter) = selection.get_selected()
    if iter:
        value = model.get_value(iter, 0)
        return value
    return None

def get_selected_values(treeview):
    values = []
    selection = treeview.get_selection()
    (model, paths) = selection.get_selected_rows()
    for path in paths:
        iter = model.get_iter(path)
        if iter:
            values.append(model.get_value(iter, 0))
    return values

def open_file_on_screen(file, screen):
    uri = gnomevfs.make_uri_from_input_with_dirs(file, 2)
    gnome.ui.url_show_on_screen(uri, screen)

def get_uri_from_clipboard():
    clipboard = gtk.Clipboard(selection="PRIMARY")
    if clipboard.wait_is_text_available():
        uri = clipboard.wait_for_text()
        if uri and utils.is_supported_uri(uri):
            return uri
    return None

# vim: set sw=4 et sts=4 tw=79 fo+=l:
