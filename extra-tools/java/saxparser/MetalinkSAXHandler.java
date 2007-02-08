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

import java.io.CharArrayWriter;

import javax.xml.parsers.SAXParser;

import org.xml.sax.Attributes;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

/**
 * 
 */
public class MetalinkSAXHandler extends DefaultHandler
{
	private CharArrayWriter text = new CharArrayWriter();
	private DMetalink dMetalink;
//    public enum ElementType { FILE, HASH}
  Attributes atr;
    
    /**
    	@param dMetalink The metalink data container
    */
    MetalinkSAXHandler( DMetalink dMetalink)
    {
        this.dMetalink = dMetalink;
    }
    
    public void startElement(
    		String uri,
    		String localName,
    		String qName,
        Attributes attributes) throws SAXException
    {
    	//Set current name and copy attributes
    	if(qName.equals("file"))
    	{
    		this.dMetalink.newFile(attributes.getValue("name"));
	   	}
			System.out.println(qName);
    	//copy attributes
    	this.atr = attributes;
    	
    }
    
    public void endElement(String uri, String localName, String qName) 
        throws SAXException
    {
    	if(qName.equals("hash"))
    	{
    		dMetalink.addHash(atr.getValue("type"), text.toString().trim());
    	}
    	if(qName.equals("url"))
    	{
    		dMetalink.addLink(text.toString().trim());//TODO, atr.getValue("type"));
    	}
    	text.reset();
    }
         
     public void characters(char[] ch, int start, int length)
     {
         text.write(ch,start,length );
     }
}
