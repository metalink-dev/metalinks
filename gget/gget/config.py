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

import os
import os.path
import sys
from gettext import gettext as _

import gconf

#import dialogs
import gtk
import utils

DIR_GGET       = "/apps/gget"
DIR_GNOME      = "/desktop/gnome"
DIR_PROXY      = "/system/proxy"

KEY_SHOW_STATUSBAR     = "/general/show_statusbar"
KEY_SHOW_TOOLBAR       = "/general/show_toolbar"
KEY_SHOW_STATUS_ICON   = "/general/show_status_icon"
KEY_SHOW_MAIN_WINDOW   = "/general/show_main_window"
KEY_SHOW_NOTIFICATIONS = "/general/show_notifications"
KEY_SHOW_QUIT_DIALOG   = "/general/show_quit_dialog"
KEY_AUTOSTART          = "/general/autostart"
KEY_WINDOW_WIDTH       = "/general/window_width"
KEY_WINDOW_HEIGHT      = "/general/window_height"
KEY_WINDOW_POSITION_X  = "/general/window_position_x"
KEY_WINDOW_POSITION_Y  = "/general/window_position_y"
KEY_SHOW_STATUS        = "/general/show_status"
KEY_SHOW_CURRENT_SIZE  = "/general/show_current_size"
KEY_SHOW_TOTAL_SIZE    = "/general/show_total_size"
KEY_SHOW_PROGRESS      = "/general/show_progress"
KEY_SHOW_SPEED         = "/general/show_speed"
KEY_SHOW_ETA           = "/general/show_eta"

KEY_ASK_FOR_LOCATION  = "/folders/ask_for_location"
KEY_DEFAULT_FOLDER    = "/folders/default_folder"
KEY_CHECK_EXTENSIONS  = "/folders/check_extensions"
KEY_EXTENSIONS        = "/folders/extensions"
KEY_EXTENSION_FOLDERS = "/folders/extension_folders"

KEY_PROXY_MODE     = "/network/proxy_mode"
KEY_PROXY_HOST     = "/network/proxy_host"
KEY_PROXY_PORT     = "/network/proxy_port"
KEY_PROXY_AUTH     = "/network/proxy_auth"
KEY_PROXY_USER     = "/network/proxy_user"
KEY_PROXY_PASSWORD = "/network/proxy_password"

KEY_TOOLBAR_STYLE              = "/interface/toolbar_style"

KEY_SYSTEM_USE_HTTP_PROXY      = "/system/http_proxy/use_http_proxy"
KEY_SYSTEM_HTTP_PROXY_HOST     = "/system/http_proxy/host"
KEY_SYSTEM_HTTP_PROXY_PORT     = "/system/http_proxy/port"
KEY_SYSTEM_USE_HTTP_PROXY_AUTH = "/system/http_proxy/use_authentication"
KEY_SYSTEM_HTTP_PROXY_USER     = "/system/http_proxy/authentication_user"
KEY_SYSTEM_HTTP_PROXY_PASS     = "/system/http_proxy/authentication_password"
KEY_SYSTEM_PROXY_USE_SAME      = "/system/http_proxy/use_same_proxy"

KEY_SYSTEM_PROXY_HTTPS_HOST           = "/system/proxy/secure_host"
KEY_SYSTEM_PROXY_HTTPS_PORT           = "/system/proxy/secure_port"
KEY_SYSTEM_PROXY_FTP_HOST             = "/system/proxy/ftp_host"
KEY_SYSTEM_PROXY_FTP_PORT             = "/system/proxy/ftp_port"

FUNCTION_SUFFIXES = {KEY_SHOW_TOOLBAR:       'bool',
                     KEY_SHOW_STATUSBAR:     'bool',
                     KEY_SHOW_STATUS_ICON:   'bool',
                     KEY_SHOW_MAIN_WINDOW:   'bool',
                     KEY_SHOW_NOTIFICATIONS: 'bool',
                     KEY_SHOW_QUIT_DIALOG:   'bool',
                     KEY_AUTOSTART:          'bool',
                     KEY_WINDOW_WIDTH:       'int',
                     KEY_WINDOW_HEIGHT:      'int',
                     KEY_WINDOW_POSITION_X:  'int',
                     KEY_WINDOW_POSITION_Y:  'int',
                     KEY_SHOW_STATUS:        'bool',
                     KEY_SHOW_CURRENT_SIZE:  'bool',
                     KEY_SHOW_TOTAL_SIZE:    'bool',
                     KEY_SHOW_PROGRESS:      'bool',
                     KEY_SHOW_SPEED:         'bool',
                     KEY_SHOW_ETA:           'bool',

                     KEY_ASK_FOR_LOCATION:  'bool',
                     KEY_DEFAULT_FOLDER:    'string',
                     KEY_CHECK_EXTENSIONS:  'bool',
                     KEY_EXTENSIONS:        'list',
                     KEY_EXTENSION_FOLDERS: 'list',

                     KEY_PROXY_MODE:     'string',
                     KEY_PROXY_HOST:     'string',
                     KEY_PROXY_PORT:     'int',
                     KEY_PROXY_AUTH:     'bool',
                     KEY_PROXY_USER:     'string',
                     KEY_PROXY_PASSWORD: 'string',

                     KEY_TOOLBAR_STYLE: 'string',

                     KEY_SYSTEM_USE_HTTP_PROXY:      'bool',
                     KEY_SYSTEM_HTTP_PROXY_HOST:     'string',
                     KEY_SYSTEM_HTTP_PROXY_PORT:     'int',
                     KEY_SYSTEM_USE_HTTP_PROXY_AUTH: 'bool',
                     KEY_SYSTEM_HTTP_PROXY_USER:     'string',
                     KEY_SYSTEM_HTTP_PROXY_PASS:     'string',
                     KEY_SYSTEM_PROXY_USE_SAME:      'bool',

                     KEY_SYSTEM_PROXY_HTTPS_HOST: 'string',
                     KEY_SYSTEM_PROXY_HTTPS_PORT: 'int',
                     KEY_SYSTEM_PROXY_FTP_HOST:   'string',
                     KEY_SYSTEM_PROXY_FTP_PORT:   'int'
                     }

XDG_CONFIG_DIR = os.getenv("XDG_CONFIG_HOME") or "~/.config"

class Configuration(object):
    """Singleton representing the configuration"""

    instance = None

    def __new__(type, *args):
        if Configuration.instance is None:
            Configuration.instance = object.__new__(type)
            Configuration.instance.__init(*args)
        return Configuration.instance

    def __init(self, *args):
        self.debug = args[0] or os.getenv("GGET_DEBUG")
        self.base_dir = os.path.expanduser(os.path.join(XDG_CONFIG_DIR,
            "gget"))
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

        self.client = gconf.client_get_default()
        if self.client.dir_exists(DIR_GGET):
            self.client.add_dir(DIR_GGET, gconf.CLIENT_PRELOAD_RECURSIVE)
        else:
            if utils.runned_from_source():
                os.system("gconftool-2 --install-schema-file %s" %
                        os.path.join(utils.get_data_dir(), "gget.schemas"))
            else:
                ed = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK, message_format=_("Could not find configuration directory in GConf"))
                ed.format_secondary_text(_("Please make sure that gget.schemas was correctly installed."))
                ed.set_title(_("Error"))
                #ed = dialogs.ErrorDialog(_("Could not find configuration directory in GConf"), _("Please make sure that gget.schemas was correctly installed."))
                ed.run()
                sys.exit(1)

    def add_notify(self, key, callback, dir=DIR_GGET):
        self.client.notify_add(dir + key, callback)

    def __get_option(self, option, dir=DIR_GGET, type=None):
        if self.debug:
            print '[GConf get]: %s%s' % (dir, option)
        if type:
            return getattr(self.client, 'get_' +
                           FUNCTION_SUFFIXES[option])(dir + option, type)
        else:
            return getattr(self.client, 'get_' +
                           FUNCTION_SUFFIXES[option])(dir + option)

    def __set_option(self, option, value, dir=DIR_GGET, type=None):
        if self.debug:
            print '[GConf set]: %s%s=%s' % (dir, option, str(value))
        if type:
            getattr(self.client, 'set_' +
                    FUNCTION_SUFFIXES[option])(dir + option, type, value)
        else:
            getattr(self.client, 'set_' +
                    FUNCTION_SUFFIXES[option])(DIR_GGET + option, value)

    # Show Statusbar
    def get_show_statusbar(self):
        return self.__get_option(KEY_SHOW_STATUSBAR)

    def set_show_statusbar(self, show_statusbar):
        self.__set_option(KEY_SHOW_STATUSBAR, show_statusbar)

    show_statusbar = property(get_show_statusbar, set_show_statusbar)

    # Show Toolbar
    def get_show_toolbar(self):
        return self.__get_option(KEY_SHOW_TOOLBAR)

    def set_show_toolbar(self, show_toolbar):
        self.__set_option(KEY_SHOW_TOOLBAR, show_toolbar)

    show_toolbar = property(get_show_toolbar, set_show_toolbar)

    # Show Status icon
    def get_show_status_icon(self):
        return self.__get_option(KEY_SHOW_STATUS_ICON)

    def set_show_status_icon(self, show_status_icon):
        self.__set_option(KEY_SHOW_STATUS_ICON, show_status_icon)

    show_status_icon = property(get_show_status_icon, set_show_status_icon)

    # Show Main window
    def get_show_main_window(self):
        return self.__get_option(KEY_SHOW_MAIN_WINDOW)

    def set_show_main_window(self, show_main_window):
        self.__set_option(KEY_SHOW_MAIN_WINDOW, show_main_window)

    show_main_window = property(get_show_main_window, set_show_main_window)

    # Show Notifications
    def get_show_notifications(self):
        return self.__get_option(KEY_SHOW_NOTIFICATIONS)

    def set_show_notifications(self, show_notifications):
        self.__set_option(KEY_SHOW_NOTIFICATIONS, show_notifications)

    show_notifications = property(get_show_notifications,
            set_show_notifications)

    # Show Quit dialog
    def get_show_quit_dialog(self):
        return self.__get_option(KEY_SHOW_QUIT_DIALOG)

    def set_show_quit_dialog(self, show_quit_dialog):
        self.__set_option(KEY_SHOW_QUIT_DIALOG, show_quit_dialog)

    show_quit_dialog = property(get_show_quit_dialog, set_show_quit_dialog)

    # Autostart
    def get_autostart(self):
        return self.__get_option(KEY_AUTOSTART)

    def set_autostart(self, autostart):
        self.__set_option(KEY_AUTOSTART, autostart)

    autostart = property(get_autostart, set_autostart)

    # Window width
    def get_window_width(self):
        return self.__get_option(KEY_WINDOW_WIDTH)

    def set_window_width(self, window_width):
        self.__set_option(KEY_WINDOW_WIDTH, window_width)

    window_width = property(get_window_width, set_window_width)

    # Window height
    def get_window_height(self):
        return self.__get_option(KEY_WINDOW_HEIGHT)

    def set_window_height(self, window_height):
        self.__set_option(KEY_WINDOW_HEIGHT, window_height)

    window_height = property(get_window_height, set_window_height)

    # Window position x
    def get_window_position_x(self):
        return self.__get_option(KEY_WINDOW_POSITION_X)

    def set_window_position_x(self, window_position_x):
        self.__set_option(KEY_WINDOW_POSITION_X, window_position_x)

    window_position_x = property(get_window_position_x, set_window_position_x)

    # Window position y
    def get_window_position_y(self):
        return self.__get_option(KEY_WINDOW_POSITION_Y)

    # Show status
    def get_show_status(self):
        return self.__get_option(KEY_SHOW_STATUS)

    def set_show_status(self, show_status):
        self.__set_option(KEY_SHOW_STATUS, show_status)

    show_status = property(get_show_status, set_show_status)

    # Show current size
    def get_show_current_size(self):
        return self.__get_option(KEY_SHOW_CURRENT_SIZE)

    def set_show_current_size(self, show_current_size):
        self.__set_option(KEY_SHOW_CURRENT_SIZE, show_current_size)

    show_current_size = property(get_show_current_size, set_show_current_size)

    # Show total size
    def get_show_total_size(self):
        return self.__get_option(KEY_SHOW_TOTAL_SIZE)

    def set_show_total_size(self, show_total_size):
        self.__set_option(KEY_SHOW_TOTAL_SIZE, show_total_size)

    show_total_size = property(get_show_total_size, set_show_total_size)

    # Show progress
    def get_show_progress(self):
        return self.__get_option(KEY_SHOW_PROGRESS)

    def set_show_progress(self, show_progress):
        self.__set_option(KEY_SHOW_PROGRESS, show_progress)

    show_progress = property(get_show_progress, set_show_progress)

    # Show speed
    def get_show_speed(self):
        return self.__get_option(KEY_SHOW_SPEED)

    def set_show_speed(self, show_speed):
        self.__set_option(KEY_SHOW_SPEED, show_speed)

    show_speed = property(get_show_speed, set_show_speed)

    # Show eta
    def get_show_eta(self):
        return self.__get_option(KEY_SHOW_ETA)

    def set_show_eta(self, show_eta):
        self.__set_option(KEY_SHOW_ETA, show_eta)

    show_eta = property(get_show_eta, set_show_eta)

    def set_window_position_y(self, window_position_y):
        self.__set_option(KEY_WINDOW_POSITION_Y, window_position_y)

    window_position_y = property(get_window_position_y, set_window_position_y)

    # Ask for location
    def get_ask_for_location(self):
        return self.__get_option(KEY_ASK_FOR_LOCATION)

    def set_ask_for_location(self, ask_for_location):
        self.__set_option(KEY_ASK_FOR_LOCATION, ask_for_location)

    ask_for_location = property(get_ask_for_location, set_ask_for_location)

    # Default folder
    def get_default_folder(self):
        return self.__get_option(KEY_DEFAULT_FOLDER)

    def set_default_folder(self, default_folder):
        self.__set_option(KEY_DEFAULT_FOLDER, default_folder)

    default_folder = property(get_default_folder, set_default_folder)

    # Check extensions
    def get_check_extensions(self):
        return self.__get_option(KEY_CHECK_EXTENSIONS)

    def set_check_extensions(self, check_extensions):
        self.__set_option(KEY_CHECK_EXTENSIONS, check_extensions)

    check_extensions = property(get_check_extensions, set_check_extensions)

    # Extensions
    def get_extensions(self):
        return self.__get_option(KEY_EXTENSIONS, type=gconf.VALUE_STRING)

    def set_extensions(self, extensions):
        self.__set_option(KEY_EXTENSIONS, extensions, type=gconf.VALUE_STRING)

    extensions = property(get_extensions, set_extensions)

    # Extension folders
    def get_extension_folders(self):
        return self.__get_option(KEY_EXTENSION_FOLDERS, type=gconf.VALUE_STRING)

    def set_extension_folders(self, extension_folders):
        self.__set_option(KEY_EXTENSION_FOLDERS, extension_folders,
                type=gconf.VALUE_STRING)

    extension_folders = property(get_extension_folders, set_extension_folders)

    # Proxy mode
    def get_proxy_mode(self):
        return self.__get_option(KEY_PROXY_MODE)

    def set_proxy_mode(self, proxy_mode):
        self.__set_option(KEY_PROXY_MODE, proxy_mode)

    proxy_mode = property(get_proxy_mode, set_proxy_mode)

    # Proxy host
    def get_proxy_host(self):
        return self.__get_option(KEY_PROXY_HOST)

    def set_proxy_host(self, proxy_host):
        self.__set_option(KEY_PROXY_HOST, proxy_host)

    proxy_host = property(get_proxy_host, set_proxy_host)

    # Proxy port
    def get_proxy_port(self):
        return self.__get_option(KEY_PROXY_PORT)

    def set_proxy_port(self, proxy_port):
        self.__set_option(KEY_PROXY_PORT, proxy_port)

    proxy_port = property(get_proxy_port, set_proxy_port)

    # Proxy auth
    def get_proxy_auth(self):
        return self.__get_option(KEY_PROXY_AUTH)

    def set_proxy_auth(self, proxy_auth):
        self.__set_option(KEY_PROXY_AUTH, proxy_auth)

    proxy_auth = property(get_proxy_auth, set_proxy_auth)

    # Proxy user
    def get_proxy_user(self):
        return self.__get_option(KEY_PROXY_USER)

    def set_proxy_user(self, proxy_user):
        self.__set_option(KEY_PROXY_USER, proxy_user)

    proxy_user = property(get_proxy_user, set_proxy_user)

    # Proxy password
    def get_proxy_password(self):
        return self.__get_option(KEY_PROXY_PASSWORD)

    def set_proxy_password(self, proxy_password):
        self.__set_option(KEY_PROXY_PASSWORD, proxy_password)

    proxy_password = property(get_proxy_password, set_proxy_password)

    # Toolbar style
    def get_toolbar_style(self):
        return self.__get_option(KEY_TOOLBAR_STYLE)

    def set_toolbar_style(self, toolbar_style):
        self.__set_option(KEY_TOOLBAR_STYLE, toolbar_style)

    toolbar_style = property(get_toolbar_style, set_toolbar_style)

    # Use HTTP proxy
    def get_use_http_proxy(self):
        return self.__get_option(KEY_SYSTEM_USE_HTTP_PROXY)

    def set_use_http_proxy(self, use_http_proxy):
        self.__set_option(KEY_SYSTEM_USE_HTTP_PROXY, use_http_proxy)

    use_http_proxy = property(get_use_http_proxy, set_use_http_proxy)

    # HTTP proxy host
    def get_http_proxy_host(self):
        return self.__get_option(KEY_SYSTEM_HTTP_PROXY_HOST)

    def set_http_proxy_host(self, http_proxy_host):
        self.__set_option(KEY_SYSTEM_HTTP_PROXY_HOST, http_proxy_host)

    http_proxy_host = property(get_http_proxy_host, set_http_proxy_host)

    # HTTP proxy port
    def get_http_proxy_port(self):
        return self.__get_option(KEY_SYSTEM_HTTP_PROXY_PORT)

    def set_http_proxy_port(self, http_proxy_port):
        self.__set_option(KEY_SYSTEM_HTTP_PROXY_PORT, http_proxy_port)

    http_proxy_port = property(get_http_proxy_port, set_http_proxy_port)

    # Use HTTP proxy auth
    def get_use_http_proxy_auth(self):
        return self.__get_option(KEY_SYSTEM_USE_HTTP_PROXY_AUTH)

    def set_use_http_proxy_auth(self, use_http_proxy_auth):
        self.__set_option(KEY_SYSTEM_USE_HTTP_PROXY_AUTH, use_http_proxy_auth)

    use_http_proxy_auth = property(get_use_http_proxy_auth,
            set_use_http_proxy_auth)

    # HTTP proxy user
    def get_http_proxy_user(self):
        return self.__get_option(KEY_SYSTEM_HTTP_PROXY_USER)

    def set_http_proxy_user(self, http_proxy_user):
        self.__set_option(KEY_SYSTEM_HTTP_PROXY_USER, http_proxy_user)

    http_proxy_user = property(get_http_proxy_user, set_http_proxy_user)

    # HTTP proxy pass
    def get_http_proxy_pass(self):
        return self.__get_option(KEY_SYSTEM_HTTP_PROXY_PASS)

    def set_http_proxy_pass(self, http_proxy_pass):
        self.__set_option(KEY_SYSTEM_HTTP_PROXY_PASS, http_proxy_pass)

    http_proxy_pass = property(get_http_proxy_pass, set_http_proxy_pass)

    # Proxy use same
    def get_proxy_use_same(self):
        return self.__get_option(KEY_SYSTEM_PROXY_USE_SAME)

    def set_proxy_use_same(self, proxy_use_same):
        self.__set_option(KEY_SYSTEM_PROXY_USE_SAME, proxy_use_same)

    use_same_proxy = property(get_proxy_use_same, set_proxy_use_same)

    # Proxy HTTPS host
    def get_proxy_https_host(self):
        return self.__get_option(KEY_SYSTEM_PROXY_HTTPS_HOST)

    def set_proxy_https_host(self, proxy_https_host):
        self.__set_option(KEY_SYSTEM_PROXY_HTTPS_HOST, proxy_https_host)

    proxy_https_host = property(get_proxy_https_host, set_proxy_https_host)

    # Proxy HTTPS port
    def get_proxy_https_port(self):
        return self.__get_option(KEY_SYSTEM_PROXY_HTTPS_PORT)

    def set_proxy_https_port(self, proxy_https_port):
        self.__set_option(KEY_SYSTEM_PROXY_HTTPS_PORT, proxy_https_port)

    proxy_https_port = property(get_proxy_https_port, set_proxy_https_port)

    # Proxy FTP host
    def get_proxy_ftp_host(self):
        return self.__get_option(KEY_SYSTEM_PROXY_FTP_HOST)

    def set_proxy_ftp_host(self, proxy_ftp_host):
        self.__set_option(KEY_SYSTEM_PROXY_FTP_HOST, proxy_ftp_host)

    proxy_ftp_host = property(get_proxy_ftp_host, set_proxy_ftp_host)

    # Proxy FTP port
    def get_proxy_ftp_port(self):
        return self.__get_option(KEY_SYSTEM_PROXY_FTP_PORT)

    def set_proxy_ftp_port(self, proxy_ftp_port):
        self.__set_option(KEY_SYSTEM_PROXY_FTP_PORT, proxy_ftp_port)

    proxy_ftp_port = property(get_proxy_ftp_port, set_proxy_ftp_port)

# vim: set sw=4 et sts=4 tw=79 fo+=l:
