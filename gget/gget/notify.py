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
from gettext import gettext as _

import gobject
import gnomevfs

import config
import gui
import dialogs
from status_icon import TrayIcon
from gget import NAME

try:
    import pynotify
except ImportError, ie:
    if str(ie) == "No module named pynotify":
        ed = dialogs.ErrorDialog(_("Error while importing pynotify module"),
                                 _("Could not find python-notify."))
        ed.run()
        sys.exit(1)

TIMEOUT = 60000

class Notification:
    def __init__(self, download):
        self.download = download

        self.config = config.Configuration()
        self.status_icon = TrayIcon()

        pynotify.init(NAME)

        self.notification = pynotify.Notification(_("Download Completed"),
                _("%s has been downloaded successfully.") %
                self.download.file_name)

        if self.download.pixbuf:
            self.notification.set_icon_from_pixbuf(self.download.pixbuf)
        else:
            pixbuf = gui.load_icon(NAME.lower(), 32, 32)
            self.notification.set_icon_from_pixbuf(pixbuf)

        # Position notification at status icon if its shown
        if self.config.show_status_icon:
            # self.notification.attach_to_status_icon(self.status_icon.icon)
            (x, y) = self.__get_position()
            self.notification.set_hint_int32("x", x)
            self.notification.set_hint_int32("y", y)


        self.notification.set_timeout(TIMEOUT) # One minute

        if not download.is_metalink:
            self.notification.add_action("file", _("Open"),
                                         self.__action_invoked)
        self.notification.add_action("folder", _("Open folder"),
                                     self.__action_invoked)
        self.notification.connect("closed", self.__closed)

        if not self.notification.show():
            print "Failed to show notification."

    def __action_invoked(self, notification, action):
        """Called when buttons in the notification is pressed."""
        if action == "file":
            uri = gnomevfs.make_uri_from_input_with_dirs(self.download.file, 2)
            gnomevfs.url_show(uri)
        elif action == "folder":
            uri = gnomevfs.make_uri_from_input(self.download.path)
            gnomevfs.url_show(uri)
        notification.close()

    def __closed(self, notification):
        notification.close()

    def __get_position(self):
        x, y = self.status_icon.image.window.get_position()
        x_, y_, width, height, depth = self.status_icon.image.window.get_geometry()
        x_position = x + (width / 2)
        y_position = y + (height / 2)

        return (x_position, y_position)

# vim: set sw=4 et sts=4 tw=79 fo+=l:
