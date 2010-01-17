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
import sys
import datetime
from gettext import gettext as _

import gtk
import gobject
import gnomevfs

import config
import dbus_service
import gui
import utils
import metalink
from notify import Notification
from gget import NAME

CONNECTING = 0
VERIFYING = 1
DOWNLOADING = 2
CANCELED = 3
PAUSED = 4
COMPLETED = 5
ERROR = 6

# Need this to be able to get an untranslated status message. Would be nice if
# get_status_string could be used, but doesn't seem like gettext can do that.
STATUS_STRINGS = {CONNECTING:  "Connecting",
                  VERIFYING:   "Verifying",
                  DOWNLOADING: "Downloading",
                  CANCELED:    "Canceled",
                  PAUSED:      "Paused",
                  COMPLETED:   "Completed",
                  ERROR:       "Error"}

DATE_FORMAT_HUMAN = "%a, %d %b %Y %H:%M:%S"
DATE_FORMAT_DIGIT = "%Y-%m-%d %H:%M:%S"

class Download(gobject.GObject):
    __gsignals__ = {"update": (gobject.SIGNAL_RUN_LAST, None, (int, int, int)),
                    "bitrate": (gobject.SIGNAL_RUN_LAST, None, (float,)),
                    "status-changed": (gobject.SIGNAL_RUN_LAST, None, (int,))}

    def __init__(self, uri, path, headers={}, date_started="",
            date_completed=""):
        gobject.GObject.__init__(self)
        self.config = config.Configuration()
        self.dbus_service = dbus_service.DBusService()

        self.uri = gnomevfs.make_uri_from_shell_arg(uri)
        self.file_name = os.path.basename(self.uri)

        self.path = path
        self.headers = headers

        if not self.config.ask_for_location:
            folder = utils.get_folder_for_extension(uri)
            if folder:
                self.path = folder

        if uri.endswith(".metalink") or metalink.urlhead(uri,
                metalink=True)["content-type"].startswith(metalink.MIME_TYPE):
            self.is_metalink = True
        else:
            self.is_metalink = False

        self.file = os.path.join(path, self.file_name)

        self.has_started = False

        self.current_size = self.__get_current_size()
        self.total_size = 0
        self.old_total_size = 0
        self.percent_complete = 0

        self.bit_rate = 0.0
        self.last_bitrate = datetime.datetime.now()

        self.old_status = -1
        self.status = -1

        self.mime_type = gnomevfs.get_file_mime_type(self.file_name)
        self.pixbuf = gui.load_icon_from_mime_type(self.mime_type, 32)

        if date_started == "":
            self.date_started = datetime.datetime.now()
        else:
            self.date_started = datetime.datetime.strptime(date_started,
                    DATE_FORMAT_DIGIT)

        if date_completed == "":
            self.date_completed = None
        else:
            self.date_completed = datetime.datetime.strptime(date_completed,
                    DATE_FORMAT_DIGIT)

        self.id = self.date_started.strftime("%Y%m%d%H%M%S")

        self.connect("status-changed", self.__status_changed)

    def __str__(self):
        return self.uri

    def __cmp__(self, other):
        """Compare downloads based on id (start date)."""
        if self.id == other.id:
            return 0
        return -1

    def __get_current_size(self):
        try:
            file_info = gnomevfs.get_file_info(self.file)
            return file_info.size
        except:
            return 0

    def get_date_str(self, date, format=DATE_FORMAT_HUMAN):
        if date == "started":
            return self.date_started.strftime(format)
        else:
            if self.date_completed:
                return self.date_completed.strftime(format)
            else:
                return ""

    def is_canceled(self):
        """Callback which returns True to cancel the download, False
        otherwise."""
        return self.status == CANCELED

    def is_paused(self):
        """Callback which returns True to pause the download and False to
        continue/resume."""
        return self.status == PAUSED

    def update(self, block_count, block_size, total_size):
        """Callback with count of blocks transferred so far, block size in
        bytes and the total size of the file in bytes."""
        utils.debug_print("Download.update called with block_count: %s \
                block_size: %s total_size: %s" % (block_count, block_size,
                    total_size))
        current_size = block_count * block_size
        if current_size > self.current_size:
            self.current_size = current_size

        self.old_total_size = self.total_size
        self.total_size = total_size

        current_bytes = float(block_count * block_size) / 1024 / 1024
        total_bytes = float(total_size) / 1024 / 1024
        try:
            percent_complete = 100 * current_bytes / total_bytes
            if percent_complete > self.percent_complete:
                self.percent_complete = percent_complete
        except ZeroDivisionError:
            self.percent_complete = 0

        if self.percent_complete > 100:
            self.percent_complete = 100

        if not self.has_started:
            self.has_started = True
            self.set_status(DOWNLOADING)

        if self.status != COMPLETED and self.percent_complete == 100:
            self.set_status(COMPLETED)

        utils.debug_print("Percent complete: %s" % self.percent_complete)

        self.emit("update", int(block_count), int(block_size), int(total_size))

    def bitrate(self, bit_rate):
        """Callback with the download bitrate in kilobytes per second."""
        if self.status not in [COMPLETED, PAUSED, CANCELED, ERROR]:
            # Only emit bitrate every second and when it changes
            diff = datetime.datetime.now() - self.last_bitrate
            if diff.seconds > 0 and self.bit_rate != bit_rate:
                self.last_bitrate = datetime.datetime.now()
                self.bit_rate = bit_rate
                self.emit("bitrate", bit_rate)

    def cancel(self):
        """Tries to cancel this download. Returns True if sucessful, else
        False."""
        return self.__set_canceled(True)

    def __set_canceled(self, canceled):
        if canceled:
            if not (self.status != CONNECTING or self.status != DOWNLOADING or \
               self.status != ERROR):
                   return False

        if canceled:
            self.set_status(CANCELED)
        else:
            self.set_status(DOWNLOADING)
        return True

    def pause(self):
        """Tries to pause this download. Returns True if sucessful, else
        False."""
        return self.__set_paused(True)

    def resume(self):
        """Tries to resume this download. Returns True if sucessful, else
        False."""
        if self.status == PAUSED:
            return self.__set_paused(False)
        elif self.status == CANCELED:
            return self.__set_canceled(False)
        return False

    def __set_paused(self, paused):
        if paused:
            if not (self.status != CONNECTING or self.status != DOWNLOADING):
                return False

        if paused:
            self.set_status(PAUSED)
        else:
            self.set_status(DOWNLOADING)
        return True

    def set_status(self, status):
        self.old_status = self.status
        self.status = status
        utils.debug_print("Download status for %s changed to: %s (%s)" % (self,
            self.get_status_string(), status))
        for download_obj in self.dbus_service.download_objects:
            if download_obj.download == self:
                download_obj.StatusChanged(STATUS_STRINGS[status])
        self.emit("status-changed", status)

    def get_status_string(self):
        if self.status == CONNECTING:
            return _("Connecting")
        elif self.status == VERIFYING:
            return _("Verifying")
        elif self.status == DOWNLOADING:
            return _("Downloading")
        elif self.status == CANCELED:
            return _("Canceled")
        elif self.status == PAUSED:
            return _("Paused")
        elif self.status == COMPLETED:
            return _("Completed")
        elif self.status == ERROR:
            return _("Error")
        else:
            return _("N/A")

    def __status_changed(self, download, status):
        if status == COMPLETED:
            self.date_completed = datetime.datetime.now()

            if self.config.show_notifications:
                Notification(download)

        # Set bitrate to 0 if download is completed, paused or canceled
        if status in [COMPLETED, PAUSED, CANCELED, ERROR]:
            if self.bit_rate != 0.0:
                self.bit_rate = 0.0
                self.emit("bitrate", self.bit_rate)

# vim: set sw=4 et sts=4 tw=79 fo+=l:
