// package org.nabber.DLApplet;

import java.io.*;
import java.net.*;
import java.util.*;

import javax.xml.parsers.*;
import org.xml.sax.*;
import org.xml.sax.helpers.*;

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
    
    private URL url; // download URL
	private String download_path;
    private int size; // size of download in bytes
    private int downloaded; // number of bytes downloaded
    private int status; // current status of download
    
    // Constructor for Download.
    public Download(URL url, String path) {
        this.url = url;
		this.download_path = path;
        size = -1;
        downloaded = 0;
        status = DOWNLOADING;
        
        // Begin the download.
        type_check(url);
    }
	
	public void type_check(URL url) {
	    if (url.toString().endsWith(".metalink")) {
		    System.out.println("processing as metalink");
		    download_metalink(url);
		} else {
		    System.out.println("processing as normal download");
	        download();
		}
	}
	
	public void download_metalink(URL url) {
	    String buffer = "";
		String line = "";
		InputStream stream = null;
		BufferedReader reader = null;
	    /*try {
		    stream = url.openStream();
			
			reader = new BufferedReader(new InputStreamReader(stream));
			
			while ((line = reader.readLine()) != null) {
                buffer += line + "\n";
            }
		} catch (IOException ex) {
			ex.printStackTrace();
		}*/
		
		
		Metalink handler = new Metalink();
        SAXParserFactory factory = SAXParserFactory.newInstance();
        try {
		  //System.out.println("parsing");
          SAXParser parser = factory.newSAXParser();
          parser.parse(url.toString(), handler);
        } catch(Exception e) {
          String errorMessage =
            "Error parsing " + url.toString() + ": " + e;
          System.err.println(errorMessage);
          e.printStackTrace();
        }
		/*try {
		    stream.close();
		} catch (IOException ex) {
			ex.printStackTrace();
		}*/
		
		for (MetalinkFile fileobj : handler.get_files()) {
		    download_file(fileobj.get_filename(), fileobj.get_urls());
		}
	}
	
	public void download_file(String filename, ArrayList <String> urls) {
	    System.out.println("Downloading: " + filename);
	}
    
    // Get this download's URL.
    public String getUrl() {
        return url.toString();
    }
    
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
    
    // Get file name portion of URL.
    public String getFileName() {
        String fileName = url.getFile();
        return fileName.substring(fileName.lastIndexOf('/') + 1);
    }
    
    // Download file.
    public void run() {
        RandomAccessFile file = null;
        InputStream stream = null;
        
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
            file = new RandomAccessFile(download_path + "/" + getFileName(), "rw");
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
    }
    
    // Notify observers that this download's status has changed.
    private void stateChanged() {
        setChanged();
        notifyObservers();
    }
}