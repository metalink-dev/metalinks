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
#   Main class for GUI.
######################################################################*/

// FROM: http://www.java-tips.org/java-se-tips/javax.swing/how-to-create-a-download-manager-in-java.html

package jyinterface;

import java.awt.*;
import java.awt.event.*;
import java.net.*;
import java.util.*;
import javax.swing.*;
import javax.swing.event.*;

// The Download Manager.
public class DownloadManager extends Panel
        implements Observer {
    
    // Add download text field.
    private JTextField addTextField;
	private JTextField addPathField;
    
    // Download table's data model.
    private DownloadsTableModel tableModel;
    
    // Table listing downloads.
    private JTable table;
    
    // These are the buttons for managing the selected download.
    private JButton pauseButton, resumeButton;
    private JButton cancelButton, clearButton;
    
    // Currently selected download.
    private Download selectedDownload;
    
    // Flag for whether or not table selection is being cleared.
    private boolean clearing;
    
	public void window() {
	     // Set application title.
		JFrame window = new JFrame();
        window.setTitle("DLApplet");
		window.setSize(640, 480);
		
		        // Set up file menu.
				
        JMenuBar menuBar = new JMenuBar();
        JMenu fileMenu = new JMenu("File");
        fileMenu.setMnemonic(KeyEvent.VK_F);
        JMenuItem fileExitMenuItem = new JMenuItem("Exit",
                KeyEvent.VK_X);
        fileExitMenuItem.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                actionExit();
            }
        });
        fileMenu.add(fileExitMenuItem);
        menuBar.add(fileMenu);
        window.setJMenuBar(menuBar);
		
		//add content
		window.add(new DownloadManager());
		
        // Handle window closing events.
        window.addWindowListener(new WindowAdapter() {
            public void windowClosing(WindowEvent e) {
                actionExit();
            }
        });
        
		window.setVisible(true);
	}
	
    // Constructor for Download Manager.
    public DownloadManager() {
        // Set window size.
        //setSize(300, 400);
        
		//Setup rows
		JPanel PanelRows = new JPanel();
		PanelRows.setLayout(new BoxLayout(PanelRows, BoxLayout.Y_AXIS));
		//JPanel addPanel3 = new JPanel();
        JLabel label = new JLabel("DLApplet");
        PanelRows.add(label);
		

        // Set up add panel.
        JPanel addPanel = new JPanel();
        label = new JLabel("URL: ");
        addPanel.add(label);
        addTextField = new JTextField(30);
        addPanel.add(addTextField);
        JButton addButton = new JButton("Start Download!");
        addButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                actionAdd();
            }
        });
        addPanel.add(addButton);
		PanelRows.add(addPanel);
		
		// Set up save dir panel.
        JPanel addPanel2 = new JPanel();
        label = new JLabel("Save Path:");
        addPanel2.add(label);
        addPathField = new JTextField(30);
        addPanel2.add(addPathField);

        JButton addBrowseButton = new JButton("Browse...");
        addBrowseButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                actionBrowse();
            }
        });
		addPanel2.add(addBrowseButton);
		PanelRows.add(addPanel2);
        
        // Set up Downloads table.
        tableModel = new DownloadsTableModel();
        table = new JTable(tableModel);
        table.getSelectionModel().addListSelectionListener(new
                ListSelectionListener() {
            public void valueChanged(ListSelectionEvent e) {
                tableSelectionChanged();
            }
        });
        // Allow only one row at a time to be selected.
        table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        
        // Set up ProgressBar as renderer for progress column.
        ProgressRenderer renderer = new ProgressRenderer(0, 100);
        renderer.setStringPainted(true); // show progress text
        table.setDefaultRenderer(JProgressBar.class, renderer);
        
        // Set table's row height large enough to fit JProgressBar.
        table.setRowHeight(
                (int) renderer.getPreferredSize().getHeight());
        
        // Set up downloads panel.
        JPanel downloadsPanel = new JPanel();
        downloadsPanel.setBorder(
                BorderFactory.createTitledBorder("Downloads"));
        downloadsPanel.setLayout(new BorderLayout());
        downloadsPanel.add(new JScrollPane(table),
                BorderLayout.CENTER);
        
        // Set up buttons panel.
        JPanel buttonsPanel = new JPanel();
        pauseButton = new JButton("Pause");
        pauseButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                actionPause();
            }
        });
        pauseButton.setEnabled(false);
        buttonsPanel.add(pauseButton);
        resumeButton = new JButton("Resume");
        resumeButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                actionResume();
            }
        });
        resumeButton.setEnabled(false);
        buttonsPanel.add(resumeButton);
        cancelButton = new JButton("Cancel");
        cancelButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                actionCancel();
            }
        });
        cancelButton.setEnabled(false);
        buttonsPanel.add(cancelButton);
        clearButton = new JButton("Clear");
        clearButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                actionClear();
            }
        });
        clearButton.setEnabled(false);
        buttonsPanel.add(clearButton);
        
        // Add panels to display.
		/*
        getContentPane().setLayout(new BorderLayout());
        getContentPane().add(addPanel, BorderLayout.NORTH);
        getContentPane().add(downloadsPanel, BorderLayout.CENTER);
        getContentPane().add(buttonsPanel, BorderLayout.SOUTH); */
        setLayout(new BorderLayout());
        //add(addPanel, BorderLayout.NORTH);
		add(PanelRows, BorderLayout.NORTH);
        add(downloadsPanel, BorderLayout.CENTER);
        add(buttonsPanel, BorderLayout.SOUTH);
        
        //precompile jython interfaces
        JythonFactory jf = JythonFactory.getInstance();
        Downloader eType = (Downloader) jf.getJythonObject(
                               "jyinterface.Downloader", "JDownloader.py");
        Download fType = (Download) jf.getJythonObject(
                               "jyinterface.Download", "JDownload.py");
    }
    
    // Exit this program.
    private void actionExit() {
        System.exit(0);
    }
    
    // Add a new download.
    private void actionAdd() {
        URL verifiedUrl = verifyUrl(addTextField.getText());
		
		// TODO validate Path value here
        if (addPathField.getText() == "") {
            JOptionPane.showMessageDialog(this,
                    "Invalid Save Path", "Error",
                    JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (verifiedUrl != null) {
            JythonFactory jf = JythonFactory.getInstance();
            Downloader dldr = (Downloader) jf.getJythonObject(
                               "jyinterface.Downloader", "JDownloader.py");
            dldr.start(verifiedUrl.toString(), addPathField.getText());
		    //Downloader dldr = new Downloader(verifiedUrl, addPathField.getText());
			for (Download dl: dldr.get_managers()) {
                tableModel.addDownload(dl);
			}
            addTextField.setText(""); // reset add text field
        } else {
            JOptionPane.showMessageDialog(this,
                    "Invalid Download URL", "Error",
                    JOptionPane.ERROR_MESSAGE);
        }
    }
	
    // Browse for a directory to save to
    private void actionBrowse() {
        addPathField.getText();
		
		//Create a file chooser
        JFileChooser fc = new JFileChooser();
		// only allow directories, not files
		fc.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
		
		int returnVal = fc.showOpenDialog(this);
		if(returnVal == JFileChooser.APPROVE_OPTION) {
			addPathField.setText(fc.getSelectedFile().getPath());
		}
    }
    
    // Verify download URL.
    private URL verifyUrl(String url) {
        // Only allow HTTP URLs.
        if (!url.toLowerCase().startsWith("http://"))
            return null;
        
        // Verify format of URL.
        URL verifiedUrl = null;
        try {
            verifiedUrl = new URL(url);
        } catch (Exception e) {
            return null;
        }
        
        // Make sure URL specifies a file.
        if (verifiedUrl.getFile().length() < 2)
            return null;
        
        return verifiedUrl;
    }
    
    // Called when table row selection changes.
    private void tableSelectionChanged() {
    /* Unregister from receiving notifications
       from the last selected download. */
        if (selectedDownload != null)
            selectedDownload.deleteObserver(DownloadManager.this);
        
    /* If not in the middle of clearing a download,
       set the selected download and register to
       receive notifications from it. */
        if (!clearing) {
            selectedDownload =
                    tableModel.getDownload(table.getSelectedRow());
            selectedDownload.addObserver(DownloadManager.this);
            updateButtons();
        }
    }
    
    // Pause the selected download.
    private void actionPause() {
        selectedDownload.pause();
        updateButtons();
    }
    
    // Resume the selected download.
    private void actionResume() {
        selectedDownload.resume();
        updateButtons();
    }
    
    // Cancel the selected download.
    private void actionCancel() {
        selectedDownload.cancel();
        updateButtons();
    }
    
    // Clear the selected download.
    private void actionClear() {
        clearing = true;
        tableModel.clearDownload(table.getSelectedRow());
        clearing = false;
        selectedDownload = null;
        updateButtons();
    }
    
  /* Update each button's state based off of the
     currently selected download's status. */
    private void updateButtons() {
        if (selectedDownload != null) {
            int status = selectedDownload.getStatus();
            switch (status) {
                case Download.DOWNLOADING:
                    pauseButton.setEnabled(true);
                    resumeButton.setEnabled(false);
                    cancelButton.setEnabled(true);
                    clearButton.setEnabled(false);
                    break;
                case Download.PAUSED:
                    pauseButton.setEnabled(false);
                    resumeButton.setEnabled(true);
                    cancelButton.setEnabled(true);
                    clearButton.setEnabled(false);
                    break;
                case Download.ERROR:
                    pauseButton.setEnabled(false);
                    resumeButton.setEnabled(true);
                    cancelButton.setEnabled(false);
                    clearButton.setEnabled(true);
                    break;
                default: // COMPLETE or CANCELLED
                    pauseButton.setEnabled(false);
                    resumeButton.setEnabled(false);
                    cancelButton.setEnabled(false);
                    clearButton.setEnabled(true);
            }
        } else {
            // No download is selected in table.
            pauseButton.setEnabled(false);
            resumeButton.setEnabled(false);
            cancelButton.setEnabled(false);
            clearButton.setEnabled(false);
        }
    }
    
  /* Update is called when a Download notifies its
     observers of any changes. */
    public void update(Observable o, Object arg) {
        // Update buttons if the selected download has changed.
        if (selectedDownload != null && selectedDownload.equals(o))
            updateButtons();
    }
    
	public void set_url(String url) {
	    addTextField.setText(url);
	}

	public void set_path(String path) {
	    addPathField.setText(path);
	}
	
    // Run the Download Manager.
    public static void main(String[] args) {
	    //window();
        DownloadManager manager = new DownloadManager();
        manager.window();
		//manager.setVisible(true);
    }
}