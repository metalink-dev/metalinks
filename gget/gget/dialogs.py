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
import shutil
from gettext import gettext as _

import gtk
import gconf
import gnomevfs
import gnomedesktop
import gnome.ui

import config
import download
import gui
import utils
from download import COMPLETED
from download_list import DownloadList
from download_manager import DownloadManager
from status_icon import TrayIcon
from gget import NAME, VERSION

class AboutDialog(gtk.AboutDialog):
    def __init__(self):
        gtk.AboutDialog.__init__(self)
        gtk.about_dialog_set_email_hook(self.__url_hook, "mailto:")
        gtk.about_dialog_set_url_hook(self.__url_hook, "")

        self.set_logo_icon_name(NAME.lower())
        self.set_name(NAME)
        self.set_version(VERSION)
        self.set_copyright("Copyright (C) 2008 Johan Svedberg")
        self.set_website("http://live.gnome.org/GGet")
        self.set_comments(_("GGet is a Download Manager for the GNOME desktop."))
        self.set_authors(["Johan Svedberg <johan@svedberg.com>"])
        self.set_translator_credits(_("translator-credits"))
        self.set_license("GNU General Public License version 2")
        # self.set_artists([""])

        self.connect("response", lambda self, *args: self.destroy())

    def __url_hook(self, widget, url, scheme):
        gnome.ui.url_show_on_screen(scheme + url, widget.get_screen())

class AddDownloadDialog:
    def __init__(self, uri="", headers={}):
        self.headers = headers
        self.config = config.Configuration()

        self.__get_widgets()
        self.__connect_widgets()

        self.clipboard = gtk.Clipboard(selection="PRIMARY")
        self.owner_change_id = self.clipboard.connect("owner-change",
                self.__clipboard_owner_change)

        if uri:
            self.uri_entry.set_text(uri)
        else:
            self.uri_entry.set_text(gui.get_uri_from_clipboard() or "")
            # self.uri_entry.paste_clipboard()
            # self.uri_entry.select_region(0, -1)

        folder = utils.get_folder_for_extension(uri)
        if not folder:
            folder = self.config.default_folder
        self.download_filechooserbutton.set_current_folder(folder)

        self.download = None

    def __get_widgets(self):
        xml = gtk.glade.XML(gui.glade_file, domain=NAME.lower())

        self.dialog = xml.get_widget("add_dialog")

        self.uri_entry = xml.get_widget("uri_entry")
        self.download_filechooserbutton = xml.get_widget("download_filechooserbutton")

        self.add_button = xml.get_widget("add_add_button")
        self.cancel_button = xml.get_widget("add_cancel_button")

    def __connect_widgets(self):
        self.dialog.connect("delete-event", self.__dialog_delete)

        self.uri_entry.connect("changed", self.__uri_entry_changed)
        self.uri_entry.connect("activate", self.__uri_entry_activate)

        self.add_button.connect("clicked", self.__add_button_clicked)
        self.cancel_button.connect("clicked", self.__cancel_button_clicked)

    def __dialog_delete(self, dialog, event):
        self.dialog.destroy()
        return False

    def __uri_entry_changed(self, entry):
        uri = entry.get_text()
        if len(uri) > 0 and utils.is_supported_uri(uri):
            self.add_button.set_sensitive(True)
        else:
            self.add_button.set_sensitive(False)

    def __clipboard_owner_change(self, clipboard, event):
        uri = gui.get_uri_from_clipboard()
        if uri:
            self.uri_entry.set_text(uri)
            # self.uri_entry.select_region(0, -1)
            # self.uri_entry.grab_focus()

    def __uri_entry_activate(self, entry):
        self.add_button.clicked()

    def __add_button_clicked(self, button):
        download_list = DownloadList()
        self.download = download_list.add_download(self.uri_entry.get_text(),
                self.download_filechooserbutton.get_current_folder(),
                self.headers)

        self.clipboard.disconnect(self.owner_change_id)
        self.dialog.destroy()

    def __cancel_button_clicked(self, button):
        self.clipboard.disconnect(self.owner_change_id)
        self.dialog.destroy()

class DetailsDialog:
    def __init__(self, download):
        self.download = download

        self.__get_widgets()
        self.__connect_widgets()

        if download.pixbuf:
            pixbuf = gui.load_icon_from_mime_type(download.mime_type, 48)
            self.image.set_from_pixbuf(pixbuf)
        else:
            self.image.set_from_icon_name(NAME.lower(), gtk.ICON_SIZE_DIALOG)

        self.uri_label.set_text(download.uri)
        self.name_label.set_text(download.file_name)
        self.folder_label.set_text(download.path)
        self.current_size_label.set_text("%s (%s bytes)" % \
                (utils.get_readable_size(download.current_size),
                    download.current_size))
        self.total_size_label.set_text("%s (%s bytes)" % \
            (utils.get_readable_size(download.total_size),
                download.total_size))
        self.mime_type_label.set_text(download.mime_type)
        self.date_started_label.set_text(download.get_date_str("started"))
        self.date_completed_label.set_text(download.get_date_str("completed"))

        download.connect("update", self.__download_update)
        download.connect("status-changed", self.__download_status_changed)

        self.dialog.show()

    def __get_widgets(self):
        xml = gtk.glade.XML(gui.glade_file, domain=NAME.lower())

        self.dialog = xml.get_widget("details_dialog")

        self.image = xml.get_widget("details_image")

        self.uri_label = xml.get_widget("uri_label")
        self.name_label = xml.get_widget("name_label")
        self.folder_label = xml.get_widget("folder_label")
        self.current_size_label = xml.get_widget("current_size_label")
        self.total_size_label = xml.get_widget("total_size_label")
        self.mime_type_label = xml.get_widget("mime_type_label")
        self.date_started_label = xml.get_widget("date_started_label")
        self.date_completed_label = xml.get_widget("date_completed_label")

        self.close_button = xml.get_widget("details_close_button")

    def __connect_widgets(self):
        self.dialog.connect("delete-event", self.__dialog_delete)
        self.dialog.connect("response", self.__dialog_response)

        self.close_button.connect("clicked", self.__close_button_clicked)

    def __dialog_response(self, dialog, response):
        self.dialog.destroy()

    def __dialog_delete(self, dialog, event):
        return True

    def __download_update(self, download, block_count, block_size, total_size):
        self.current_size_label.set_text("%s (%s bytes)" %
                (utils.get_readable_size(download.current_size),
                    download.current_size))

    def __download_status_changed(self, download, status):
        if status == COMPLETED:
            self.date_completed_label.set_text(download.get_date_str("completed"))

    def __close_button_clicked(self, button):
        self.dialog.destroy()

class ErrorDialog(gtk.MessageDialog):
    def __init__(self, primary_msg, secondary_msg):
        gtk.MessageDialog.__init__(self, parent=None,
                flags=gtk.DIALOG_MODAL|gtk . DIALOG_DESTROY_WITH_PARENT,
                type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK,
                message_format=primary_msg)
        self.format_secondary_text(secondary_msg)
        self.set_title(_("Error"))

AUTOSTART_DIR = "~/.config/autostart"
DESKTOP_FILE = "gget.desktop"

class PreferencesDialog:
    def __init__(self, config):
        self.config = config
        self.download_manager = DownloadManager()

        self.__get_widgets()
        self.__make_extensions_treeview()
        self.__connect_widgets()
        self.__add_config_notifications()

        # Set widget states from configuration
        self.status_icon_checkbutton.set_active(self.config.show_status_icon)
        self.main_window_checkbutton.set_active(self.config.show_main_window)
        self.notifications_checkbutton.set_active(self.config.show_notifications)
        self.quit_dialog_checkbutton.set_active(self.config.show_quit_dialog)
        self.autostart_checkbutton.set_active(self.config.autostart)

        self.main_window_checkbutton.set_sensitive(self.config.show_status_icon)

        if self.config.ask_for_location:
            self.ask_folder_radiobutton.set_active(True)
        else:
            self.specify_folder_radiobutton.set_active(True)
        self.default_folder_filechooserbutton.set_current_folder(self.config.default_folder)
        self.extensions_checkbutton.set_active(self.config.check_extensions)
        if not self.config.check_extensions:
            self.extensions_alignment.set_sensitive(False)

        for extension, folder in zip(self.config.extensions,
                self.config.extension_folders):
            self.extensions_model.append((extension, folder))

        self.manual_proxy_vbox.set_sensitive(False)
        if self.config.proxy_mode == "gnome":
            self.gnome_radiobutton.set_active(True)
        elif self.config.proxy_mode == "manual":
            self.manual_radiobutton.set_active(True)
        else:
            self.direct_radiobutton.set_active(True)

        self.proxy_entry.set_text(self.config.proxy_host)
        self.proxy_port_spinbutton.set_value(self.config.proxy_port)
        self.proxy_auth_checkbutton.set_active(self.config.proxy_auth)
        self.proxy_auth_hbox.set_sensitive(self.config.proxy_auth)
        self.proxy_user_entry.set_text(self.config.proxy_user)
        self.proxy_password_entry.set_text(self.config.proxy_password)

    def __get_widgets(self):
        """Get widgets from the glade file."""
        xml = gtk.glade.XML(gui.glade_file, domain=NAME.lower())

        self.dialog = xml.get_widget("preferences_dialog")

        # General tab
        self.status_icon_checkbutton = xml.get_widget("status_icon_checkbutton")
        self.main_window_checkbutton = xml.get_widget("main_window_checkbutton")
        self.notifications_checkbutton = xml.get_widget("notifications_checkbutton")
        self.quit_dialog_checkbutton = xml.get_widget("quit_dialog_checkbutton")

        self.autostart_checkbutton = xml.get_widget("autostart_checkbutton")

        # Folders tab
        self.ask_folder_radiobutton = xml.get_widget("ask_folder_radiobutton")
        self.specify_folder_radiobutton = xml.get_widget("specify_folder_radiobutton")
        self.default_folder_filechooserbutton = xml.get_widget("default_folder_filechooserbutton")
        self.extensions_checkbutton = xml.get_widget("extensions_checkbutton")
        self.extensions_alignment = xml.get_widget("extensions_alignment")
        self.extensions_treeview = xml.get_widget("extensions_treeview")
        self.add_extension_button = xml.get_widget("add_extension_button")
        self.remove_extension_button = xml.get_widget("remove_extension_button")

        # Network tab
        self.direct_radiobutton = xml.get_widget("direct_radiobutton")
        self.gnome_radiobutton = xml.get_widget("gnome_radiobutton")
        self.manual_radiobutton = xml.get_widget("manual_radiobutton")
        self.manual_proxy_vbox = xml.get_widget("manual_proxy_vbox")
        self.proxy_entry = xml.get_widget("proxy_entry")
        self.proxy_port_spinbutton = xml.get_widget("proxy_port_spinbutton")
        self.proxy_auth_checkbutton = xml.get_widget("proxy_auth_checkbutton")
        self.proxy_auth_hbox = xml.get_widget("proxy_auth_hbox")
        self.proxy_user_entry = xml.get_widget("proxy_user_entry")
        self.proxy_password_entry = xml.get_widget("proxy_password_entry")

        # Buttons
        self.close_button = xml.get_widget("close_button")

    def __make_extensions_treeview(self):
        self.extensions_model = gtk.ListStore(str, str)
        self.extensions_treeview.set_model(self.extensions_model)

        # Extension
        self.extension_cell_renderer = gtk.CellRendererText()
        self.extension_cell_renderer.props.xpad = 3
        self.extension_cell_renderer.props.ypad = 3
        self.extension_cell_renderer.props.editable = True
        self.extension_cell_renderer.connect("edited",
                self.__extension_cell_renderer_edited)
        self.extension_treeview_column = gtk.TreeViewColumn(_("Extension"),
                self.extension_cell_renderer)
        self.extension_treeview_column.set_cell_data_func(
                self.extension_cell_renderer, self.__extension_cell_data_func)
        self.extensions_treeview.append_column(self.extension_treeview_column)

        # Folder
        folder_cell_renderer = gtk.CellRendererText()
        folder_cell_renderer.props.xpad = 3
        folder_cell_renderer.props.ypad = 3
        folder_cell_renderer.props.editable = True
        folder_cell_renderer.connect("edited",
                self.__folder_cell_renderer_edited)
        folder_treeview_column = gtk.TreeViewColumn(_("Folder"),
                folder_cell_renderer)
        folder_treeview_column.set_cell_data_func(folder_cell_renderer,
                self.__folder_cell_data_func)
        self.extensions_treeview.append_column(folder_treeview_column)

    def __extension_cell_data_func(self, column, cell, model, iter):
        cell.props.text = model.get_value(iter, 0)

    def __folder_cell_data_func(self, column, cell, model, iter):
        cell.props.text = model.get_value(iter, 1)

    def __extension_cell_renderer_edited(self, cell, path, new_text):
        extensions = self.config.extensions
        if self.extensions_model[path][0] in extensions:
            extensions[extensions.index(self.extensions_model[path][0])] = new_text
            self.config.extensions = extensions
        self.extensions_model[path][0] = new_text

    def __folder_cell_renderer_edited(self, cell, path, new_text):
        extension_folders = self.config.extension_folders
        if self.extensions_model[path][1] in extension_folders:
            extension_folders[extension_folders.index(self.extensions_model[path][1])] = new_text
            self.config.extension_folders = extension_folders
        self.extensions_model[path][1] = new_text

    def __connect_widgets(self):
        """Connect to the widget signals we are interested in."""
        # General tab
        self.status_icon_checkbutton.connect("toggled",
                self.__status_icon_checkbutton_toggled)
        self.main_window_checkbutton.connect("toggled",
                self.__main_window_checkbutton_toggled)
        self.notifications_checkbutton.connect("toggled",
                self.__notifications_checkbutton_toggled)
        self.quit_dialog_checkbutton.connect("toggled",
                self.__quit_dialog_checkbutton_toggled)

        self.autostart_checkbutton.connect("toggled",
                self.__autostart_checkbutton_toggled)

        # Folders tab
        self.ask_folder_radiobutton.connect("toggled",
                self.__ask_folder_radiobutton_toggled)
        self.default_folder_filechooserbutton.connect("current-folder-changed",
                self.__default_folder_filechooserbutton_current_folder_changed)
        self.extensions_checkbutton.connect("toggled",
                self.__extensions_checkbutton_toggled)
        self.add_extension_button.connect("clicked",
                self.__add_extension_button_clicked)
        self.remove_extension_button.connect("clicked",
                self.__remove_extension_button_clicked)

        selection = self.extensions_treeview.get_selection()
        selection.connect("changed",
                self.__extensions_treeview_selection_changed)

        # Network tab
        self.direct_radiobutton.connect("toggled",
                self.__direct_radiobutton_toggled)
        self.gnome_radiobutton.connect("toggled",
                self.__gnome_radiobutton_toggled)
        self.manual_radiobutton.connect("toggled",
                self.__manual_radiobutton_toggled)
        self.proxy_entry.connect("changed",
                self.__proxy_entry_changed)
        self.proxy_port_spinbutton.connect("value-changed",
                self.__proxy_port_spinbutton_value_changed)
        self.proxy_auth_checkbutton.connect("toggled",
                self.__proxy_auth_checkbutton_toggled)
        self.proxy_user_entry.connect("changed",
                self.__proxy_user_entry_changed)
        self.proxy_password_entry.connect("changed",
                self.__proxy_password_entry_changed)

        # Buttons
        self.close_button.connect("clicked", self.__close_button_clicked)

    def __add_config_notifications(self):
        """Adds callbacks which gets called when configuration keys changes
        in gconf."""
        self.config.add_notify(config.KEY_SHOW_STATUS_ICON,
                self.__show_status_icon_key_changed)
        self.config.add_notify(config.KEY_SHOW_MAIN_WINDOW,
                self.__show_main_window_key_changed)
        self.config.add_notify(config.KEY_SHOW_NOTIFICATIONS,
                self.__show_notifications_key_changed)
        self.config.add_notify(config.KEY_SHOW_QUIT_DIALOG,
                self.__show_quit_dialog_key_changed)
        self.config.add_notify(config.KEY_AUTOSTART,
                self.__autostart_key_changed)
        self.config.add_notify(config.KEY_ASK_FOR_LOCATION,
                self.__ask_for_location_key_changed)
        self.config.add_notify(config.KEY_DEFAULT_FOLDER,
                self.__default_folder_key_changed)
        self.config.add_notify(config.KEY_CHECK_EXTENSIONS,
                self.__check_extensions_key_changed)
        self.config.add_notify(config.KEY_PROXY_MODE,
                self.__proxy_mode_key_changed)
        self.config.add_notify(config.KEY_PROXY_HOST,
                self.__proxy_host_key_changed)
        self.config.add_notify(config.KEY_PROXY_PORT,
                self.__proxy_port_key_changed)
        self.config.add_notify(config.KEY_PROXY_AUTH,
                self.__proxy_auth_key_changed)
        self.config.add_notify(config.KEY_PROXY_USER,
                self.__proxy_user_key_changed)
        self.config.add_notify(config.KEY_PROXY_PASSWORD,
                self.__proxy_password_key_changed)

    def __show_status_icon_key_changed(self, client, cnxn_id, entry, data):
        if not entry.value:
            self.status_icon_checkbutton.set_active(True)
        elif entry.value.type == gconf.VALUE_BOOL:
            value = entry.value.get_bool()
            status_icon = TrayIcon()
            # status_icon.icon.set_visible(value)
            if value:
                status_icon.icon.show_all()
            else:
                status_icon.icon.hide_all()

            self.status_icon_checkbutton.set_active(value)
            # Main window must be showed if no status icon is showed
            if not value:
                self.main_window_checkbutton.set_sensitive(False)
                self.config.show_main_window = True
            else:
                if not self.main_window_checkbutton.get_property("sensitive"):
                    self.main_window_checkbutton.set_sensitive(True)
        else:
            self.status_icon_checkbutton.set_active(True)

    def __show_main_window_key_changed(self, client, cnxn_id, entry, data):
        if not entry.value:
            self.main_window_checkbutton.set_active(True)
        elif entry.value.type == gconf.VALUE_BOOL:
            self.main_window_checkbutton.set_active(entry.value.get_bool())
        else:
            self.main_window_checkbutton.set_active(True)

    def __show_notifications_key_changed(self, client, cnxn_id, entry, data):
        if not entry.value:
            self.notifications_checkbutton.set_active(True)
        elif entry.value.type == gconf.VALUE_BOOL:
            self.notifications_checkbutton.set_active(entry.value.get_bool())
        else:
            self.notifications_checkbutton.set_active(True)

    def __show_quit_dialog_key_changed(self, client, cnxn_id, entry, data):
        if not entry.value:
            self.quit_dialog_checkbutton.set_active(True)
        elif entry.value.type == gconf.VALUE_BOOL:
            self.quit_dialog_checkbutton.set_active(entry.value.get_bool())
        else:
            self.quit_dialog_checkbutton.set_active(True)

    def __autostart_key_changed(self, client, cnxn_id, entry, data):
        if not entry.value:
            self.autostart_checkbutton.set_active(True)
        elif entry.value.type == gconf.VALUE_BOOL:
            value = entry.value.get_bool()
            self.autostart_checkbutton.set_active(value)

            autostart_dir = os.path.expanduser(AUTOSTART_DIR)
            if value:
                try:
                    item = gnomedesktop.item_new_from_basename(DESKTOP_FILE,
                            gnomedesktop.LOAD_ONLY_IF_EXISTS)
                except gobject.GError:
                    raise ValueError("File path not a .desktop file")

                if not item:
                    raise ValueError("URI not found")

                # Looks like gnomedesktop.DesktopItem.save(str, bool) isn't
                # implemented so copying manually for now.
                if not os.path.exists(autostart_dir):
                    os.makedirs(autostart_dir)

                shutil.copy2(item.get_location().replace("file://", ""),
                        autostart_dir)
            else:
                autostart_file = os.path.join(autostart_dir, DESKTOP_FILE)
                if os.path.exists(autostart_file):
                    os.remove(autostart_file)
        else:
            self.autostart_checkbutton.set_active(True)

    def __ask_for_location_key_changed(self, client, cnxn_id, entry, data):
        if not entry.value:
            self.ask_folder_radiobutton.set_active(True)
        elif entry.value.type == gconf.VALUE_BOOL:
            value = entry.value.get_bool()
            self.ask_folder_radiobutton.set_active(value)
            if not value:
                self.specify_folder_radiobutton.set_active(True)
        else:
            self.ask_folder_radiobutton.set_active(True)

    def __default_folder_key_changed(self, client, cnxn_id, entry, data):
        if entry.value.type == gconf.VALUE_STRING:
            folder = entry.value.to_string()
            self.default_folder_filechooserbutton.set_current_folder(folder)

    def __check_extensions_key_changed(self, client, cnxn_id, entry, data):
        if not entry.value:
            self.extensions_checkbutton.set_active(True)
            self.extensions_alignment.set_sensitive(True)
        elif entry.value.type == gconf.VALUE_BOOL:
            value = entry.value.get_bool()
            self.extensions_checkbutton.set_active(value)
            self.extensions_alignment.set_sensitive(value)
        else:
            self.extensions_checkbutton.set_active(True)
            self.extensions_alignment.set_sensitive(True)

    def __proxy_mode_key_changed(self, client, cnxn_id, entry, data):
        if entry.value.type == gconf.VALUE_STRING:
            mode = entry.value.to_string()
            if mode == "direct":
                self.direct_radiobutton.set_active(True)
                self.manual_proxy_vbox.set_sensitive(False)
            elif mode == "gnome":
                self.gnome_radiobutton.set_active(True)
                self.manual_proxy_vbox.set_sensitive(False)
                if self.config.use_http_proxy:
                    if self.config.use_http_proxy_auth:
                        self.download_manager.set_proxy("http", "http://%s:%s@%s:%s" % (self.config.http_proxy_user, self.config.http_proxy_pass, self.config.http_proxy_host, self.config.http_proxy_port))
                        if self.config.use_same_proxy:
                            self.download_manager.set_proxy("https", "https://%s:%s@%s:%s" % (self.config.http_proxy_user, self.config.http_proxy_pass, self.config.proxy_https_host, self.config.proxy_https_port))
                            self.download_manager.set_proxy("ftp", "ftp://%s:%s@%s:%s" % (self.config.http_proxy_user, self.config.http_proxy_pass, self.config.proxy_ftp_host, self.config.proxy_ftp_port))
                    else:
                        self.download_manager.set_proxy("http", "http://%s:%s" % (self.config.http_proxy_host, self.config.http_proxy_port))
                        self.download_manager.set_proxy("https", "https://%s:%s" % (self.config.proxy_https_host, self.config.proxy_https_port))
                        self.download_manager.set_proxy("ftp", "ftp://%s:%s" % (self.config.proxy_ftp_host, self.config.proxy_ftp_port))
            elif mode == "manual":
                self.manual_radiobutton.set_active(True)
                self.manual_proxy_vbox.set_sensitive(True)
                if self.config.proxy_auth:
                    self.download_manager.set_proxy("http", "http://%s:%s@%s:%s" % (self.config.proxy_user, self.config.proxy_password, self.config.proxy_host, self.config.proxy_port))
                else:
                    self.download_manager.set_proxy("http", "http://%s:%s" % (self.config.proxy_host, self.config.proxy_port))

    def __proxy_host_key_changed(self, client, cnxn_id, entry, data):
        if entry.value.type == gconf.VALUE_STRING:
            self.proxy_entry.set_text(entry.value.to_string())

    def __proxy_port_key_changed(self, client, cnxn_id, entry, data):
        if entry.value.type == gconf.VALUE_INT:
            self.proxy_port_spinbutton.set_value(entry.value.get_int())

    def __proxy_auth_key_changed(self, client, cnxn_id, entry, data):
        if entry.value.type == gconf.VALUE_BOOL:
            auth = entry.value.get_bool()
            self.proxy_auth_checkbutton.set_active(auth)
            self.proxy_auth_hbox.set_sensitive(auth)

    def __proxy_user_key_changed(self, client, cnxn_id, entry, data):
        if entry.value.type == gconf.VALUE_STRING:
            self.proxy_user_entry.set_text(entry.value.to_string())

    def __proxy_password_key_changed(self, client, cnxn_id, entry, data):
        if entry.value.type == gconf.VALUE_STRING:
            self.proxy_password_entry.set_text(entry.value.to_string())

    def __status_icon_checkbutton_toggled(self, checkbutton):
        self.config.show_status_icon = checkbutton.get_active()

    def __main_window_checkbutton_toggled(self, checkbutton):
        self.config.show_main_window = checkbutton.get_active()

    def __notifications_checkbutton_toggled(self, checkbutton):
        self.config.show_notifications = checkbutton.get_active()

    def __quit_dialog_checkbutton_toggled(self, checkbutton):
        self.config.show_quit_dialog = checkbutton.get_active()

    def __autostart_checkbutton_toggled(self, checkbutton):
        self.config.autostart = checkbutton.get_active()

    def __ask_folder_radiobutton_toggled(self, radiobutton):
        active = radiobutton.get_active()
        self.config.ask_for_location = active
        self.default_folder_filechooserbutton.set_sensitive(not active)

    def __default_folder_filechooserbutton_current_folder_changed(self,
            filechooserbutton):
        folder = filechooserbutton.get_current_folder()
        # Prevent infinite loop
        if self.config.default_folder != folder:
            self.config.default_folder = folder

    def __extensions_checkbutton_toggled(self, checkbutton):
        self.config.check_extensions = checkbutton.get_active()

    def __extensions_treeview_selection_changed(self, selection):
        """When selection changes set sensitivity appropriately."""
        (extensions_model, extensions_iter) = selection.get_selected()
        if extensions_iter:
            self.remove_extension_button.set_sensitive(True)
        else:
            self.remove_extension_button.set_sensitive(False)

    def __add_extension_button_clicked(self, button):
        extensions = self.config.extensions
        extensions.append("*.*")
        self.config.extensions = extensions

        extension_folders = self.config.extension_folders
        extension_folders.append(self.config.default_folder)
        self.config.extension_folders = extension_folders

        iter = self.extensions_model.append(("*.*", self.config.default_folder))
        path = self.extensions_model.get_path(iter)
        self.extensions_treeview.set_cursor_on_cell(path,
                self.extension_treeview_column, self.extension_cell_renderer,
                True)

    def __remove_extension_button_clicked(self, button):
        selection = self.extensions_treeview.get_selection()
        (extensions_model, extensions_iter) = selection.get_selected()
        if extensions_iter:
            extension = extensions_model.get_value(extensions_iter, 0)
            extension_folder = extensions_model.get_value(extensions_iter, 1)
            extensions_model.remove(extensions_iter)
            extensions = self.config.extensions
            if extension in extensions:
                extensions.remove(extension)
                self.config.extensions = extensions
            extension_folders = self.config.extension_folders
            if extension_folder in extension_folders:
                extension_folders.remove(extension_folder)
                self.config.extension_folders = extension_folders

    def __direct_radiobutton_toggled(self, radiobutton):
        if radiobutton.get_active():
            self.config.proxy_mode = "direct"

    def __gnome_radiobutton_toggled(self, radiobutton):
        if radiobutton.get_active():
            self.config.proxy_mode = "gnome"

    def __manual_radiobutton_toggled(self, radiobutton):
        if radiobutton.get_active():
            self.config.proxy_mode = "manual"

    def __proxy_entry_changed(self, entry):
        self.config.proxy_host = entry.get_text()

    def __proxy_port_spinbutton_value_changed(self, spinbutton):
        self.config.proxy_port = spinbutton.get_value_as_int()

    def __proxy_auth_checkbutton_toggled(self, checkbutton):
        self.config.proxy_auth = checkbutton.get_active()

    def __proxy_user_entry_changed(self, entry):
        self.config.proxy_user = entry.get_text()

    def __proxy_password_entry_changed(self, entry):
        self.config.proxy_password = entry.get_text()

    def __close_button_clicked(self, button):
        self.dialog.hide()

class QuitDialog:
    def __init__(self):
        self.config = config.Configuration()

        self.__get_widgets()
        self.__connect_widgets()

        self.config.add_notify(config.KEY_SHOW_QUIT_DIALOG,
                self.__show_quit_dialog_key_changed)

        self.show_again_checkbutton.set_active(not self.config.show_quit_dialog)

    def __get_widgets(self):
        xml = gtk.glade.XML(gui.glade_file, domain=NAME.lower())

        self.dialog = xml.get_widget("quit_dialog")

        self.show_again_checkbutton = xml.get_widget("show_quit_dialog_checkbutton")

        self.no_button = xml.get_widget("quit_no_button")
        self.yes_button = xml.get_widget("quit_yes_button")

    def __connect_widgets(self):
        self.dialog.connect("delete-event", self.__dialog_delete)
        self.show_again_checkbutton.connect("toggled",
                self.__show_again_checkbutton_toggled)
        self.no_button.connect("clicked", self.__button_clicked)
        self.yes_button.connect("clicked", self.__button_clicked)

    def __dialog_delete(self, dialog, event):
        self.dialog.destroy()
        return False

    def __show_again_checkbutton_toggled(self, checkbutton):
        self.config.show_quit_dialog = not checkbutton.get_active()

    def __button_clicked(self, button):
        self.dialog.destroy()

    def __show_quit_dialog_key_changed(self, client, cnxn_id, entry, data):
        if not entry.value:
            self.show_again_checkbutton.set_active(True)
        elif entry.value.type == gconf.VALUE_BOOL:
            self.show_again_checkbutton.set_active(not entry.value.get_bool())
        else:
            self.show_again_checkbutton.set_active(True)

# vim: set sw=4 et sts=4 tw=79 fo+=l:
