/*######################################################################
#
# Project: DLApplet
# URL: http://www.nabber.org/projects/
# E-mail: webmaster@nabber.org
#
# Copyright: (C) 2009, Neil McNab
# License: GNU General Public License Version 2
#   (http://www.gnu.org/copyleft/gpl.html)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# Filename: $URL$
# Last Updated: $Date$
# Author(s): Neil McNab
#
# Description:
#   GUI for table of downloads.
######################################################################*/

package jyinterface;

import java.util.*;
import javax.swing.*;
import javax.swing.table.*;

// This class manages the download table's data.
class DownloadsTableModel extends AbstractTableModel
        implements Observer {
    
    // These are the names for the table's columns.
    private static final String[] columnNames = {"File", "Size",
    "Progress", "Status"};
    
    // These are the classes for each column's values.
    private static final Class[] columnClasses = {String.class,
    String.class, JProgressBar.class, String.class};
    
    // The table's list of downloads.
    private ArrayList downloadList = new ArrayList();
    
    // Add a new download to the table.
    public void addDownload(Download download) {
        
        // Register to be notified when the download changes.
        download.addObserver(this);
        
        downloadList.add(download);
        
        // Fire table row insertion notification to table.
        fireTableRowsInserted(getRowCount() - 1, getRowCount() - 1);
    }
    
    // Get a download for the specified row.
    public Download getDownload(int row) {
        return (Download) downloadList.get(row);
    }
    
    // Remove a download from the list.
    public void clearDownload(int row) {
        downloadList.remove(row);
        
        // Fire table row deletion notification to table.
        fireTableRowsDeleted(row, row);
    }
    
    // Get table's column count.
    public int getColumnCount() {
        return columnNames.length;
    }
    
    // Get a column's name.
    public String getColumnName(int col) {
        return columnNames[col];
    }
    
    // Get a column's class.
    public Class getColumnClass(int col) {
        return columnClasses[col];
    }
    
    // Get table's row count.
    public int getRowCount() {
        return downloadList.size();
    }
    
    // Get value for a specific row and column combination.
    public Object getValueAt(int row, int col) {
        
        Download download = (Download) downloadList.get(row);
        switch (col) {
            case 0: // Filename
                return download.displayFileName();
            case 1: // Size
                int size = download.getSize();
                return (size == -1) ? "" : Integer.toString(size);
            case 2: // Progress
                return new Float(download.getProgress());
            case 3: // Status
                return Download.STATUSES[download.getStatus()];
        }
        return "";
    }
    
  /* Update is called when a Download notifies its
     observers of any changes */
    public void update(Observable o, Object arg) {
        int index = downloadList.indexOf(o);
        
        // Fire table row update notification to table.
        fireTableRowsUpdated(index, index);
    }
}