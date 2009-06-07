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
#   Main class for Java applet to download files.
######################################################################*/

package jyinterface;

import jyinterface.Download;
import jyinterface.JythonFactory;
import org.python.util.PythonInterpreter;

import javax.swing.JApplet;
import javax.swing.JFrame;

import java.io.*;
import java.net.URL;

public class DLApplet extends JApplet{

  //String text = "I'm a simple applet";
  //TextField filenameT;
  //TextField urlT;
  //Button downloadB;
  /*DownloadManager manager; */
  Download et;

  public void init() {
        //text = "I'm a simple applet";
        //setBackground(Color.cyan);
		
		//add(this.urlT = new TextField(getParameter("url"), 100));
		//add(this.urlT = new TextField(getParameter("filename"), 100));
		//add(Button downloadB = new Button("Download!"));
		/*add(urlT = new TextField(getParameter("url"), 100));
		add(filenameT = new TextField(getParameter("filename"), 100));
		add(downloadB = new Button("Download!"));
		
      downloadB.addActionListener(new java.awt.event.ActionListener() {
        public void actionPerformed(ActionEvent e) {
        downloadB_actionPerformed(e);
      }
      });*/
	  //setSize(300, 400);
      /*
	  add(manager = new DownloadManager());
	  manager.set_url(getParameter("url"));
	  manager.set_path(getParameter("path"));
	  manager.setVisible(true);*/
	  
	  //DownloadManager f = new DownloadManager();
	  //f.setVisible(true);
      
      System.out.println("URL: " + getParameter("url"));

      JythonFactory jf = JythonFactory.getInstance();
      Download eType = (Download) jf.getJythonObject(
                               "jyinterface.Download", "download.py");
      System.out.println("TEST: " + eType.complete_url("c:\test"));

  }

  /*
  void downloadB_actionPerformed(ActionEvent e) {
    //txtResults.setText("btnCancel selected!");
	System.out.println(urlT.getText());
	//Download mydownload = 
	//Download(new URL(urlT.getText()), filenameT.getText());
	//mydownload.download();
  }
  */
  public static void main (String [] args) {
      //DownloadManager();
      //return;
      JFrame f = new JFrame("DLApplet");

      DLApplet ex = new DLApplet();

      ex.init();
	  
	  //new DownloadManager();
	  
      //f.add("Center", ex);

      f.pack();
      //f.show();
	  f.setVisible(true);

  }

  public void start() {
        System.out.println("starting...");
		/*
		byte buffer[] = "test".getBytes();
		RandomAccessFile file = null;
		
		try {
			file = new RandomAccessFile("c:\\Users\\mcnab\\Desktop\\test.txt", "rw");
		} catch (FileNotFoundException ex) {
			ex.printStackTrace();
		}
		try {
			file.write(buffer);
		} catch (IOException ex) {
			ex.printStackTrace();
		}
		try {
			file.close();
		} catch (IOException ex) {
			ex.printStackTrace();
		}*/
	}
  public void stop() {
        System.out.println("stopping...");
  }
  public void destroy() {
        System.out.println("preparing to unload...");
  }
}