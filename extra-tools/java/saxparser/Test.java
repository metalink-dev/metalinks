/*
	This file is part of the saxparser for Java from the Metalinks tools project
	Copyright (C) 2007  A. Bram Neijt <bneijt@gmail.com>

	This program is free software; you can redistribute it and/or
	modify it under the terms of the GNU General Public License
	as published by the Free Software Foundation; either version 2
	of the License, or (at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

*/

import java.io.*;

import org.xml.sax.*;
import org.xml.sax.helpers.DefaultHandler;

import javax.xml.parsers.SAXParserFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser;

public class Test
{
    public static void main(String argv[])
    {
    	 if (argv.length != 1) {
            System.err.println("Usage: cmd filename");
            System.exit(1);
        }
        
        // Use an instance of ourselves as the SAX event handler
        DMetalink d = new DMetalink();
        DefaultHandler handler = new MetalinkSAXHandler(d);
        // Use the default (non-validating) parser
        SAXParserFactory factory = SAXParserFactory.newInstance();
        try {
            // Parse the input
            SAXParser saxParser = factory.newSAXParser();
            saxParser.parse( new File(argv[0]), handler);
		        System.out.println(d.toString());
		        //Generate the Magnet link
						for(int i = 0; i < d.files.size(); ++i)
						{
							DMetalink.FileEntry f = (DMetalink.FileEntry) d.files.get(i);
							if(f.magnet() != null)
				        System.out.println(f.magnet());
			      }
			      
        } catch (Throwable t) {
            t.printStackTrace();
        }
        System.exit(0);
    }
}
