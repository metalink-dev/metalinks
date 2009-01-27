#!/usr/bin/python
#
#    Copyright (c) 2007 Hampus Wessman, Sweden.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import wxversion
wxversion.ensureMinimal("2.6")
import wx, metalink, sys, os.path

current_version = "1.2.0"

use_chunks_default = True
max_chunks_default = 100
chunk_size_default = 256

# Just a simple hack... (used to locate the icon)
try:
    data_path = os.path.dirname(sys.argv[0])
    if data_path != "" and data_path != ".":
        print "Data path:", data_path
except:
    data_path = ""

class SettingsDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title)
        # Init some values
        config = wx.ConfigBase.Get()
        config.SetPath("/Scanning")
        use_chunks = config.ReadBool("use_chunk_checksums", use_chunks_default)
        max_chunks = config.ReadInt("max_chunk_checksums", max_chunks_default)
        size_chunks = config.ReadInt("min_chunk_size", chunk_size_default)
        
        # Create controls
        txt_chunks = wx.StaticText(self, -1, "Use chunk checksums?")
        self.checkbox_chunks = wx.CheckBox(self, -1, "Enable")
        self.checkbox_chunks.SetValue(use_chunks)
        txt_maxchunks = wx.StaticText(self, -1, "Maximum number of chunks:")
        self.txtctrl_maxchunks = wx.SpinCtrl(self, -1, min=2, max=10000)
        self.txtctrl_maxchunks.SetValue(max_chunks)
        txt_chunksize = wx.StaticText(self, -1, "Minimum chunk size (KiB):")
        self.txtctrl_chunksize = wx.SpinCtrl(self, -1, min=1, max=10240)
        self.txtctrl_chunksize.SetValue(size_chunks)
        # Sizers
        vbox =  wx.BoxSizer(wx.VERTICAL)
        
        flex_sizer = wx.FlexGridSizer(0, 2)
        flex_sizer.AddGrowableCol(1)
        flex_sizer.Add(txt_chunks, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        flex_sizer.Add(self.checkbox_chunks, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        flex_sizer.Add(txt_maxchunks, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        flex_sizer.Add(self.txtctrl_maxchunks, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        flex_sizer.Add(txt_chunksize, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        flex_sizer.Add(self.txtctrl_chunksize, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        
        sizer =  self.CreateButtonSizer(wx.OK|wx.CANCEL)
        chunk_staticbox = wx.StaticBoxSizer(wx.StaticBox(self, -1, "Scan settings"), wx.VERTICAL)
        chunk_staticbox.Add(flex_sizer, 1, wx.ALL | wx.EXPAND, 2)
        
        vbox.Add(chunk_staticbox, 0, wx.ALL | wx.EXPAND, 5)
        vbox.Add(sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        self.SetSizer(vbox)
        vbox.SetSizeHints(self)
        self.SetSize(wx.Size(300,-1))
        
        # Binding events
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        
    def  OnOK(self, evt):
        # Save data
        config = wx.ConfigBase.Get()
        config.SetPath("/Scanning")
        use_chunks = self.checkbox_chunks.GetValue()
        max_chunks = self.txtctrl_maxchunks.GetValue()
        size_chunks = self.txtctrl_chunksize.GetValue()
        config.WriteBool("use_chunk_checksums", use_chunks)
        config.WriteInt("max_chunk_checksums", max_chunks)
        config.WriteInt("min_chunk_size", size_chunks)
        # Close dialog
        if self.IsModal():
            self.EndModal(wx.ID_OK)
        else:
            self.SetReturnCode(wx.ID_OK)
            self.show(False)

# Main GUI frame
class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title)  
        self.create_gui()
        self.filename = ""
        self.new_file = True
        self.locked = False
        self.ml = metalink.Metalink()
        self.update()

    def create_gui(self):
        p = wx.Panel(self, -1)
        self.p = p
        
        if wx.GetOsDescription().find("Windows") == -1:
            print "Not on win32. Using png-file for icon."
            icon = wx.Icon(os.path.join(data_path, "metalink_small.png"), wx.BITMAP_TYPE_PNG)
        else:
            print "Running win32. Using ico-file."
            icon = wx.Icon(os.path.join(data_path, "metalink_small.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        # Release Information
        txt_identity = wx.StaticText(p, -1, "Release name:")
        self.txtctrl_identity = wx.TextCtrl(p, -1)
        txt_version = wx.StaticText(p, -1, "Version:")
        self.txtctrl_version = wx.TextCtrl(p, -1)
        txt_pub_name = wx.StaticText(p, -1, "Publisher name:")
        self.txtctrl_pub_name = wx.TextCtrl(p, -1)
        txt_copy = wx.StaticText(p, -1, "Copyright:")
        self.txtctrl_copy = wx.TextCtrl(p, -1)
        txt_url = wx.StaticText(p, -1, "Web site URL:")
        self.txtctrl_pub_url = wx.TextCtrl(p, -1)
        txt_desc = wx.StaticText(p, -1, "Description:")
        self.txtctrl_desc = wx.TextCtrl(p, -1)
        
        self.license = {'GNU GPL': 'http://www.gnu.org/licenses/gpl.html',
            'GNU LGPL':'http://www.gnu.org/licenses/lgpl.html',
            'GNU FDL':'http://www.gnu.org/licenses/fdl.html',
            'CC GNU GPL':'http://creativecommons.org/licenses/GPL/2.0/',
            'CC GNU LGPL':'http://creativecommons.org/licenses/LGPL/2.1/',
            'CC Public Domain':'http://creativecommons.org/licenses/publicdomain/',
            'CC Music Sharing':'http://creativecommons.org/licenses/by-nc-nd/2.0/deed-music',
            'CC Dev Nations':'http://creativecommons.org/licenses/devnations/2.0/',
            'CC by-nc-nd':'http://creativecommons.org/licenses/by-nc-nd/2.5/',
            'CC by-nc-sa':'http://creativecommons.org/licenses/by-nc-sa/3.0/',
            'CC by-nc':'http://creativecommons.org/licenses/by-nc/3.0/',
            'CC by-nd':'http://creativecommons.org/licenses/by-nd/2.5/',
            'CC by-sa':'http://creativecommons.org/licenses/by-sa/2.5/',
            'CC by':'http://creativecommons.org/licenses/by/2.5/',
            'CC Sampling':'http://creativecommons.org/licenses/sampling/1.0/',
            'CC Sampling+':'http://creativecommons.org/licenses/sampling+/1.0/',
            'CC nc-sampling+':'http://creativecommons.org/licenses/nc-sampling+/1.0/',
            'BSD':'http://opensource.org/licenses/bsd-license.php',
            'MIT':'http://opensource.org/licenses/mit-license.php',
            'MPL 1.0':'http://opensource.org/licenses/mozilla1.0.php',
            'MPL 1.1':'http://opensource.org/licenses/mozilla1.1.php',
            'AFL 3.0':'http://opensource.org/licenses/afl-3.0.php',
            'OSL 3.0': 'http://opensource.org/licenses/osl-3.0.php',
            'zlib/libpng':'http://opensource.org/licenses/zlib-license.php',
            'Artistic License':'http://opensource.org/licenses/artistic-license.php'
            }
        choices_license = ['Unknown', 'Commercial', 'Shareware', 'Public Domain',
            'GNU GPL', 'GNU LGPL', 'GNU FDL',
            'CC GNU GPL', 'CC GNU LGPL', 'CC Public Domain', 'CC Music Sharing', 'CC Dev Nations', 'CC by-nc-nd',
            'CC by-nc-sa', 'CC by-nc', 'CC by-nd', 'CC by-sa', 'CC by', 'CC Sampling', 'CC Sampling+', 'CC nc-sampling+',
            'BSD', 'MIT', 'MPL 1.0', 'MPL 1.1', 'AFL 3.0', 'OSL 3.0', 'zlib/libpng', 'Artistic License']
        txt_license_name = wx.StaticText(p, -1, "License name:")
        self.combo_license_name = wx.ComboBox(p, -1, 'Unknown', wx.DefaultPosition, wx.Size(150,-1), choices_license, wx.CB_DROPDOWN)
        txt_license_url = wx.StaticText(p, -1, "License URL:")
        self.txtctrl_license_url = wx.TextCtrl(p, -1)
        
        # Sizers Release Information
        rel_sizer = wx.FlexGridSizer(0, 2)
        rel_sizer.AddGrowableCol(1)
        rel_sizer.Add(txt_identity, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)

        rel_box = wx.BoxSizer(wx.HORIZONTAL)
        rel_box.Add(self.txtctrl_identity, 1, wx.ALL | wx.EXPAND, 2)
        rel_box.Add(txt_version, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 2)
        rel_box.Add(self.txtctrl_version, 0, wx.ALL, 2)
        rel_sizer.Add(rel_box, 1, wx.EXPAND)

        rel_sizer.Add(txt_pub_name, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        rel_sizer.Add(self.txtctrl_pub_name, 1, wx.ALL | wx.EXPAND, 2)
        rel_sizer.Add(txt_copy, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        rel_sizer.Add(self.txtctrl_copy, 1, wx.ALL | wx.EXPAND, 2)
        rel_sizer.Add(txt_url, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        rel_sizer.Add(self.txtctrl_pub_url, 1, wx.ALL | wx.EXPAND, 2)
        rel_sizer.Add(txt_desc, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        rel_sizer.Add(self.txtctrl_desc, 1, wx.ALL | wx.EXPAND, 2)
        rel_sizer.Add(txt_license_name, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        
        rel_box = wx.BoxSizer(wx.HORIZONTAL)
        rel_box.Add(self.combo_license_name, 0, wx.ALL, 2)
        rel_box.Add(txt_license_url, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 2)
        rel_box.Add(self.txtctrl_license_url, 1, wx.ALL | wx.EXPAND, 2)
        rel_sizer.Add(rel_box, 1, wx.EXPAND)

        rel_staticbox = wx.StaticBoxSizer(wx.StaticBox(p, -1, "Release Information (Recommended)"), wx.VERTICAL)
        rel_staticbox.Add(rel_sizer, 1, wx.ALL | wx.EXPAND, 2)

        # File Information
        txt_filename = wx.StaticText(p, -1, "File name:")
        self.txtctrl_filename = wx.TextCtrl(p, -1)
        txt_size = wx.StaticText(p, -1, "File size (bytes):")
        self.txtctrl_size = wx.TextCtrl(p, -1)
        txt_md5 = wx.StaticText(p, -1, "MD5 hash:")
        self.txtctrl_md5 = wx.TextCtrl(p, -1)
        txt_sha1 = wx.StaticText(p, -1, "SHA-1 hash:")
        self.txtctrl_sha1 = wx.TextCtrl(p, -1)
        txt_sha256 = wx.StaticText(p, -1, "SHA-256 hash:")
        self.txtctrl_sha256 = wx.TextCtrl(p, -1)
        txt_os = wx.StaticText(p, -1, "Platform:")
        choices_os = ['Unknown','Source', 'BSD-x86', 'BSD-x64', 'Linux-x86', 'Linux-x64', 'Linuxia64', 'Linux-alpha', 'Linux-arm', 'Linux-hppa', 'Linux-m68k', 'Linux-mips', 'Linux-mipsel', 'Linux-PPC', 'Linux-PPC64', 'Linux-s390', 'Linux-SPARC', 'MacOSX-PPC', 'MacOSX-Intel', 'MacOSX-UB', 'Solaris-SPARC', 'Solaris-x86', 'Windows-x86', 'Windows-x64', 'Windowsia64']
        self.combo_os = wx.ComboBox(p, -1, 'Unknown', wx.DefaultPosition, wx.Size(150,-1), choices_os, wx.CB_DROPDOWN)
        txt_lang = wx.StaticText(p, -1, "Language:")
        self.txtctrl_lang = wx.TextCtrl(p, -1, "", wx.DefaultPosition, wx.Size(50, -1))
        txt_maxconn_total = wx.StaticText(p, -1, "Max connections for this file:")
        choices_maxconn = ['-', '1', '2', '3', '4', '5', '10']
        self.combo_maxconn_total = wx.ComboBox(p, -1, '-', wx.DefaultPosition, wx.DefaultSize, choices_maxconn, wx.CB_DROPDOWN)
        
        self.btn_file_clear = wx.Button(p, -1, "Clear")
        self.btn_scan = wx.Button(p, -1, "Scan file...")

        # Sizers File Information
        file_sizer = wx.FlexGridSizer(0, 2)
        file_sizer.AddGrowableCol(1)
        file_sizer.Add(txt_filename, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)

        file_box = wx.BoxSizer(wx.HORIZONTAL)
        file_box.Add(self.txtctrl_filename, 1, wx.ALL | wx.EXPAND, 2)
        file_box.Add(txt_size, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 2)
        file_box.Add(self.txtctrl_size, 0, wx.ALL, 2)
        file_sizer.Add(file_box, 1, wx.EXPAND)

        file_sizer.Add(txt_md5, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        file_sizer.Add(self.txtctrl_md5, 0, wx.ALL | wx.EXPAND, 2)
        file_sizer.Add(txt_sha1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        file_sizer.Add(self.txtctrl_sha1, 0, wx.ALL | wx.EXPAND, 2)
        file_sizer.Add(txt_sha256, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        file_sizer.Add(self.txtctrl_sha256, 0, wx.ALL | wx.EXPAND, 2)

        file_sizer.Add(txt_os, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)

        file_box = wx.BoxSizer(wx.HORIZONTAL)
        file_box.Add(self.combo_os, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        file_box.Add(txt_lang, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
        file_box.Add(self.txtctrl_lang, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        file_box.Add(txt_maxconn_total, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
        file_box.Add(self.combo_maxconn_total, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        file_box.Add(wx.Size(0,0), 1)
        file_box.Add(self.btn_file_clear, 0, wx.RIGHT, 2)
        file_box.Add(self.btn_scan, 0)
        file_sizer.Add(file_box, 0, wx.ALL | wx.EXPAND, 2)

        file_staticbox = wx.StaticBoxSizer(wx.StaticBox(p, -1, "File Information (Recommended)"), wx.VERTICAL)
        file_staticbox.Add(file_sizer, 1, wx.ALL | wx.EXPAND, 2)

        # Resources
        self.filelist_columns = False
        self.filelist = wx.ListCtrl(p, -1, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT)
        self.init_filelist()
        txt_url = wx.StaticText(p, -1, "URL:")
        self.txtctrl_url = wx.TextCtrl(p, -1, "", wx.DefaultPosition, wx.Size(50, -1), wx.TE_PROCESS_ENTER)
        txt_loc = wx.StaticText(p, -1, "Location:")
        self.txtctrl_loc = wx.TextCtrl(p, -1, "", wx.DefaultPosition, wx.Size(50, -1), wx.TE_PROCESS_ENTER)
        txt_pref = wx.StaticText(p, -1, "Preference:")
        self.txtctrl_pref = wx.TextCtrl(p, -1, "", wx.DefaultPosition, wx.Size(50, -1), wx.TE_PROCESS_ENTER)
        txt_maxconn = wx.StaticText(p, -1, "Connections:")
        choices_maxconn = ['-', '1', '2', '3', '4', '5', '10']
        self.combo_maxconn = wx.ComboBox(p, -1, '-', wx.DefaultPosition, wx.DefaultSize, choices_maxconn, wx.CB_DROPDOWN)
        self.btn_add = wx.Button(p, -1, "Add")
        self.btn_change = wx.Button(p, -1, "Change")
        self.btn_remove = wx.Button(p, -1, "Remove")

        # Sizers Resources
        res_editbox = wx.BoxSizer(wx.HORIZONTAL)
        res_editbox.Add(txt_url, 0, wx.RIGHT | wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 2)
        res_editbox.Add(self.txtctrl_url, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        res_editbox.Add(txt_loc, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        res_editbox.Add(self.txtctrl_loc, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        res_editbox.Add(txt_pref, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        res_editbox.Add(self.txtctrl_pref, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        res_editbox.Add(txt_maxconn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        res_editbox.Add(self.combo_maxconn, 0, wx.LEFT | wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 2)

        res_btnbox = wx.BoxSizer(wx.HORIZONTAL)
        res_btnbox.Add(wx.Size(0,0), 1)
        res_btnbox.Add(self.btn_add, 0)
        res_btnbox.Add(self.btn_change, 0, wx.LEFT | wx.RIGHT, 2)
        res_btnbox.Add(self.btn_remove, 0)

        res_staticbox = wx.StaticBoxSizer(wx.StaticBox(p, -1, "List of URLs (Required)"), wx.VERTICAL)
        res_staticbox.Add(self.filelist, 1, wx.ALL | wx.EXPAND, 2)
        res_staticbox.Add(res_editbox, 0, wx.ALL | wx.EXPAND, 2)
        res_staticbox.Add(res_btnbox, 0, wx.ALL | wx.EXPAND, 2)
        
        # Menu
        file = wx.Menu()
        self.menu_new = file.Append(-1, "New", "Create a new metalink. All unsaved data will be lost!")
        self.menu_open = file.Append(-1, "Open...", "Open a metalink file.")
        self.menu_save = file.Append(-1, "Save", "Save current file.")
        self.menu_save_as = file.Append(-1, "Save as...", "Save with a new file name.")
        self.menu_exit = file.Append(-1, "Exit", "Close the editor. All unsaved data will be lost!")
        
        opt = wx.Menu()
        id_settings = wx.NewId()
        self.menu_settings = opt.Append(id_settings, "Settings...", "Change the settings. Controls how chunk checksums are generated.")
        #opt.Enable(id_settings, False)
        
        help = wx.Menu()
        self.menu_about = help.Append(-1, "About...", "Show info about the application.")
        
        menu = wx.MenuBar()
        menu.Append(file, "File")
        menu.Append(opt, "Options")
        menu.Append(help, "Help")
        self.SetMenuBar(menu)
        
        self.CreateStatusBar(2)
        self.GetStatusBar().SetStatusWidths([-1, 200])
        
        # Bind events
        self.Bind(wx.EVT_BUTTON, self.onBtnFileClear, self.btn_file_clear)
        self.Bind(wx.EVT_BUTTON, self.onBtnScan, self.btn_scan)
        self.Bind(wx.EVT_BUTTON, self.onAddURL, self.btn_add)
        self.Bind(wx.EVT_BUTTON, self.onBtnChange, self.btn_change)
        self.Bind(wx.EVT_BUTTON, self.onBtnRemove, self.btn_remove)
        self.Bind(wx.EVT_TEXT_ENTER, self.onAddURL, self.txtctrl_url)
        self.Bind(wx.EVT_TEXT_ENTER, self.onAddURL, self.txtctrl_loc)
        self.Bind(wx.EVT_TEXT_ENTER, self.onAddURL, self.txtctrl_pref)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onURLSelected, self.filelist)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onURLDeselect, self.filelist)
        self.Bind(wx.EVT_MENU, self.onMenuAbout, self.menu_about)
        self.Bind(wx.EVT_MENU, self.onMenuSettings, self.menu_settings)
        self.Bind(wx.EVT_MENU, self.onMenuNew, self.menu_new)
        self.Bind(wx.EVT_MENU, self.onMenuOpen, self.menu_open)
        self.Bind(wx.EVT_MENU, self.onMenuSave, self.menu_save)
        self.Bind(wx.EVT_MENU, self.onMenuSaveAs, self.menu_save_as)
        self.Bind(wx.EVT_MENU, self.onMenuExit, self.menu_exit)
        self.Bind(wx.EVT_COMBOBOX, self.onLicenseSelected, self.combo_license_name)

        # Frame
        topsizer = wx.BoxSizer(wx.VERTICAL)
        topsizer.Add(rel_staticbox, 0, wx.ALL | wx.EXPAND, 5)
        topsizer.Add(file_staticbox, 0, wx.RIGHT | wx.LEFT | wx.BOTTOM | wx.EXPAND, 5)
        topsizer.Add(res_staticbox, 1, wx.RIGHT | wx.LEFT | wx.BOTTOM | wx.EXPAND, 5)
        self.topsizer = topsizer
        p.SetSizer(topsizer)
        p.Layout()
        topsizer.SetSizeHints(self)
        self.SetSize(wx.Size(800, 700))
    
    def init_filelist(self):
        # Remove all items
        index = -1
        while True:
            index = self.filelist.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE);
            if index == -1: break
            self.filelist.DeleteItem(index)
        # Insert columns if needed
        if not self.filelist_columns:
            self.filelist.InsertColumn(0, "URL", wx.LIST_FORMAT_LEFT, 520)
            self.filelist.InsertColumn(1, "Location", wx.LIST_FORMAT_LEFT, -1)
            self.filelist.InsertColumn(2, "Preference", wx.LIST_FORMAT_LEFT, -1)
            self.filelist.InsertColumn(3, "Connections", wx.LIST_FORMAT_LEFT, -1)
            self.filelist_columns = True

    def clear_urlfields(self):
        self.txtctrl_url.Clear()
        self.txtctrl_loc.Clear()
        self.txtctrl_pref.Clear()
        self.combo_maxconn.SetValue("-")

    def update(self):
        # Update URL stuff
        num_items = self.filelist.GetItemCount()
        if num_items > 0: urls = True
        else: urls = False
        self.btn_change.Enable(urls)
        self.btn_remove.Enable(urls)
        # Update title
        filename = os.path.basename(self.filename)
        if filename == "": filename = "Untitled"
        self.SetTitle(filename + " - Metalink Editor version "+current_version)
        # Lock / Unlock checksum fields
        enabled = not self.locked
        self.txtctrl_filename.SetEditable(enabled)
        self.txtctrl_size.SetEditable(enabled)
        self.txtctrl_md5.SetEditable(enabled)
        self.txtctrl_sha1.SetEditable(enabled)
        self.txtctrl_sha256.SetEditable(enabled)
        # Status text
        if len(self.ml.pieces) > 0:
            self.SetStatusText(str(len(self.ml.pieces)) + " chunk checksums.", 1)
        else:
            self.SetStatusText("No chunk checksums.", 1)
    
    def onMenuAbout(self, evt):
        wx.MessageBox("Metalink Editor is an editor for metalink files (www.metalinker.org).\n\nThe application was programmed by Hampus Wessman.\nWeb site: http://hampus.vox.nu/metalink/\n\nAnthony Bryan has helped alot with ideas and comments. Thanks!", "About Metalink Editor", wx.ICON_INFORMATION)

    def onMenuSettings(self, evt):
        dlg = SettingsDialog(self, -1, "Change Settings")
        dlg.ShowModal()
        dlg.Destroy()
    
    def onMenuExit(self, evt):
        self.Destroy()
    
    def onLicenseSelected(self, evt):
        name = evt.GetString()
        if name in self.license.keys():
            url = self.license[name]
        else:
            url = ''
        self.txtctrl_license_url.SetValue(url)
    
    def onBtnScan(self, evt):
        filename = wx.FileSelector("Choose a file to scan")
        if filename != "":
            config = wx.ConfigBase.Get()
            config.SetPath("/Scanning")
            use_chunks = config.ReadBool("use_chunk_checksums", use_chunks_default)
            max_chunks = config.ReadInt("max_chunk_checksums", max_chunks_default)
            size_chunks = config.ReadInt("min_chunk_size", chunk_size_default)
            old_filename = self.ml.filename
            progressdlg = wx.ProgressDialog("Scanning file...", "Please wait while Metalink Editor scans the selected file. This can take some time for very large files.",
                100, self, wx.PD_AUTO_HIDE | wx.PD_APP_MODAL | wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_ESTIMATED_TIME)
            success = self.ml.scan_file(filename, use_chunks, max_chunks, size_chunks, progressdlg)
            progressdlg.Destroy()
            if not success: return
            self.txtctrl_size.SetValue(self.ml.size)
            self.txtctrl_filename.SetValue(self.ml.filename)
            self.txtctrl_md5.SetValue(self.ml.hash_md5)
            self.txtctrl_sha1.SetValue(self.ml.hash_sha1)
            self.txtctrl_sha256.SetValue(self.ml.hash_sha256)
            if self.ml.hash_sha256 == "":
                self.txtctrl_sha256.Enable(False) # No support for SHA-256
            # Update URLs
            num_urls = self.filelist.GetItemCount()
            new_filename = self.ml.filename
            if num_urls > 0 and new_filename != old_filename:
                answer = wx.MessageBox("Would you like to update your URLs, so that they use the new filename instead of the old?", "Update mirrors?", wx.ICON_QUESTION | wx.YES_NO, self)
                if answer == wx.YES:
                    print "\nUpdating mirrors with the new filename."
                    print "Changing", old_filename, "to", new_filename + "."
                    item = -1
                    while True:
                        item = self.filelist.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE)
                        if item == -1: break
                        url = self.filelist.GetItem(item, 0).GetText()

                        #if old_filename == "":
                        url = os.path.dirname(url) + "/" + new_filename
                        self.filelist.SetStringItem(item, 0, url)
                        #else:
                        #    pos = url.rfind(old_filename)
                        #    if pos != -1:
                        #        print "Updated", url
                        #        url = url[:pos] + new_filename
                        #        self.filelist.SetStringItem(item, 0, url)

            item = -1
            while True:
                item = self.filelist.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE)
                if item == -1: break
                url = self.filelist.GetItem(item, 0).GetText()
                if url.startswith("ed2k://"):
                    # remove ed2k links, they add themselves back in later
                    self.filelist.DeleteItem(item)
                                
            # add ed2k link to GUI for this file
            self.addurl(metalink.Resource(self.ml.ed2k))
            
            self.filename = filename + ".metalink"
            self.new_file = True
            self.locked = True
            self.update()

    def onAddURL(self, evt):
        if self.txtctrl_url.GetValue() != "":
            url = self.txtctrl_url.GetValue()
            loc = self.txtctrl_loc.GetValue()
            pref = self.txtctrl_pref.GetValue()
            conns = self.combo_maxconn.GetValue()
            self.addurl(metalink.Resource(url, "", loc, pref, conns))
            
    def addurl(self, res):
            if not res.validate():
                for e in res.errors:
                    answer = wx.MessageBox(e + " Add it anyway?", "Confirm", wx.ICON_ERROR | wx.OK | wx.CANCEL, self)
                    if answer != wx.OK: return
            num_items = self.filelist.GetItemCount()
            self.filelist.InsertStringItem(num_items, res.url)
            self.filelist.SetStringItem(num_items, 1, res.location)
            self.filelist.SetStringItem(num_items, 2, res.preference)
            self.filelist.SetStringItem(num_items, 3, res.conns)
            self.clear_urlfields()
            self.update()

    def onBtnChange(self, evt):
        if self.txtctrl_url.GetValue() != "":
            url = self.txtctrl_url.GetValue()
            loc = self.txtctrl_loc.GetValue()
            pref = self.txtctrl_pref.GetValue()
            conns = self.combo_maxconn.GetValue()
            res = metalink.Resource(url, "", loc, pref, conns)
            if not res.validate():
                for e in res.errors:
                    answer = wx.MessageBox(e + " Change it anyway?", "Confirm", wx.ICON_ERROR | wx.OK | wx.CANCEL, self)
                    if answer != wx.OK: return
            item = self.filelist.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED);
            self.filelist.SetStringItem(item, 0, res.url)
            self.filelist.SetStringItem(item, 1, res.location)
            self.filelist.SetStringItem(item, 2, res.preference)
            self.filelist.SetStringItem(item, 3, res.conns)
            self.clear_urlfields()

    def onBtnRemove(self, evt):
        index = -1
        while True:
            index = self.filelist.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED);
            if index == -1: break
            self.filelist.DeleteItem(index)

    def onURLSelected(self, evt):
        item = self.filelist.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED);
        url = self.filelist.GetItem(item, 0).GetText()
        loc = self.filelist.GetItem(item, 1).GetText()
        pref = self.filelist.GetItem(item, 2).GetText()
        conns = self.filelist.GetItem(item, 3).GetText()
        self.txtctrl_url.SetValue(url)
        self.txtctrl_loc.SetValue(loc)
        self.txtctrl_pref.SetValue(pref)
        self.combo_maxconn.SetValue(conns)

    def onURLDeselect(self, evt):
        self.clear_urlfields()
    
    def onMenuSave(self, evt):
        if self.filename == "" or self.new_file:
            if not self.save_browse():
                return
        if self.filename != "":
            self.save()
    
    def onMenuSaveAs(self, evt):
        if self.save_browse():
            self.save()
    
    def save_browse(self):
        if self.filename != "":
            default_path, default_name = os.path.split(self.filename)
        else:
            default_path, default_name = "", ""
        filename = wx.FileSelector("Save as...", default_path, default_name, ".metalink", "All files (*.*)|*.*|Metalink files (*.metalink)|*.metalink", wx.SAVE)
        if filename == "":
            return False
        else:
            if filename != self.filename:
                self.new_file = True
            self.filename = filename
            self.update()
            return True
    
    def save(self):
        # Generate the file
        self.ml.filename = self.txtctrl_filename.GetValue()
        self.ml.identity = self.txtctrl_identity.GetValue()
        self.ml.publisher_name = self.txtctrl_pub_name.GetValue()
        self.ml.publisher_url = self.txtctrl_pub_url.GetValue()
        self.ml.copyright = self.txtctrl_copy.GetValue()
        self.ml.description = self.txtctrl_desc.GetValue()
        self.ml.license_name = self.combo_license_name.GetValue()
        if self.ml.license_name == 'Unknown': self.ml.license_name = ""
        self.ml.license_url = self.txtctrl_license_url.GetValue()
        self.ml.size = self.txtctrl_size.GetValue()
        self.ml.version = self.txtctrl_version.GetValue()
        self.ml.os = self.combo_os.GetValue()
        if self.ml.os == 'Unknown': self.ml.os = ""
        self.ml.language = self.txtctrl_lang.GetValue()
        self.ml.maxconn_total = self.combo_maxconn_total.GetValue()
        self.ml.origin = ""
        self.ml.hash_md5 = self.txtctrl_md5.GetValue()
        self.ml.hash_sha1 = self.txtctrl_sha1.GetValue()
        self.ml.hash_sha256 = self.txtctrl_sha256.GetValue()
        self.ml.clear_res()
        item = -1
        while True:
            item = self.filelist.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_DONTCARE)
            if item == -1: break
            url = self.filelist.GetItem(item, 0).GetText()
            loc = self.filelist.GetItem(item, 1).GetText()
            pref = self.filelist.GetItem(item, 2).GetText()
            conns = self.filelist.GetItem(item, 3).GetText()
            res = metalink.Resource(url, "default", loc, pref, conns)
            if not res.validate():
                for e in res.errors:
                    answer = wx.MessageBox(e + " Continue anyway?", "Confirm", wx.ICON_ERROR | wx.OK | wx.CANCEL, self)
                    if answer != wx.OK: return
            self.ml.add_res(res)
        if not self.ml.validate():
            for e in self.ml.errors:
                answer = wx.MessageBox(e + " Continue anyway?", "Confirm", wx.ICON_ERROR | wx.OK | wx.CANCEL, self)
                if answer != wx.OK: return
            self.ml.errors = []
        try:
            text = self.ml.generate()
        except Exception, e:
            wx.MessageBox(str(e), "Error!", wx.ICON_ERROR)
            return
        outfilename = self.filename
        # Warn about overwrites
        if os.path.isfile(self.filename) and self.new_file:
            answer = wx.MessageBox("There already exists a file named "+os.path.basename(outfilename)+". Overwrite file?", "Confirm", wx.OK | wx.CANCEL | wx.ICON_QUESTION, self)
            if answer != wx.OK: return
        # Save the file
        try:
            fp = open(outfilename, "w")
        except IOError:
            wx.MessageBox("Could not open output file!", "Error!", wx.ICON_ERROR)
            return
        try:
            fp.write(text)
            fp.close()
        except IOError, e:
            wx.MessageBox(str(e), "Error!", wx.ICON_ERROR)
            return
        self.new_file = False
        #wx.MessageBox("Saved file as " + outfilename, "File saved!")
        print "\nSaved file as", outfilename
        self.SetStatusText("Saved file as " + outfilename)

    def onMenuOpen(self, evt):
        filename = wx.FileSelector("Choose metalink file to load", "", "", ".metalink", "All files (*.*)|*.*|Metalink files (*.metalink)|*.metalink", wx.OPEN)
        if filename != "":
            try:
                self.ml = metalink.Metalink()
                self.ml.load_file(filename)
            except Exception, e:
                wx.MessageBox(str(e), "Error!", wx.ICON_ERROR)
                return
            self.txtctrl_filename.SetValue(self.ml.filename)
            self.txtctrl_identity.SetValue(self.ml.identity)
            self.txtctrl_pub_name.SetValue(self.ml.publisher_name)
            self.txtctrl_pub_url.SetValue(self.ml.publisher_url)
            self.txtctrl_copy.SetValue(self.ml.copyright)
            self.txtctrl_desc.SetValue(self.ml.description)
            self.combo_license_name.SetValue(self.ml.license_name)
            self.txtctrl_license_url.SetValue(self.ml.license_url)
            self.txtctrl_size.SetValue(self.ml.size)
            self.txtctrl_version.SetValue(self.ml.version)
            self.combo_os.SetValue(self.ml.os)
            self.txtctrl_lang.SetValue(self.ml.language)
            self.combo_maxconn_total.SetValue(self.ml.maxconn_total)
            self.txtctrl_md5.SetValue(self.ml.hash_md5)
            self.txtctrl_sha1.SetValue(self.ml.hash_sha1)
            self.txtctrl_sha256.SetValue(self.ml.hash_sha256)
            self.txtctrl_url.Clear()
            self.txtctrl_loc.Clear()
            self.txtctrl_pref.Clear()
            self.init_filelist()
            for res in self.ml.resources:
                num_items = self.filelist.GetItemCount()
                self.filelist.InsertStringItem(num_items, res.url)
                self.filelist.SetStringItem(num_items, 1, res.location)
                self.filelist.SetStringItem(num_items, 2, res.preference)
                self.filelist.SetStringItem(num_items, 3, res.conns)
            if len(self.ml.pieces) > 0 or self.ml.hash_md5 != "" or self.ml.hash_sha1 != "" or self.ml.hash_sha256 != "":
                self.locked = True
            else:
                self.locked = False
            self.new_file = False
            self.filename = filename
            print "\nLoaded file:", filename
            self.update()

    def onMenuNew(self, evt):
        answer = wx.MessageBox("Any unsaved data will be lost! Are you sure you want to continue?", "Confirm", wx.OK | wx.CANCEL, self)
        if answer == wx.OK:
            self.ml = metalink.Metalink()
            self.txtctrl_filename.Clear()
            self.txtctrl_identity.Clear()
            self.txtctrl_version.Clear()
            self.txtctrl_pub_name.Clear()
            self.txtctrl_pub_url.Clear()
            self.txtctrl_copy.Clear()
            self.txtctrl_desc.Clear()
            self.combo_license_name.SetValue("Unknown")
            self.txtctrl_license_url.Clear()
            self.txtctrl_size.Clear()
            self.txtctrl_md5.Clear()
            self.txtctrl_sha1.Clear()
            self.txtctrl_sha256.Clear()
            self.combo_os.SetValue("Unknown")
            self.txtctrl_lang.Clear()
            self.combo_maxconn_total.SetValue("-")
            self.txtctrl_url.Clear()
            self.txtctrl_loc.Clear()
            self.txtctrl_pref.Clear()
            self.combo_maxconn.SetValue("-")
            self.init_filelist()
            self.filename = ""
            self.new_file = True
            self.locked = False
            self.update()
    
    def onBtnFileClear(self, evt):
        answer = wx.MessageBox("Information about checksums and file size will be lost. Continue?", "Confirm", wx.OK | wx.CANCEL, self)
        if answer == wx.OK:
            self.ml.pieces = []
            self.ml.hash_md5 = ""
            self.ml.hash_sha1 = ""
            self.ml.hash_sha256 = ""
            self.ml.sig = ""
            self.ml.size = ""
            #self.ml.filename = ""
            #self.txtctrl_filename.Clear()
            self.txtctrl_size.Clear()
            self.txtctrl_md5.Clear()
            self.txtctrl_sha1.Clear()
            self.txtctrl_sha256.Clear()
            self.locked = False
            self.update()

# Application class
class MainApp(wx.App):
    def OnInit(self):
        if wx.GetOsDescription().find("Windows") == -1:
            configname = ".metalink_editor"
            print "Not on win32. Using configuration file:", configname
        else:
            configname = "metalink_editor.ini"
            print "Running win32. Using configuration file:", configname
        config = wx.FileConfig("Metalink Editor", "Hampus Wessman", configname)
        wx.ConfigBase.Set(config)
        self.frame = MainFrame(None, "Metalink Editor")
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

if __name__ == '__main__':
    app = MainApp(0)
    app.MainLoop()
