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
# tweaked from upstream because we don't have cElementTree
from xml.etree import ElementTree as ET

import gobject

import config
import utils
from download import Download, DATE_FORMAT_DIGIT, CONNECTING, DOWNLOADING, COMPLETED

XML_HEADER = '<?xml version="1.0" encoding="UTF-8" ?>\n'
DOWNLOADS_FILE = "downloads.xml"

class DownloadList(gobject.GObject):
    """Singleton holding the list of downloads"""

    __gsignals__ = {"download-added": (gobject.SIGNAL_RUN_LAST, None,
                                       (object,)),
                    "download-removed": (gobject.SIGNAL_RUN_LAST, None,
                                         (object,))}

    instance = None

    def __new__(type, *args):
        if DownloadList.instance is None:
            DownloadList.instance = gobject.GObject.__new__(type)
            DownloadList.instance.__init(*args)
        return DownloadList.instance

    def __init(self, *args):
        gobject.GObject.__init__(self)
        self.config = config.Configuration()
        self.downloads = []

    def load_from_xml(self):
        """Loads download objects from the xml file."""
        self.download_file_path = os.path.join(self.config.base_dir,
                DOWNLOADS_FILE)
        if not os.path.exists(self.download_file_path):
            self.__create_xml()
        else:
            self.tree = ET.parse(self.download_file_path)
            downloads_element = self.tree.getroot()
            for download_element in list(downloads_element):
                uri = download_element.findtext("uri")
                path = download_element.findtext("path")
                file_name = download_element.findtext("filename")
                total_size = download_element.findtext("size")
                status = download_element.findtext("status")
                date_started = download_element.findtext("date_started")
                date_completed = download_element.findtext("date_completed")

                download = Download(uri, path, date_started, date_completed)
                download.file_name = file_name
                if total_size:
                    download.total_size = int(total_size)
                if status:
                    download.status = int(status)
                if download.status == COMPLETED:
                    download.percent_complete = 100
                else:
                    if download.total_size != 0:
                        download.percent_complete = 100 * download.current_size / download.total_size
                    else:
                        download.percent_complete = 0
                self.__append_download(download)

    def __create_xml(self):
        file = open(self.download_file_path, "w")
        file.write(XML_HEADER)
        self.tree = ET.ElementTree(ET.fromstring("<downloads>\n</downloads>"))
        self.tree.write(file)
        file.close()

    def add_download(self, uri, path=None, headers={}):
        """Constructs a new download object and adds it to the list and xml
        tree."""
        if path is None:
            path = self.config.default_folder

        download = Download(uri, path, headers)
        self.__append_download(download)
        self.__add_download_to_xml(download)
        return download

    def __append_download(self, download):
        """Connects to the download signals we are interested in before adding
        the download object to the list of downloads."""
        download.connect("update", self.__download_update)
        download.connect("status-changed", self.__download_status_changed)
        self.downloads.append(download)
        utils.debug_print("Appended download %s to list of downloads." %
                download)
        self.emit("download-added", (download))

    def __add_download_to_xml(self, download):
        """Adds the download to the xml tree and saves it to disk."""
        downloads_element = self.tree.getroot()
        download_element = ET.SubElement(downloads_element, "download")
        uri_element = ET.SubElement(download_element, "uri")
        uri_element.text = download.uri
        path_element = ET.SubElement(download_element, "path")
        path_element.text = download.path
        filename_element = ET.SubElement(download_element, "filename")
        filename_element.text = download.file_name
        size_element = ET.SubElement(download_element, "size")
        size_element.text = download.total_size
        status_element = ET.SubElement(download_element, "status")
        status_element.text = str(download.status)
        date_started_element = ET.SubElement(download_element, "date_started")
        date_started_element.text = download.get_date_str("started",
                DATE_FORMAT_DIGIT)
        date_completed_element = ET.SubElement(download_element,
                                               "date_completed")
        date_completed_element.text = download.get_date_str("completed",
                DATE_FORMAT_DIGIT)

        self.__save_xml()

    def __download_update(self, download, block_count, block_size,
            total_size):
        """If the total file size has changed (not likely happen) the download
        element associated is found and the size updated."""
        if download.old_total_size != total_size:
            download_element = self.__get_download_element(download)
            if download_element:
                size_element = download_element.find("size")
                size_element.text = str(total_size)
                self.__save_xml()

    def __download_status_changed(self, download, status):
        """Finds the download element which status was changed and updates the
        xml tree."""
        download_element = self.__get_download_element(download)
        if download_element:
            status_element = download_element.find("status")
            status_element.text = str(status)
            if status == COMPLETED:
                date_completed = download_element.find("date_completed")
                date_completed.text = download.get_date_str("completed",
                            DATE_FORMAT_DIGIT)
            self.__save_xml()

    def __get_download_element(self, download):
        """Returns the download element in the xml tree associated with the
        download object passed. If its not found None is returned."""
        downloads_element = self.tree.getroot()
        for download_element in list(downloads_element):
            uri = download_element.findtext("uri")
            path = download_element.findtext("path")
            if download.uri == uri and download.path == path:
                return download_element
        return None

    def get_download(self, id):
        """Returns the download object in the list with the given id."""
        for download in self.downloads:
            if id == download.id:
                return download
        return None

    def remove_download(self, download):
        """Removes a download object from the list and xml tree."""
        # Make sure the download is stopped before its removed
        if not download.is_canceled():
            download.cancel()
        self.downloads.remove(download)
        download_element = self.__get_download_element(download)
        self.tree.getroot().remove(download_element)
        utils.debug_print("Removed download %s from list of downloads." %
                download)
        self.emit("download-removed", (download))
        self.__save_xml()

    def remove_completed_downloads(self):
        """Removes all completed downloads in the list (and xml tree)."""
        downloads = list(self.downloads)
        for download in downloads:
            if download.status == COMPLETED:
                self.remove_download(download)

    def has_active_downloads(self):
        """Checks if there are any active downloads in progress."""
        downloads = list(self.downloads)
        for download in downloads:
            if download.status in [CONNECTING, DOWNLOADING]:
                return True
        return False

    def __save_xml(self):
        """Adds a header and indents the xml tree before saving it to disk."""
        utils.debug_print("Saved download list to: %s" %
                self.download_file_path)
        file = open(self.download_file_path, "w")
        file.write(XML_HEADER)
        utils.indent(self.tree.getroot())
        self.tree.write(file)
        file.close()

# vim: set sw=4 et sts=4 tw=79 fo+=l:
