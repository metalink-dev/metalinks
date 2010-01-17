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

import gtk
import egg.trayicon

import config
import dialogs
import gui

from gget import NAME

class StatusIcon(object):
    """Singleton representing the status icon"""

    instance = None

    def __new__(type, *args):
        if StatusIcon.instance is None:
            StatusIcon.instance = object.__new__(type)
            StatusIcon.instance.__init(*args)
        return StatusIcon.instance

    def __init(self, *args):
        self.main_window = args[0]

        self.icon = gtk.status_icon_new_from_icon_name(NAME.lower())

        self.__build_context_menu()

        self.__connect_widgets()

    def __build_context_menu(self):
        self.context_menu = gtk.Menu()

        self.add_imi = gtk.ImageMenuItem(gtk.STOCK_ADD)
        self.add_imi.show()
        self.context_menu.append(self.add_imi)

        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.context_menu.append(separator)

        self.preferences_imi = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        self.preferences_imi.show()
        self.context_menu.append(self.preferences_imi)

        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.context_menu.append(separator)

        self.quit_imi = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.quit_imi.show()
        self.context_menu.append(self.quit_imi)

    def __connect_widgets(self):
        self.icon.connect("activate", self.__icon_clicked)
        self.icon.connect("popup-menu", self.__icon_popup_menu,
                self.context_menu)

        self.add_imi.connect("activate",
                self.main_window.show_add_download_dialog)
        self.preferences_imi.connect("activate",
                self.main_window.preferences_menu_item_activate)
        self.quit_imi.connect("activate", self.main_window.quit)

    def __icon_clicked(self, icon):
        if self.main_window.window.get_property("visible"):
            self.main_window.window.hide()
        else:
            self.main_window.window.present()

    def __icon_popup_menu(self, icon, button, activate_time, menu):
        menu.popup(None, None, gtk.status_icon_position_menu, button,
                activate_time, icon)

class TrayIcon(object):
    """Singleton representing the tray icon"""

    instance = None

    def __new__(type, *args):
        if TrayIcon.instance is None:
            TrayIcon.instance = object.__new__(type)
            TrayIcon.instance.__init(*args)
        return TrayIcon.instance

    def __init(self, *args):
        self.main_window = args[0]
        self.config = config.Configuration()

        self.icon = egg.trayicon.TrayIcon(NAME)

        self.eb = gtk.EventBox()
        self.eb.set_visible_window(False)
        self.eb.set_events(gtk.gdk.POINTER_MOTION_MASK)

        self.image = gtk.Image()
        self.image.set_from_icon_name(NAME.lower(), gtk.ICON_SIZE_BUTTON)
        self.eb.add(self.image)
        self.icon.add(self.eb)

        self.__build_context_menu()

        self.__connect_widgets()

        self.icon.show_all()

    def __build_context_menu(self):
        self.context_menu = gtk.Menu()

        self.add_imi = gtk.ImageMenuItem(gtk.STOCK_ADD)
        self.add_imi.show()
        self.context_menu.append(self.add_imi)

        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.context_menu.append(separator)

        self.preferences_imi = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        self.preferences_imi.show()
        self.context_menu.append(self.preferences_imi)

        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.context_menu.append(separator)

        self.quit_imi = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        self.quit_imi.show()
        self.context_menu.append(self.quit_imi)

    def __connect_widgets(self):
        self.eb.connect('button-press-event', self.__button_press_event)

        self.add_imi.connect("activate",
                self.main_window.show_add_download_dialog)
        self.preferences_imi.connect("activate",
                self.main_window.preferences_menu_item_activate)
        self.quit_imi.connect("activate", self.main_window.quit)

    def __button_press_event(self, widget, event):
        if event.type != gtk.gdk.BUTTON_PRESS:
            return
        if event.button == 1: # Left click
            self.__left_click()
        elif event.button == 2: # Middle click
            self.__middle_click()
        elif event.button == 3: # Right click
            self.__right_click(event)

    def __left_click(self):
        if self.main_window.window.get_property("visible"):
            self.main_window.window.hide()
        else:
            self.main_window.window.present()

    def __middle_click(self):
        if self.config.ask_for_location:
            add = dialogs.AddDownloadDialog()
            add.dialog.show()
        else:
            uri = gui.get_uri_from_clipboard()
            if uri:
                self.main_window.download_list.add_download(uri,
                        self.config.default_folder)

    def __right_click(self, event):
        self.context_menu.popup(None, None, None, event.button, event.time)

# vim: set sw=4 et sts=4 tw=79 fo+=l:
