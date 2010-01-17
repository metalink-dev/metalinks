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
import traceback
from gettext import gettext as _

import gtk
import gtk.gdk
import gobject
import gconf
import gnomevfs
import gnome.ui

import config
import download
import gui
import utils
from download import CONNECTING, DOWNLOADING, PAUSED, CANCELED, COMPLETED
from dialogs import AboutDialog, AddDownloadDialog, DetailsDialog, ErrorDialog, PreferencesDialog, QuitDialog
from gget import NAME

# D&D targets
TARGET_URI_LIST = 0
TARGET_NETSCAPE_URL = 1

class MainWindow:
    def __init__(self, config, download_list):
        self.config = config
        self.download_list = download_list
        self.download_list.connect("download-added", self.__download_added)
        self.download_list.connect("download-removed", self.__download_removed)

        self.__get_widgets()

        targets = [("text/uri-list", 0, TARGET_URI_LIST),
                ("x-url/http", 0, TARGET_NETSCAPE_URL),
                ("x-url/ftp", 0, TARGET_NETSCAPE_URL),
                ("_NETSCAPE_URL", 0, TARGET_NETSCAPE_URL)]
        self.window.drag_dest_set(gtk.DEST_DEFAULT_ALL |
                gtk.DEST_DEFAULT_HIGHLIGHT, targets, gtk.gdk.ACTION_COPY)

        self.__make_downloads_treeview()

        self.__connect_widgets()
        self.__add_config_notifications()

        # Set widget states from configuration
        self.window.set_default_size(self.config.window_width,
                self.config.window_height)
        self.window.move(self.config.window_position_x,
                self.config.window_position_y)

        self.show_toolbar_menu_item.set_active(self.config.show_toolbar)
        # self.show_statusbar_menu_item.set_active(self.config.show_statusbar)

        self.toolbar.props.visible = self.config.show_toolbar
        self.__set_toolbar_style(self.config.toolbar_style)

        self.show_status_menu_item.set_active(self.config.show_status)
        self.show_current_size_menu_item.set_active(self.config.show_current_size)
        self.show_total_size_menu_item.set_active(self.config.show_total_size)
        self.show_progress_menu_item.set_active(self.config.show_progress)
        self.show_speed_menu_item.set_active(self.config.show_speed)
        self.show_eta_menu_item.set_active(self.config.show_eta)

        self.status_treeview_column.props.visible = self.config.show_status
        self.size_treeview_column.props.visible = self.config.show_current_size
        self.total_size_treeview_column.props.visible = self.config.show_total_size
        self.progress_treeview_column.props.visible = self.config.show_progress
        self.speed_treeview_column.props.visible = self.config.show_speed
        self.eta_treeview_column.props.visible = self.config.show_eta

        # self.statusbar.props.visible = self.config.show_statusbar

    def __get_widgets(self):
        """Get widgets from the glade file."""
        xml = gtk.glade.XML(gui.glade_file, domain=NAME.lower())

        self.window = xml.get_widget("main_window")

        # File menu
        self.add_menu_item = xml.get_widget("add_menu_item")
        self.quit_menu_item = xml.get_widget("quit_menu_item")

        # Edit menu
        self.select_all_menu_item = xml.get_widget("select_all_menu_item")
        self.unselect_all_menu_item = xml.get_widget("unselect_all_menu_item")
        self.preferences_menu_item = xml.get_widget("preferences_menu_item")

        # Show menu
        self.show_toolbar_menu_item = xml.get_widget("show_toolbar_menu_item")
        # self.show_statusbar_menu_item = xml.get_widget("show_statusbar_menu_item")
        self.show_status_menu_item = xml.get_widget("show_status_menu_item")
        self.show_current_size_menu_item = xml.get_widget("show_current_size_menu_item")
        self.show_total_size_menu_item = xml.get_widget("show_total_size_menu_item")
        self.show_progress_menu_item = xml.get_widget("show_progress_menu_item")
        self.show_speed_menu_item = xml.get_widget("show_speed_menu_item")
        self.show_eta_menu_item = xml.get_widget("show_eta_menu_item")

        # Help menu
        self.about_menu_item = xml.get_widget("about_menu_item")

        # Toolbar
        self.toolbar = xml.get_widget("toolbar")

        self.add_tool_button = xml.get_widget("add_tool_button")
        self.pause_tool_button = xml.get_widget("pause_tool_button")
        self.resume_tool_button = xml.get_widget("resume_tool_button")
        self.cancel_tool_button = xml.get_widget("cancel_tool_button")
        self.remove_tool_button = xml.get_widget("remove_tool_button")
        self.clear_tool_button = xml.get_widget("clear_tool_button")
        self.details_tool_button = xml.get_widget("details_tool_button")

        self.downloads_treeview = xml.get_widget("downloads_treeview")

        # self.statusbar = xml.get_widget("statusbar")

    def __make_downloads_treeview(self):
        """Constructs the treeview containing downloads."""
        self.downloads_model = gtk.ListStore(object)
        self.downloads_treeview.set_model(self.downloads_model)
        self.downloads_treeview_selection = self.downloads_treeview.get_selection()
        self.downloads_treeview_selection.set_mode(gtk.SELECTION_MULTIPLE)

        cell_renderer_pixbuf = gtk.CellRendererPixbuf()
        cell_renderer_pixbuf.props.xpad = 3
        # cell_renderer_pixbuf.props.ypad = 3

        cell_renderer_text = gtk.CellRendererText()
        cell_renderer_text.props.xpad = 3
        # cell_renderer_text.props.ypad = 3

        cell_renderer_progress = gtk.CellRendererProgress()
        # cell_renderer_progress.props.xpad = 3
        cell_renderer_progress.props.ypad = 8

        # Name column
        self.name_treeview_column = gtk.TreeViewColumn(_("Name"))
        self.name_treeview_column.pack_start(cell_renderer_pixbuf)
        self.name_treeview_column.set_cell_data_func(cell_renderer_pixbuf,
                self.__image_cell_data_func)
        self.name_treeview_column.pack_start(cell_renderer_text)
        self.name_treeview_column.set_cell_data_func(cell_renderer_text,
                self.__name_cell_data_func)
        self.downloads_treeview.append_column(self.name_treeview_column)
        self.downloads_treeview.set_search_column(1)
        self.downloads_treeview.set_search_equal_func(self.__downloads_treeview_search_equal)

        # Status column
        self.status_treeview_column = gtk.TreeViewColumn(_("Status"),
                cell_renderer_text)
        self.status_treeview_column.set_cell_data_func(cell_renderer_text,
                self.__status_cell_data_func)
        self.downloads_treeview.append_column(self.status_treeview_column)

        # Current size column
        self.size_treeview_column = gtk.TreeViewColumn(_("Current size"),
                cell_renderer_text)
        self.size_treeview_column.set_cell_data_func(cell_renderer_text,
                self.__size_cell_data_func)
        self.downloads_treeview.append_column(self.size_treeview_column)

        # Total size column
        self.total_size_treeview_column = gtk.TreeViewColumn(_("Total size"),
                cell_renderer_text)
        self.total_size_treeview_column.set_cell_data_func(cell_renderer_text,
                self.__total_size_cell_data_func)
        self.downloads_treeview.append_column(self.total_size_treeview_column)

        # Progress column
        self.progress_treeview_column = gtk.TreeViewColumn(_("Progress"),
                cell_renderer_progress)
        self.progress_treeview_column.set_cell_data_func(cell_renderer_progress,
                self.__progress_cell_data_func)
        self.downloads_treeview.append_column(self.progress_treeview_column)

        # Speed column
        self.speed_treeview_column = gtk.TreeViewColumn(_("Speed"),
                cell_renderer_text)
        self.speed_treeview_column.set_cell_data_func(cell_renderer_text,
                self.__speed_cell_data_func)
        self.downloads_treeview.append_column(self.speed_treeview_column)

        # ETA column
        self.eta_treeview_column = gtk.TreeViewColumn(_("ETA"),
                cell_renderer_text)
        self.eta_treeview_column.set_cell_data_func(cell_renderer_text,
                self.__eta_cell_data_func)
        self.downloads_treeview.append_column(self.eta_treeview_column)

        # Context menu
        self.downloads_treeview_menu = gtk.Menu()
        self.pause_imi = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PAUSE)
        self.pause_imi.show()
        self.downloads_treeview_menu.append(self.pause_imi)

        self.resume_imi = gtk.ImageMenuItem(_("Resume"))
        self.resume_imi.get_image().set_from_stock(gtk.STOCK_MEDIA_PLAY,
                gtk.ICON_SIZE_MENU)
        self.resume_imi.set_sensitive(False)
        self.downloads_treeview_menu.append(self.resume_imi)

        self.cancel_imi = gtk.ImageMenuItem(gtk.STOCK_CANCEL)
        self.cancel_imi.show()
        self.downloads_treeview_menu.append(self.cancel_imi)

        self.remove_imi = gtk.ImageMenuItem(gtk.STOCK_REMOVE)
        self.remove_imi.show()
        self.downloads_treeview_menu.append(self.remove_imi)

        separator_imi = gtk.SeparatorMenuItem()
        separator_imi.show()
        self.downloads_treeview_menu.append(separator_imi)

        self.open_imi = gtk.ImageMenuItem(_("Open"))
        self.open_imi.show()
        self.downloads_treeview_menu.append(self.open_imi)

        self.open_folder_imi = gtk.ImageMenuItem(_("Open folder"))
        self.open_folder_imi.get_image().set_from_stock(gtk.STOCK_OPEN,
                gtk.ICON_SIZE_MENU)
        self.open_folder_imi.show()
        self.downloads_treeview_menu.append(self.open_folder_imi)

        separator_imi2 = gtk.SeparatorMenuItem()
        separator_imi2.show()
        self.downloads_treeview_menu.append(separator_imi2)

        self.details_imi = gtk.ImageMenuItem(_("Details"))
        self.details_imi.get_image().set_from_stock(gtk.STOCK_INFO,
                gtk.ICON_SIZE_MENU)
        self.details_imi.show()
        self.downloads_treeview_menu.append(self.details_imi)

    def __image_cell_data_func(self, column, cell, model, iter):
        """Data function for the image of the download."""
        download = model.get_value(iter, 0)
        cell.props.pixbuf = download.pixbuf

    def __name_cell_data_func(self, column, cell, model, iter):
        """Data function for the name of downloads."""
        download = model.get_value(iter, 0)
        cell.props.text = download.file_name

    def __downloads_treeview_search_equal(self, model, column, key, iter):
        """Compare method for search in the downloads treeview."""
        download = model.get_value(iter, 0)
        return key.lower() not in download.file_name.lower()

    def __status_cell_data_func(self, column, cell, model, iter):
        """Data function for the status of downloads."""
        download = model.get_value(iter, 0)
        cell.props.text = download.get_status_string()

    def __size_cell_data_func(self, column, cell, model, iter):
        """Data function for the file size of downloads."""
        download = model.get_value(iter, 0)
        cell.props.text = utils.get_readable_size(download.current_size)

    def __total_size_cell_data_func(self, column, cell, model, iter):
        """Data function for the file size of downloads."""
        download = model.get_value(iter, 0)
        cell.props.text = utils.get_readable_size(download.total_size)

    def __progress_cell_data_func(self, column, cell, model, iter):
        """Data function for the progress bar of downloads."""
        download = model.get_value(iter, 0)
        cell.props.value = download.percent_complete

    def __speed_cell_data_func(self, column, cell, model, iter):
        """Data function for the speed of downloads."""
        download = model.get_value(iter, 0)
        cell.props.text = utils.get_readable_speed(download.bit_rate)

    def __eta_cell_data_func(self, column, cell, model, iter):
        """Data function for estemated time of arrival (ETA) of downloads."""
        download = model.get_value(iter, 0)
        size = download.total_size - download.current_size
        cell.props.text = utils.get_readable_eta(size, download.bit_rate)

    def __connect_widgets(self):
        """Connect to the widget signals we are interested in."""
        self.window.connect("destroy", self.quit)
        self.window.connect("configure-event", self.__window_configure_event)
        self.window.connect("drag_data_received",
                self.__window_drag_data_received)

        # File menu
        self.add_menu_item.connect("activate", self.show_add_download_dialog)
        self.quit_menu_item.connect("activate", self.quit)

        # Edit menu
        self.select_all_menu_item.connect("activate", self.__select_all, True)
        self.unselect_all_menu_item.connect("activate", self.__select_all,
                False)
        self.preferences_menu_item.connect("activate",
                self.preferences_menu_item_activate)

        # Show menu
        self.show_toolbar_menu_item.connect("toggled",
                self.__show_toolbar_menu_item_toggled)
        # self.show_statusbar_menu_item.connect("toggled",
                # self.__show_statusbar_menu_item_toggled)

        self.show_status_menu_item.connect("toggled",
                self.__show_status_menu_item_toggled)
        self.show_current_size_menu_item.connect("toggled",
                self.__show_current_size_menu_item_toggled)
        self.show_total_size_menu_item.connect("toggled",
                self.__show_total_size_menu_item_toggled)
        self.show_progress_menu_item.connect("toggled",
                self.__show_progress_menu_item_toggled)
        self.show_speed_menu_item.connect("toggled",
                self.__show_speed_menu_item_toggled)
        self.show_eta_menu_item.connect("toggled",
                self.__show_eta_menu_item_toggled)

        # Help
        self.about_menu_item.connect("activate",
                self.__about_menu_item_activate)

        # Toolbar
        self.add_tool_button.connect("clicked", self.show_add_download_dialog)
        self.pause_tool_button.connect("clicked",
                self.__pause_tool_button_clicked)
        self.resume_tool_button.connect("clicked",
                self.__resume_tool_button_clicked)
        self.cancel_tool_button.connect("clicked",
                self.__cancel_selected_downloads)
        self.remove_tool_button.connect("clicked",
                self.__remove_selected_downloads)
        self.clear_tool_button.connect("clicked",
                self.__clear_tool_button_clicked)
        self.details_tool_button.connect("clicked",
                self.__details_selected_download)

        # Downloads model and treeview
        self.downloads_model.connect("row-deleted",
                self.__downloads_model_row_deleted)
        self.downloads_model.connect("row-inserted",
                self.__downloads_models_row_inserted)
        self.downloads_treeview_selection.connect("changed",
                self.__downloads_treeview_selection_changed)
        self.downloads_treeview.connect("row-activated",
                self.__downloads_treeview_row_activated)
        self.downloads_treeview.connect("button-press-event",
                self.__downloads_treeview_button_press_event,
                self.downloads_treeview_menu)
        self.downloads_treeview.connect("key-press-event",
                self.__downloads_treeview_key_press_event)

        self.pause_imi.connect("activate", self.__pause_imi_activate)
        self.resume_imi.connect("activate", self.__resume_imi_activate)
        self.cancel_imi.connect("activate", self.__cancel_selected_downloads)
        self.remove_imi.connect("activate", self.__remove_selected_downloads)
        self.open_imi.connect("activate", self.__open_imi_activate)
        self.open_folder_imi.connect("activate",
                self.__open_folder_imi_activate)
        self.details_imi.connect("activate", self.__details_selected_download)

    def __window_configure_event(self, widget, event):
        """Saves the window geometry and position"""
        (width, height) = widget.get_size()
        self.config.window_width = width
        self.config.window_height = height
        (position_x, position_y) = widget.get_position()
        self.config.window_position_x = position_x
        self.config.window_position_y = position_y
        return False # Propagate signal further

    def __window_drag_data_received(self, widget, context, x, y, selection,
            target_type, time):
        if target_type == TARGET_URI_LIST:
            # TODO: Need gnome_vfs_uri_list_parse and gnome_vfs_uri_to_string
            # but they seem to be missing in the binding
            pass
        elif target_type == TARGET_NETSCAPE_URL:
            uri = selection.data.split()[0]
        else:
            context.finish(False, True, time)
            return True

        if self.config.ask_for_location:
            add = AddDownloadDialog(uri)
            add.dialog.run()
        else:
            self.download_list.add_download(uri, self.config.default_folder)
            context.finish(True, False, time)

    def show_add_download_dialog(self, widget):
        """Show the dialog used for adding a new download."""
        add = AddDownloadDialog()
        add.dialog.run()

    def preferences_menu_item_activate(self, menu_item):
        """Show the preferences dialog."""
        pd = PreferencesDialog(self.config)
        pd.dialog.show()

    def __select_all(self, menu_item, select_all):
        """Select/Unselect all downloads"""
        if select_all:
            self.downloads_treeview_selection.select_all()
        else:
            self.downloads_treeview_selection.unselect_all()

    def __show_toolbar_menu_item_toggled(self, menu_item):
        """Show/Hide toolbar"""
        self.config.show_toolbar = menu_item.get_active()

    # def __show_statusbar_menu_item_toggled(self, menu_item):
        # """Show/Hide statusbar"""
        # self.config.show_statusbar = menu_item.get_active()

    def __show_status_menu_item_toggled(self, menu_item):
        """Show/Hide Status column"""
        self.config.show_status = menu_item.get_active()

    def __show_current_size_menu_item_toggled(self, menu_item):
        """Show/Hide Current size column"""
        self.config.show_current_size = menu_item.get_active()

    def __show_total_size_menu_item_toggled(self, menu_item):
        """Show/Hide Total size column"""
        self.config.show_total_size = menu_item.get_active()

    def __show_progress_menu_item_toggled(self, menu_item):
        """Show/Hide Progress column"""
        self.config.show_progress = menu_item.get_active()

    def __show_speed_menu_item_toggled(self, menu_item):
        """Show/Hide Speed column"""
        self.config.show_speed = menu_item.get_active()

    def __show_eta_menu_item_toggled(self, menu_item):
        """Show/Hide ETA column"""
        self.config.show_eta = menu_item.get_active()

    def __about_menu_item_activate(self, menu_item):
        """Show the about dialog."""
        ad = AboutDialog()
        ad.run()

    def __downloads_model_row_deleted(self, model, path):
        """Called when a new download is removed from the model."""
        number_rows = len(model)
        if number_rows <= 0:
            self.clear_tool_button.set_sensitive(False)
            self.select_all_menu_item.set_sensitive(False)
            self.unselect_all_menu_item.set_sensitive(False)

    def __downloads_models_row_inserted(self, model, path, iter):
        """Called when a new download is added to the model."""
        number_rows = len(model)
        if number_rows == 1:
            self.select_all_menu_item.set_sensitive(True)

    def __downloads_treeview_selection_changed(self, selection):
        """Called when selection changes. Sets download releated widgets and
        their sensitivity."""
        downloads = gui.get_selected_values(self.downloads_treeview)
        number_selected = selection.count_selected_rows()
        # Disable tool buttons and menu items if nothing is selected, else
        # enable the ones that should be
        if number_selected < 1:
            self.__download_widgets_set_sensitive(False)
        elif number_selected == 1:
            self.unselect_all_menu_item.set_sensitive(True)
            self.remove_tool_button.set_sensitive(True)
            self.remove_imi.set_sensitive(True)
            self.details_tool_button.set_sensitive(True)
            self.details_imi.set_sensitive(True)
            if downloads:
                status = downloads[0].status
                self.__set_widgets_sensitivity_for_status(status)

        elif number_selected > 1:
            self.__download_widgets_set_sensitive(False)
            self.unselect_all_menu_item.set_sensitive(True)
            self.remove_tool_button.set_sensitive(True)
            self.remove_imi.set_sensitive(True)

            has_paused = has_canceled = has_active = False
            if downloads:
                for download in downloads:
                    if download.status == PAUSED:
                        has_paused = True
                    elif download.status == CANCELED:
                        has_canceled = True
                    elif download.status == CONNECTING or \
                         download.status == DOWNLOADING:
                        has_active = True

            if has_paused or has_canceled:
                self.resume_tool_button.set_sensitive(True)
                self.resume_imi.set_sensitive(True)

            if has_active:
                self.pause_tool_button.set_sensitive(True)
                self.pause_imi.set_sensitive(True)
                self.cancel_tool_button.set_sensitive(True)
                self.cancel_imi.set_sensitive(True)

            self.pause_imi.props.visible = self.pause_imi.props.sensitive
            self.resume_imi.props.visible = self.resume_imi.props.sensitive
            self.cancel_imi.props.visible = self.cancel_imi.props.sensitive

            # Details should only be possible if one row is selected
            self.details_tool_button.set_sensitive(False)
            self.details_imi.set_sensitive(False)

        # Select all should not be availible if all is selected already
        if number_selected == len(self.downloads_model):
            self.select_all_menu_item.set_sensitive(False)
        elif not self.select_all_menu_item.props.sensitive:
            self.select_all_menu_item.set_sensitive(True)

    def __download_widgets_set_sensitive(self, sensitive):
        """Sets the sensitivity property for widgets associated with a the
        downloads treeview."""
        self.pause_tool_button.set_sensitive(sensitive)
        self.pause_imi.set_sensitive(sensitive)
        self.resume_tool_button.set_sensitive(sensitive)
        self.resume_imi.set_sensitive(sensitive)
        self.cancel_tool_button.set_sensitive(sensitive)
        self.cancel_imi.set_sensitive(sensitive)
        self.remove_tool_button.set_sensitive(sensitive)
        self.remove_imi.set_sensitive(sensitive)
        self.details_tool_button.set_sensitive(sensitive)
        self.details_imi.set_sensitive(sensitive)

    def __set_widgets_sensitivity_for_status(self, status):
        """Sets the appropriate sensitivity property for widgets based on the
        given status."""

        if status == COMPLETED:
            self.pause_tool_button.set_sensitive(False)
            self.pause_imi.set_sensitive(False)
            self.resume_tool_button.set_sensitive(False)
            self.resume_imi.set_sensitive(False)
            self.cancel_tool_button.set_sensitive(False)
            self.cancel_imi.set_sensitive(False)

        elif status == CANCELED:
            self.pause_tool_button.set_sensitive(False)
            self.pause_imi.set_sensitive(False)
            self.resume_tool_button.set_sensitive(True)
            self.resume_imi.set_sensitive(True)
            self.cancel_tool_button.set_sensitive(False)
            self.cancel_imi.set_sensitive(False)

        elif status == PAUSED:
            self.pause_tool_button.set_sensitive(False)
            self.pause_imi.set_sensitive(False)
            self.resume_tool_button.set_sensitive(True)
            self.resume_imi.set_sensitive(True)
            self.cancel_tool_button.set_sensitive(True)
            self.cancel_imi.set_sensitive(True)

        elif status == DOWNLOADING or status == CONNECTING:
            self.pause_tool_button.set_sensitive(True)
            self.pause_imi.set_sensitive(True)
            self.resume_tool_button.set_sensitive(False)
            self.resume_imi.set_sensitive(False)
            self.cancel_tool_button.set_sensitive(True)
            self.cancel_imi.set_sensitive(True)

        self.pause_imi.props.visible = self.pause_imi.props.sensitive
        self.resume_imi.props.visible = self.resume_imi.props.sensitive
        self.cancel_imi.props.visible = self.cancel_imi.props.sensitive

    def __downloads_treeview_row_activated(self, treeview, path, column):
        """Called when a download is double-clicked. Opens the file with the
        associated program."""
        download = self.downloads_model[path][0]
        if download:
            if not download.is_metalink:
                gui.open_file_on_screen(download.file, treeview.get_screen())

    def __downloads_treeview_button_press_event(self, treeview, event, menu):
        """Show context menu for downloads treeview"""
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            n_selected = self.downloads_treeview_selection.count_selected_rows()
            downloads = gui.get_selected_values(self.downloads_treeview)
            if n_selected == 1:
                if downloads:
                    self.open_imi.set_sensitive(not downloads[0].is_metalink)
                self.open_folder_imi.set_sensitive(True)
                self.details_imi.set_sensitive(True)
                menu.popup(None, None, None, event.button, event.time)
                return True
            elif n_selected > 1:
                self.open_imi.set_sensitive(False)
                self.open_folder_imi.set_sensitive(False)
                self.details_imi.set_sensitive(False)
                menu.popup(None, None, None, event.button, event.time)
                return True
        return False

    def __downloads_treeview_key_press_event(self, treeview, event):
        """Called when a key is pressed on the downloads treeview."""
        if event.keyval == gtk.keysyms.Delete:
            self.__remove_selected_downloads()

    def __pause_tool_button_clicked(self, tool_button):
        self.__pause_selected_downloads()

    def __resume_tool_button_clicked(self, tool_button):
        self.__pause_selected_downloads(False)

    def __clear_tool_button_clicked(self, tool_button):
        self.download_list.remove_completed_downloads()

    def __pause_imi_activate(self, imagemenuitem):
        self.__pause_selected_downloads()

    def __resume_imi_activate(self, imagemenuitem):
        self.__pause_selected_downloads(False)

    def __pause_selected_downloads(self, pause=True):
        downloads = gui.get_selected_values(self.downloads_treeview)
        if downloads:
            for download in downloads:
                if pause:
                    download.pause()
                else:
                    download.resume()

    def __cancel_selected_downloads(self, widget):
        """Cancels the selected download in DownloadList."""
        downloads = gui.get_selected_values(self.downloads_treeview)
        for download in downloads:
            download.cancel()

    def __remove_selected_downloads(self, widget=None):
        """Removes the selected download from DownloadList."""
        downloads = gui.get_selected_values(self.downloads_treeview)
        for download in downloads:
            self.download_list.remove_download(download)

    def __open_imi_activate(self, imagemenuitem):
        """Opens the downloaded file with the associated program."""
        downloads = gui.get_selected_values(self.downloads_treeview)
        if downloads:
            gui.open_file_on_screen(downloads[0].file,
                    imagemenuitem.get_screen())

    def __open_folder_imi_activate(self, imagemenuitem):
        """Opens the folder containing the download."""
        downloads = gui.get_selected_values(self.downloads_treeview)
        if downloads:
            uri = gnomevfs.make_uri_from_input(downloads[0].path)
            gnome.ui.url_show_on_screen(uri, imagemenuitem.get_screen())

    def __details_selected_download(self, widget):
        """Shows details for the selected download. The details option will
        only be availble when only one download in selected."""
        downloads = gui.get_selected_values(self.downloads_treeview)
        if downloads:
            DetailsDialog(downloads[0])

    def quit(self, widget=None):
        """Quits the application. Called from various places."""
        if self.download_list.has_active_downloads() and self.config.show_quit_dialog:
            quit_dialog = QuitDialog()
            if quit_dialog.dialog.run() in [-4, 0]:
                return
        gtk.main_quit()

    def __add_config_notifications(self):
        """Adds callbacks which gets called when configuration keys changes
        in gconf."""
        self.config.add_notify(config.KEY_SHOW_TOOLBAR,
                self.__show_toolbar_key_changed)
        self.config.add_notify(config.KEY_TOOLBAR_STYLE,
                self.__toolbar_style_key_changed)
        self.config.add_notify(config.KEY_SHOW_STATUS,
                self.__show_status_key_changed)
        self.config.add_notify(config.KEY_SHOW_CURRENT_SIZE,
                self.__show_current_size_key_changed)
        self.config.add_notify(config.KEY_SHOW_TOTAL_SIZE,
                self.__show_total_size_key_changed)
        self.config.add_notify(config.KEY_SHOW_PROGRESS,
                self.__show_progress_key_changed)
        self.config.add_notify(config.KEY_SHOW_SPEED,
                self.__show_speed_key_changed)
        self.config.add_notify(config.KEY_SHOW_ETA,
                self.__show_eta_key_changed)
        # self.config.add_notify(config.KEY_SHOW_STATUSBAR,
                # self.__show_statusbar_key_changed)

    def __show_toolbar_key_changed(self, client, cnxn_id, entry, data):
        """Called when the gconf key for toolbar visibility is changed"""
        if not entry.value:
            self.toolbar.props.visible = True
        elif entry.value.type == gconf.VALUE_BOOL:
            self.toolbar.props.visible = entry.value.get_bool()
        else:
            self.toolbar.props.visible = True

    def __toolbar_style_key_changed(self, client, cnxn_id, entry, data):
        """Called when the gconf key for toolbar style is changed"""
        if not entry.value:
            self.__set_toolbar_style("both")
        elif entry.value.type == gconf.VALUE_STRING:
            self.__set_toolbar_style(entry.value.get_string())
        else:
            self.__set_toolbar_style("both")

    def __set_toolbar_style(self, toolbar_style="both"):
        """Sets the toolbar to the specified style."""
        if toolbar_style == "icons":
            self.toolbar.set_style(gtk.TOOLBAR_ICONS)
        elif toolbar_style == "both":
            self.toolbar.set_style(gtk.TOOLBAR_BOTH)
        elif toolbar_style == "both-horiz":
            self.toolbar.set_style(gtk.TOOLBAR_BOTH_HORIZ)
        elif toolbar_style == "text":
            self.toolbar.set_style(gtk.TOOLBAR_TEXT)

    # def __show_statusbar_key_changed(self, client, cnxn_id, entry, data):
        # """Called when the gconf key for statusbar visibility is changed"""
        # if not entry.value:
            # self.statusbar.props.visible = True
        # elif entry.value.type == gconf.VALUE_BOOL:
            # self.statusbar.props.visible = entry.value.get_bool()
        # else:
            # self.statusbar.props.visible = True

    def __show_status_key_changed(self, client, cnxn_id, entry, data):
        """Called when the gconf key for status visibility is changed"""
        if not entry.value:
            self.status_treeview_column.props.visible = True
        elif entry.value.type == gconf.VALUE_BOOL:
            self.status_treeview_column.props.visible = entry.value.get_bool()
        else:
            self.status_treeview_column.props.visible = True

    def __show_current_size_key_changed(self, client, cnxn_id, entry, data):
        """Called when the gconf key for current size visibility is changed"""
        if not entry.value:
            self.size_treeview_column.props.visible = True
        elif entry.value.type == gconf.VALUE_BOOL:
            self.size_treeview_column.props.visible = entry.value.get_bool()
        else:
            self.size_treeview_column.props.visible = True

    def __show_total_size_key_changed(self, client, cnxn_id, entry, data):
        """Called when the gconf key for total size visibility is changed"""
        if not entry.value:
            self.total_size_treeview_column.props.visible = True
        elif entry.value.type == gconf.VALUE_BOOL:
            self.total_size_treeview_column.props.visible = entry.value.get_bool()
        else:
            self.total_size_treeview_column.props.visible = True

    def __show_progress_key_changed(self, client, cnxn_id, entry, data):
        """Called when the gconf key for progress visibility is changed"""
        if not entry.value:
            self.progress_treeview_column.props.visible = True
        elif entry.value.type == gconf.VALUE_BOOL:
            self.progress_treeview_column.props.visible = entry.value.get_bool()
        else:
            self.progress_treeview_column.props.visible = True

    def __show_speed_key_changed(self, client, cnxn_id, entry, data):
        """Called when the gconf key for speed visibility is changed"""
        if not entry.value:
            self.speed_treeview_column.props.visible = True
        elif entry.value.type == gconf.VALUE_BOOL:
            self.speed_treeview_column.props.visible = entry.value.get_bool()
        else:
            self.progress_treeview_column.props.visible = True

    def __show_eta_key_changed(self, client, cnxn_id, entry, data):
        """Called when the gconf key for eta visibility is changed"""
        if not entry.value:
            self.eta_treeview_column.props.visible = True
        elif entry.value.type == gconf.VALUE_BOOL:
            self.eta_treeview_column.props.visible = entry.value.get_bool()
        else:
            self.eta_treeview_column.props.visible = True

    def __download_added(self, download_list, download):
        """Called when a new download is added to DownloadList. Adds the
        download to the treeview model and sets up the update handler."""
        self.downloads_model.append([download])
        download.connect("update", self.__download_update)
        download.connect("status-changed", self.__download_status_changed)
        gui.queue_resize(self.downloads_treeview)

        # Enable clear button if necessary
        if not self.clear_tool_button.props.sensitive and \
           download.status == COMPLETED:
            self.clear_tool_button.set_sensitive(True)

    def __download_removed(self, download_list, download):
        """Called when a download is removed from DownloadList. Removes the
        download from the treeview model. Also checks if there a any completed
        downloads in the list so the clear button can be enabled/disabled
        appropriately."""
        downloads_iter = self.downloads_model.get_iter_first()
        has_completed = False
        iter_to_remove = None
        for row in self.downloads_model:
            if row[0].status == COMPLETED:
                has_completed = True

            if row[0] is download:
                iter_to_remove = downloads_iter

            downloads_iter = self.downloads_model.iter_next(downloads_iter)

        if iter_to_remove:
            self.downloads_model.remove(iter_to_remove)
            gui.queue_resize(self.downloads_treeview)

        self.clear_tool_button.props.sensitive = has_completed

    def __download_update(self, download, block_count, block_size, total_size):
        """Called on download updates. Finds the associated treeview row and
        fires a row changed signal."""
        self.update_download_row(download)

    def __download_status_changed(self, download, status):
        """Called when the status of a download changes. Tells the treeview to
        update the row with that download."""
        self.__downloads_treeview_selection_changed(self.downloads_treeview_selection)

        # Enable clear button if necessary
        if not self.clear_tool_button.props.sensitive and \
           status == COMPLETED:
            self.clear_tool_button.set_sensitive(True)

        self.update_download_row(download)

    def update_download_row(self, download):
        """Called on download updates. Finds the associated treeview row and
        fires a row changed signal."""
        downloads_iter = self.downloads_model.get_iter_first()
        for row in self.downloads_model:
            if row[0] is download:
                downloads_path = self.downloads_model.get_path(downloads_iter)
                self.downloads_model.row_changed(downloads_path,
                        downloads_iter)
                break
            downloads_iter = self.downloads_model.iter_next(downloads_iter)

    def on_unhandled_exception(self, type, value, tb):
        """Called if an unhandled exception occurres. Shows the exception in
        an error dialog and prints the stack trace to stderr."""
        try:
            list = traceback.format_tb(tb, None) + \
                    traceback.format_exception_only(type, value)
            tracelog = '\nTraceback (most recent call last):\n' + "%-20s%s" % \
                    ("".join(list[:-1]), list[-1])

            message = "An internal program error has occurred."
            message += "\n" + tracelog

            gtk.gdk.threads_enter()
            ed = ErrorDialog(_("Unhandled exception"), message)
            ed.run()
            ed.destroy()
            gtk.gdk.threads_leave()

            sys.stderr.write(message)
        except:
            traceback.print_exc()

# vim: set sw=4 et sts=4 tw=79 fo+=l:
