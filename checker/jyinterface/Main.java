package jyinterface;

import jyinterface.Download;
import jyinterface.JythonFactory;
import org.python.util.PythonInterpreter;

public class Main {
    
    Download et;
    
    /** Creates a new instance of Main */
    public Main() {
    }
    
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {

        JythonFactory jf = JythonFactory.getInstance();
        Download eType = (Download) jf.getJythonObject(
                               "jyinterface.Download", "download.py");
        System.out.println("URL: " + eType.complete_url("c:\test"));
        
    }
}