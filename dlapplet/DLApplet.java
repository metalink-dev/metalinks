//package org.nabber.DLApplet;

//import java.applet.Applet;
//import java.awt.Graphics;
//import java.awt.Color;
//import java.awt.Frame;
//import java.awt.Button;
//import java.awt.TextField;
//import java.awt.event.ActionEvent;
import javax.swing.JApplet;
import javax.swing.JFrame;

import java.io.*;
import java.net.URL;

public class DLApplet extends JApplet{

  //String text = "I'm a simple applet";
  //TextField filenameT;
  //TextField urlT;
  //Button downloadB;
  DownloadManager manager;

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
	  add(manager = new DownloadManager());
	  manager.set_url(getParameter("url"));
	  manager.set_path(getParameter("path"));
	  manager.setVisible(true);
	  
	  //DownloadManager f = new DownloadManager();
	  //f.setVisible(true);
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

