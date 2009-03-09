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
#   Master class to handle downloads.
######################################################################*/

import java.util.ArrayList;
import java.net.URL;
import java.io.File;

import javax.xml.parsers.*;
import org.xml.sax.*;
import org.xml.sax.helpers.*;

class Downloader extends Object {
    ArrayList <String> urls = new ArrayList <String> ();
	String path = "";
	ArrayList <Download> managers = new ArrayList <Download> ();

	public Downloader(URL url, String pathin) {
	    path = pathin;
	    if (url.toString().endsWith(".metalink")) {
		    System.out.println("processing as metalink");
		    download_metalink(url);
		} else {
		    System.out.println("processing as normal download");
			urls.add(url.toString());
	        download_file(url.toString().substring(url.toString().lastIndexOf('/')+1), urls);
		}
	}
	
	public void download_metalink(URL url) {		
		Metalink handler = new Metalink();
        SAXParserFactory factory = SAXParserFactory.newInstance();
        try {
          SAXParser parser = factory.newSAXParser();
          parser.parse(url.toString(), handler);
        } catch(Exception e) {
          String errorMessage =
            "Error parsing " + url.toString() + ": " + e;
          System.err.println(errorMessage);
          e.printStackTrace();
        }
		
		for (MetalinkFile fileobj : handler.get_files()) {
		    download_file(fileobj.get_filename(), fileobj.get_urls());
		}
	}
	
	public void download_file(String filename, ArrayList <String> dlurls) {
		//System.out.println("downloadfile: " + filename);
	    MetalinkFile ml = new MetalinkFile(filename);
		
		for (String url : dlurls) {
		    ml.add_url(url);
		}
		download_file_urls(ml);
	}
		
	public void download_file_urls(MetalinkFile ml) {
		//System.out.println("Downloading to: " + ml.get_filename());
		
		String fullpath = path + "/" + ml.filename;
		
		//create subdirectories if needed
		System.out.println("subdir: " + fullpath.substring(0, fullpath.lastIndexOf('/')));
		File dir = new File(fullpath.substring(0, fullpath.lastIndexOf('/')));
		if (!dir.exists()) {
		    dir.mkdirs();
		}
		
		boolean segmented = false;
		
		if (segmented) {
			//segment manager
		}
		if (!segmented) {
		    System.out.println("fullpath: " + fullpath);
			Download dl = new Download(ml, fullpath);
			managers.add(dl);
		}
	}
	
	public ArrayList <Download> get_managers() {
	    return managers;
	}

}