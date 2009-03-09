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
#   Class to handle normal downloads.  Tries alternate URLs if failure.
######################################################################*/

// FROM: http://www.java-tips.org/java-se-tips/javax.swing/how-to-create-a-download-manager-in-java.html

import java.io.*;
import java.net.*;
import java.util.*;

// This class downloads a file from a URL.
class Download extends Observable implements Runnable {
    
    // Max size of download buffer.
    private static final int MAX_BUFFER_SIZE = 1024;
    
    // These are the status names.
    public static final String STATUSES[] = {"Downloading",
    "Paused", "Complete", "Cancelled", "Error"};
    
    // These are the status codes.
    public static final int DOWNLOADING = 0;
    public static final int PAUSED = 1;
    public static final int COMPLETE = 2;
    public static final int CANCELLED = 3;
    public static final int ERROR = 4;
    
    //private URL url; // download URL
	ArrayList <String> urls = new ArrayList <String> ();
	private String filename;
	private String path;
    private int size; // size of download in bytes
    private int downloaded; // number of bytes downloaded
    private int status; // current status of download
    
    // Constructor for Download.
    public Download(MetalinkFile ml, String pathin) {
		filename = ml.filename;
		path = pathin;
		urls = ml.get_urls();
        size = -1;
        downloaded = 0;
        status = DOWNLOADING;
        
        // Begin the download.
        download();
    }
	
	/*public void setUrl(URL url) {
		this.url = url;
	}*/
	
	/*public void setPath(String path) { 
		this.download_path = path;
	}*/
	
    // Get this download's URL.
    /*public String getUrl() {
        return url.toString();
    }*/
    
    // Get this download's size.
    public int getSize() {
        return size;
    }
    
    // Get this download's progress.
    public float getProgress() {
        return ((float) downloaded / size) * 100;
    }
    
    // Get this download's status.
    public int getStatus() {
        return status;
    }
    
    // Pause this download.
    public void pause() {
        status = PAUSED;
        stateChanged();
    }
    
    // Resume this download.
    public void resume() {
        status = DOWNLOADING;
        stateChanged();
        download();
    }
    
    // Cancel this download.
    public void cancel() {
        status = CANCELLED;
        stateChanged();
    }
    
    // Mark this download as having an error.
    private void error() {
        status = ERROR;
        stateChanged();
    }
    
    // Start or resume downloading.
    private void download() {
        Thread thread = new Thread(this);
        thread.start();
    }
    
	public String displayFileName() {
        return filename;
    }
	
    public String getFileName() {
        return path;// + "/" + filename;
    }
    
    // Download file.
    public void run() {
      RandomAccessFile file = null;
      InputStream stream = null;

	  URL url = null;

      for (String urlstr : urls) {
	    if (status == ERROR) {
	        status = DOWNLOADING;
		}
		System.out.println("trying url normally: " + urlstr);
		try {
	        url = new URL(urlstr);
		} catch (MalformedURLException e) {
		    e.printStackTrace();
		}
        try {
            // Open connection to URL.
            HttpURLConnection connection =
                    (HttpURLConnection) url.openConnection();
            
            // Specify what portion of file to download.
            connection.setRequestProperty("Range",
                    "bytes=" + downloaded + "-");
            
            // Connect to server.
            connection.connect();
            
            // Make sure response code is in the 200 range.
            if (connection.getResponseCode() / 100 != 2) {
                error();
            }
            
            // Check for valid content length.
            int contentLength = connection.getContentLength();
            if (contentLength < 1) {
                error();
            }
            
      /* Set the size for this download if it
         hasn't been already set. */
            if (size == -1) {
                size = contentLength;
                stateChanged();
            }
            
            // Open file and seek to the end of it.
            file = new RandomAccessFile(getFileName(), "rw");
			//file = new RandomAccessFile(getFileName(url), "rw");
            file.seek(downloaded);
            
            stream = connection.getInputStream();
            while (status == DOWNLOADING) {
        /* Size buffer according to how much of the
           file is left to download. */
                byte buffer[];
                if (size - downloaded > MAX_BUFFER_SIZE) {
                    buffer = new byte[MAX_BUFFER_SIZE];
                } else {
                    buffer = new byte[size - downloaded];
                }
                
                // Read from server into buffer.
                int read = stream.read(buffer);
                if (read == -1)
                    break;
                
                // Write buffer to file.
                file.write(buffer, 0, read);
                downloaded += read;
                stateChanged();
            }
            
      /* Change status to complete if this point was
         reached because downloading has finished. */
            if (status == DOWNLOADING) {
                status = COMPLETE;
                stateChanged();
            }
        } catch (Exception e) {
            error();
        } finally {
            // Close file.
            if (file != null) {
                try {
                    file.close();
                } catch (Exception e) {}
            }
            
            // Close connection to server.
            if (stream != null) {
                try {
                    stream.close();
                } catch (Exception e) {}
            }
        }
		if (status != ERROR) {
		    break;
		}
	  }
    }
    
    // Notify observers that this download's status has changed.
    private void stateChanged() {
        setChanged();
        notifyObservers();
    }
}