

/*

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
