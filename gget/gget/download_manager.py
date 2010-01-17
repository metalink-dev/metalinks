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
import thread
import traceback
from gettext import gettext as _

import gtk
import gobject

import metalink

import config
import utils
from download import CONNECTING, DOWNLOADING, CANCELED, COMPLETED, ERROR
from download_list import DownloadList
from gget import NAME, VERSION

class DownloadManager(gobject.GObject):
    """Singleton handling the downloads"""

    __gsignals__ = {"download-started": (gobject.SIGNAL_RUN_LAST, None,
        (object,))}

    instance = None

    def __new__(type, *args):
        if DownloadManager.instance is None:
            DownloadManager.instance = gobject.GObject.__new__(type)
            DownloadManager.instance.__init(*args)
        return DownloadManager.instance

    def __init(self, *args):
        gobject.GObject.__init__(self)
        self.config = config.Configuration()
        self.download_list = DownloadList()
        self.download_list.connect("download-added", self.__download_added)

        metalink.USER_AGENT = "%s %s" % (NAME, VERSION)

        self.__set_proxies()

    def __set_proxies(self):
        if self.config.proxy_mode == "gnome":
            if self.config.use_http_proxy:
                if self.config.use_http_proxy_auth:
                    self.set_proxy("http", "http://%s:%s@%s:%s" % \
                            (self.config.http_proxy_user,
                             self.config.http_proxy_pass,
                             self.config.http_proxy_host,
                             self.config.http_proxy_port))
                    if self.config.use_same_proxy:
                        self.set_proxy("https", "https://%s:%s@%s:%s" % \
                                (self.config.http_proxy_user,
                                 self.config.http_proxy_pass,
                                 self.config.proxy_https_host,
                                 self.config.proxy_https_port))
                        self.set_proxy("ftp", "ftp://%s:%s@%s:%s" % \
                                (self.config.http_proxy_user,
                                 self.config.http_proxy_pass,
                                 self.config.proxy_ftp_host,
                                 self.config.proxy_ftp_port))
                else:
                    self.set_proxy("http", "http://%s:%s" % \
                            (self.config.http_proxy_host,
                             self.config.http_proxy_port))
                    self.set_proxy("https", "https://%s:%s" % \
                            (self.config.proxy_https_host,
                             self.config.proxy_https_port))
                    self.set_proxy("ftp", "ftp://%s:%s" % \
                            (self.config.proxy_ftp_host,
                             self.config.proxy_ftp_port))
        elif self.config.proxy_mode == "manual":
            if self.config.proxy_auth:
                self.set_proxy("http", "http://%s:%s@%s:%s" % \
                               (self.config.proxy_user,
                                self.config.proxy_password,
                                self.config.proxy_host,
                                self.config.proxy_port))
            else:
                self.set_proxy("http", "http://%s:%s" % \
                        (self.config.proxy_host, self.config.proxy_port))

    def __download_added(self, download_list, download):
        """Called when a new download is added to DownloadList. Starts the
        download if its not already completed."""
        download.connect("status-changed", self.__status_changed)

        if not download.status in [COMPLETED, CANCELED]:
            self.start_download(download)

    def __status_changed(self, download, status):
        """Called when the status of a download changes. If a canceled download
        is resumed we need to start the download again."""
        if status == DOWNLOADING and \
           download.old_status == CANCELED:
            self.start_download(download)

    def start_download(self, download):
        """Starts a download in a new thread."""
        utils.debug_print("Starting download %s" % download)
        thread.start_new_thread(self.__start_download, (download,))
        self.emit("download-started", (download))

    def __start_download(self, download):
        # Python 2.5 seems to have a bug: sys.excepthook is not call from code
        # in a thread, see http://spyced.blogspot.com/2007/06/workaround-for-sysexcepthook-bug.html
        # sys.excepthook(*sys.exc_info())

        if download.status in [-1, DOWNLOADING]:
            download.set_status(CONNECTING)
        try:
            result = metalink.get(download.uri, download.path,
                    handlers={"status": download.update,
                              "bitrate": download.bitrate,
                              "cancel": download.is_canceled,
                              "pause": download.is_paused},
                    #headers=download.headers)
                    )

            if not result:
                download.set_status(ERROR)
                print "Failed downloading of file %s" % download.uri

        except Exception, e:
            print "Exception caught in DownloadManager.__start_download: "
            traceback.print_exc()

    def set_proxy(self, protocol, proxy):
        """Sets the proxy to use for the specified protocol."""
        if protocol == "http":
            metalink.HTTP_PROXY = proxy
            utils.debug_print("HTTP proxy: %s" % metalink.HTTP_PROXY)
        elif protocol == "https":
            metalink.HTTPS_PROXY = proxy
            utils.debug_print("HTTPS proxy: %s" % metalink.HTTPS_PROXY)
        elif protocol == "ftp":
            metalink.FTP_PROXY = proxy
            utils.debug_print("FTP proxy: %s" % metalink.FTP_PROXY)

# vim: set sw=4 et sts=4 tw=79 fo+=l:
