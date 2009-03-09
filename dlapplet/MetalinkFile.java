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
#   Class to handle files according to the Metalink spec.
######################################################################*/
import java.util.ArrayList;
import org.xml.sax.Attributes;

public class MetalinkFile extends Object {
    ArrayList <String> urls = new ArrayList <String> ();
	String filename;
	public MetalinkFile(String filenamein) {
	    filename = filenamein;
	}
	
    public void add_url(String url) {
	    urls.add(url);
	}
	
	public String get_filename() {
	    return filename;
	}
	
	public ArrayList <String> get_urls() {
	    return urls;
	}
}