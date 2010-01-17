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

import getopt
import gettext
import locale
import os
import sys
from gettext import gettext as _

import pygtk
pygtk.require("2.0")
import gtk
import gnome

import config
import dbus_service
import gui
from dialogs import AddDownloadDialog
from download_list import DownloadList
from download_manager import DownloadManager
from window import MainWindow
from status_icon import TrayIcon
from gget import NAME, VERSION, LOCALE_DIR

class Application:
    def run(self):
        self.__init_i18n()
        [args, headers] = self.__get_options()

        gnome.init(NAME, VERSION)
        gtk.gdk.threads_init()
        gtk.window_set_default_icon_list(*gui.get_icon_list([16, 22, 24, 32]))

        self.download_list = DownloadList()
        self.download_manager = DownloadManager()

        self.dbus_service = dbus_service.DBusService()

        # If the DBus service is already running, add downloads using it
        if not self.dbus_service.register():
            for uri in args:
                self.dbus_service.download_manager.AddDownload(uri,
                        os.getcwd(), headers)
            return 0

        self.dbus_service.register_object(dbus_service.DOWNLOAD_MGR_OBJ_PATH,
                                          self.download_list)

        self.main_window = MainWindow(self.config, self.download_list)
        self.dbus_service.register_object(dbus_service.MAIN_WINDOW_OBJ_PATH,
                                          self.main_window)
        if self.config.show_main_window:
            self.main_window.window.show()

        self.status_icon = TrayIcon(self.main_window)
        if not self.config.show_status_icon:
            self.status_icon.icon.hide_all()

        sys.excepthook = self.main_window.on_unhandled_exception

        self.download_list.load_from_xml()

        for uri in args:
            if self.config.ask_for_location:
                add = AddDownloadDialog(uri, headers)
                add.dialog.run()
            else:
                self.download_list.add_download(uri,
                        self.config.default_folder, headers)

        gtk.main()

    def __init_i18n(self):
        gettext.bindtextdomain(NAME.lower(), LOCALE_DIR)
        gettext.textdomain(NAME.lower())

        #locale.bindtextdomain(NAME.lower(), LOCALE_DIR)
        #locale.textdomain(NAME.lower())

    def __get_options(self):
        """Get command line options."""
        try:
            opts, args = getopt.getopt(sys.argv[1:], "dh", ["debug", "header=",
                "help"])
        except getopt.GetoptError:
            opts = []
            args = sys.argv[1:]

        debug = False
        headers = {}
        for o, a in opts:
            if o in ("-d", "--debug"):
                debug = True
            elif o in ("--header"):
                kv = a.split("=")
                if (len(kv) == 2):
                    headers[kv[0]] = kv[1]
            elif o in ("-h", "--help"):
                self.__print_usage()

        self.config = config.Configuration(debug)
        return [args, headers]

    def __print_usage(self):
        """Output usage information and exit."""
        print _("Usage: %s [OPTION]... [URI]...") % (sys.argv[0])
        print ""
        print _("OPTIONS:")
        print "  -d, --debug		%s" % (_("enable debug messages"))
        print "  -h, --help		%s" % (_("show this help message and exit"))

        sys.exit()

# vim: set sw=4 et sts=4 tw=79 fo+=l:
