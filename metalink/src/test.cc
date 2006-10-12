/*
The following code compiles and runs, but it doesn't have the right result.
All calls to the program end in an exit_groups(1) somewhere. Because of this
weir behaviour my boost installation is very probably broken.
*/
#include <iostream>
#include <fstream>
#include <string>
#include <boost/program_options.hpp>
#include <boost/filesystem/operations.hpp>
#include <boost/filesystem/convenience.hpp>


#include <sys/stat.h>	//mkdir(2)
#include <sys/types.h> //mkdir(2)

using namespace std;
namespace po = boost::program_options;

int main(int argc, char *argv[])
try
{

	
	po::variables_map variableMap;
	

	try{
	//Program argument handling
	string xslHelp("XSLT link to use (Default: )");
	po::options_description generalOptions("General options");
	generalOptions.add_options()
		("help,h", "Produce a help message")
		("notdtd", "Don't include doctype reference in the output")
		("noxsl", "Don't include XSLT reference in the output")
		("xsl", po::value<std::string>(), "adsf")
		("genxsl", "Create default xsl from memory (if non existent)")	
		("stdout,c", "Collect all links on the stdout")
		;

	po::options_description dcOptions("Dublin Core metadata");
	dcOptions.add_options()
		("source", po::value<std::string>(), "All files are also available at <arg>/filename")
		("publisher", po::value<std::string>(), "Information about the publisher")
		("description", po::value<std::string>(), "Short description of the file")
		("rights", po::value<std::string>(), "Information about rights held in and over the resource.")
		("format", po::value<std::string>(), "Format information, like MIME type (Try `file -i <file>`)")
		;

//		("", po::value<std::string>(), "")

	po::options_description digestOptions("Digest options");
	digestOptions.add_options()
		("nosha1", "Don't include the SHA1")
		("nosha512", "Don't include the SHA512")
		("nomd5", "Don't include the MD5")
		("noed2k", "Don't include the ED2K (eDonkey2000 hash)")
		("nognunet070", "Don't include the GNUnet 0.7.x")
		;

  po::options_description hiddenOptions("Hidden options");
  hiddenOptions.add_options()
    ("input-file", po::value< vector<string> >(), "Input file(s)")
    ;
    
  po::options_description helpOptions;
  helpOptions.add(generalOptions).add(dcOptions).add(digestOptions);

  
  po::options_description allOptions;
  allOptions.add(generalOptions).add(dcOptions).add(digestOptions).add(hiddenOptions);
  
	po::positional_options_description positional;
	positional.add("input-file", -1);
	/*
	po::store(
		po::parse_command_line(argc, argv, allOptions)
		,variableMap);

	po::store(
		po::command_line_parser(argc, argv)
		.options(allOptions)
		.positional(positional)
		.run()
		,variableMap);
		*/	
	po::notify(variableMap);
  exit(1);	
	if(variableMap.count("help"))
	{
		cout << "EHLP HELPELH OELEPD";
		return 0;
	}
	}
  catch(exception& e) {
  	cerr << "error: " << e.what() << endl;
  	return 1;
  }
  catch(...) {
  	cerr << "Exception of unknown type!" << endl;
		throw;
  }

		
	return 0;
}
catch(const std::exception &e)
{
	cerr << "Caught std::exception (" << typeid(e).name() << "): " << e.what() << endl;
}
