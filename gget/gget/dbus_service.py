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

import os.path

import gtk.gdk

import config
import dialogs
import download
import utils
from gget import NAME

try:
    import dbus
    import dbus.service
    from dbus.mainloop.glib import DBusGMainLoop
except ImportError, ie:
    if str(ie) == "No module named dbus":
        ed = dialogs.ErrorDialog(_("Error while importing dbus module"),
                             _("Could not find python-dbus."))
        ed.run()
        sys.exit(1)

SERVICE = "org.gnome.GGet"
MAIN_WINDOW_OBJ_PATH = "/org/gnome/GGet/MainWindow"
MAIN_WINDOW_IFACE = "org.gnome.GGet.MainWindow"
DOWNLOAD_MGR_OBJ_PATH = "/org/gnome/GGet/DownloadManager"
DOWNLOAD_MGR_IFACE = "org.gnome.GGet.DownloadManager"
DOWNLOADS_OBJ_PATH = "/org/gnome/GGet/downloads"
DOWNLOAD_IFACE = "org.gnome.GGet.Download"

class DBusService(object):
    """Singleton representing the DBus service"""

    instance = None

    def __new__(type, *args):
        if DBusService.instance is None:
            DBusService.instance = object.__new__(type)
            DBusService.instance.__init(*args)
        return DBusService.instance

    def __init(self, *args):
        self.download_objects = []

    def register(self):
        """Tries to registers the DBus service and its exposed objects. Returns
        True if sucessful (i.e. service not already running) else False."""
        dbus_loop = DBusGMainLoop()
        self.session_bus = dbus.SessionBus(mainloop=dbus_loop)

        try:
            utils.take_dbus_name(SERVICE, bus=self.session_bus)
        except utils.DBusNameExistsException, e:
            self.download_manager = self.get_interface(DOWNLOAD_MGR_OBJ_PATH,
                                                       DOWNLOAD_MGR_IFACE)

            utils.debug_print("The %s DBus service (%s) is already registered on the session bus." % (NAME, SERVICE))
            return False

        utils.debug_print("The %s DBus service (%s) was sucessfully registered on the session bus." % (NAME, SERVICE))

        self.bus_name = dbus.service.BusName(SERVICE, bus=self.session_bus)
        return True

    def get_interface(self, object_path, interface):
        """Returns a DBus interface from an object path."""
        obj = self.session_bus.get_object(SERVICE, object_path)
        return dbus.Interface(obj, interface)

    def register_object(self, path, *args):
        """Register the GGet DBus service object specified by path."""
        if path == MAIN_WINDOW_OBJ_PATH:
            self.main_window = MainWindowObject(self.bus_name, args[0])
        elif path == DOWNLOAD_MGR_OBJ_PATH:
            self.download_manager = DownloadManagerObject(self,
                                                          args[0])
        elif path == DOWNLOADS_OBJ_PATH:
            d = DownloadObject(self.bus_name, args[0])
            self.download_objects.append(d)

class MainWindowObject(dbus.service.Object):
    def __init__(self, bus_name, main_window):
        dbus.service.Object.__init__(self, bus_name, MAIN_WINDOW_OBJ_PATH)
        self.main_window = main_window
        self.config = config.Configuration()

    # Methods

    @dbus.service.method(MAIN_WINDOW_IFACE, in_signature='', out_signature='')
    def Present(self):
        utils.debug_print("Invoked DBus method: %s.%s" % (MAIN_WINDOW_IFACE,
                                                          "Present"))
        self.main_window.window.present()

    @dbus.service.method(MAIN_WINDOW_IFACE, in_signature='', out_signature='')
    def Hide(self):
        utils.debug_print("Invoked DBus method: %s.%s" % (MAIN_WINDOW_IFACE,
                                                          "Hide"))
        self.main_window.window.hide()

class DownloadManagerObject(dbus.service.Object):
    def __init__(self, dbus_service, download_list):
        dbus.service.Object.__init__(self, dbus_service.bus_name,
                                     DOWNLOAD_MGR_OBJ_PATH)
        self.dbus_service = dbus_service
        self.download_list = download_list
        self.config = config.Configuration()

        self.download_list.connect("download-added", self.__download_added)
        self.download_list.connect("download-removed", self.__download_removed)

    def __download_added(self, download_list, download):
        self.dbus_service.register_object(DOWNLOADS_OBJ_PATH, download)
        obj_path = DOWNLOADS_OBJ_PATH + "/" + download.id
        self.DownloadAdded(obj_path)

    def __download_removed(self, download_list, download):
        obj_path = DOWNLOADS_OBJ_PATH + "/" + download.id
        for download_obj in self.dbus_service.download_objects:
            if download_obj.download == download:
                #download_obj.remove_from_connection()
                self.dbus_service.download_objects.remove(download_obj)
        self.DownloadRemoved(obj_path)

    # Signals

    @dbus.service.signal(DOWNLOAD_MGR_IFACE, signature='s')
    def DownloadAdded(self, obj_path):
        utils.debug_print("Emitted DBus signal: %s.%s" % (DOWNLOAD_MGR_IFACE,
                                                          "DownloadAdded"))

    @dbus.service.signal(DOWNLOAD_MGR_IFACE, signature='s')
    def DownloadRemoved(self, obj_path):
        utils.debug_print("Emitted DBus signal: %s.%s" % (DOWNLOAD_MGR_IFACE,
                                                          "DownloadRemoved"))

    # Methods

    @dbus.service.method(DOWNLOAD_MGR_IFACE, in_signature='ssa{ss}',
                         out_signature='s')
    def AddDownload(self, uri, path, headers):
        utils.debug_print("Invoked DBus method: %s.%s" % (DOWNLOAD_MGR_IFACE,
                                                          "AddDownload"))
        r = ""
        if self.config.ask_for_location:
            gtk.gdk.threads_enter()
            add = dialogs.AddDownloadDialog(uri, headers)
            if add.dialog.run() == 1:
                download = add.download
                if download:
                    r = DOWNLOADS_OBJ_PATH + "/" + download.id
            gtk.gdk.threads_leave()
        else:
            download = self.download_list.add_download(uri, path, headers)
            r = DOWNLOADS_OBJ_PATH + "/" + download.id
        return r

    @dbus.service.method(DOWNLOAD_MGR_IFACE, in_signature='s',
                         out_signature='b')
    def RemoveDownload(self, obj_path):
        utils.debug_print("Invoked DBus method: %s.%s" % (DOWNLOAD_MGR_IFACE,
                                                          "RemoveDownload"))
        download = self.download_list.get_download(os.path.basename(obj_path))
        if download:
            self.download_list.remove_download(download)
            return True
        return False

    @dbus.service.method(DOWNLOAD_MGR_IFACE, in_signature='', out_signature='')
    def RemoveCompletedDownloads(self):
        utils.debug_print("Invoked DBus method: %s.%s" % (DOWNLOAD_MGR_IFACE,
                          "RemoveCompletedDownloads"))
        self.download_list.remove_completed_downloads()

    @dbus.service.method(DOWNLOAD_MGR_IFACE, in_signature='',
                         out_signature='as')
    def ListDownloads(self):
        utils.debug_print("Invoked DBus method: %s.%s" % (DOWNLOAD_MGR_IFACE,
                                                          "ListDownloads"))
        r = []
        for download in self.download_list.downloads:
            r.append(DOWNLOADS_OBJ_PATH + "/" + download.id)
        return r

class DownloadObject(dbus.service.Object):
    def __init__(self, bus_name, download):
        path = DOWNLOADS_OBJ_PATH + "/" + download.id
        dbus.service.Object.__init__(self, bus_name, path)
        self.download = download
        self.config = config.Configuration()

    # Signals

    @dbus.service.signal(DOWNLOAD_IFACE, signature='s')
    def StatusChanged(self, status):
        utils.debug_print("Emitted DBus signal: %s.%s" % (DOWNLOAD_IFACE,
                                                          "StatusChanged"))

    # Methods

    @dbus.service.method(DOWNLOAD_IFACE, in_signature='', out_signature='b')
    def Pause(self):
        utils.debug_print("Invoked DBus method: %s.%s" % (DOWNLOAD_IFACE,
                                                          "Pause"))
        return self.download.pause()

    @dbus.service.method(DOWNLOAD_IFACE, in_signature='', out_signature='b')
    def Resume(self):
        utils.debug_print("Invoked DBus method: %s.%s" % (DOWNLOAD_IFACE,
                                                          "Resume"))
        return self.download.resume()

    @dbus.service.method(DOWNLOAD_IFACE, in_signature='', out_signature='b')
    def Cancel(self):
        utils.debug_print("Invoked DBus method: %s.%s" % (DOWNLOAD_IFACE,
                                                          "Cancel"))
        return self.download.cancel()

    @dbus.service.method(DOWNLOAD_IFACE, in_signature='', out_signature='a{ss}')
    def GetProperties(self):
        utils.debug_print("Invoked DBus method: %s.%s" % (DOWNLOAD_IFACE,
                                                          "GetProperties"))
        r = {}
        r["uri"] = self.download.uri
        r["path"] = self.download.path
        r["file"] = self.download.file_name
        r["status"] = download.STATUS_STRINGS[self.download.status]
        r["mime-type"] = self.download.mime_type
        r["total size"] = str(self.download.total_size)
        r["date started"] = self.download.get_date_str("started")
        r["date completed"] = self.download.get_date_str("completed")
        return r

# vim: set sw=4 et sts=4 tw=79 fo+=l:
