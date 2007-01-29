/*
 * Test program for the MetalinkSAXHandler
 *
 * Read a given Metalink XML file into memory.
 *
 *
 *
 *
 *
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
