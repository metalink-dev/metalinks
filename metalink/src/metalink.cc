/*
	This file is part of the metalink program
	Copyright (C) 2005  A. Bram Neijt <bneijt@gmail.com>

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

/** \file The main program

	The main program creates the hashes, interprets the commandline, fills the bneijt::Globals class
	and then open reads and handles all files.
	
	Please note that not using virtual classes for the Hash interface is an optimization, because we don't need the virtual table. I'm still thinking about a nice way of handling this in a more readable fashion, but introducting pointers to functions doesn't make the code look better ;-)
	
	As the list of hashes used is still small, we'll just learn to live with it.
*/

#include <iostream>
#include <fstream>
#include <string>
#include <boost/program_options.hpp>
#include <boost/filesystem/operations.hpp>
#include <boost/filesystem/convenience.hpp>

#include "Metalink/Metalink.hh"
#include "Hash/HashMD4/HashMD4.hh"
#include "Hash/HashED2K/HashED2K.hh"
#include "Hash/HashGNUnet/HashGNUnet.hh"
#include "Hash/GCrypt/GCrypt.hh"
#include "Hash/HashSHA1/HashSHA1.hh"
#include "Hash/HashSHA512/HashSHA512.hh"

#include "Globals/Globals.hh"

#include "Misc/Preprocessor/Foreach.hh"

#include <sys/stat.h>	//mkdir(2)
#include <sys/types.h> //mkdir(2)

using namespace std;
using namespace bneijt;
namespace po = boost::program_options;

int main(int argc, char *argv[])
try
{
	
	po::variables_map variableMap;
	

	try{
	//Program argument handling
	string xslHelp("XSLT link to use (Default: " + Globals::xsl + ")");
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
		cout << Globals::programName << " - " << Globals::programDescription << "\n";
		cout << "Version " << Globals::version[0] << "." << Globals::version[1] << "." << Globals::version[2];
		cout << ", Copyright (C) 2005 A. Bram Neijt <bneijt@gmail.com>\n";
		cout << Globals::programName << " comes with ABSOLUTELY NO WARRANTY and is licensed under GPL version 2\n\n";
		cout << "Usage: " << Globals::programName << " [options] <input files>\n";
		cout << helpOptions << "\n";
		cout << "Example: Generate the stylesheet and seperate records for all files\n\t"
				 << Globals::programName << " --genxsl *\n";
		cout << "Example: Generate the stylesheet and an index of all files\n\t"
				 << Globals::programName << " --genxsl -c * > index.metalinks.xml\n";
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

	if(variableMap.count("genxsl") != 0)
	{
		boost::filesystem::path file(Globals::xsl, boost::filesystem::native);
		if(!boost::filesystem::exists( file ))
		{
			cerr << "Generating " << Globals::xsl << "\n";
			boost::filesystem::path path("xsl", boost::filesystem::native);
			if(!boost::filesystem::exists( path ))
			{
				if(mkdir("xsl", 0777) != 0)
					cerr << "Notice: Tried to generate 'xsl' directory, but was unable\n";
				else
					cerr << "Notice: Created 'xsl' directory\n";

			}
			
			ofstream mf(Globals::xsl.c_str());
			if(mf.is_open())
			{
				mf << Globals::stylesheet;
				cerr << "Generated " << Globals::xsl << "\n";
			}
			else
				cerr << " ERROR: unable to open '" << Globals::xsl << "' for writing!\n";
		}
		else
			cerr << "Notice: " << Globals::xsl << " already exists, not changing anything.\n";
	}


	//Global boolean filling
	Globals::showDTD = (variableMap.count("nodtd") == 0);
	Globals::noxsl = (variableMap.count("noxsl") != 0);
	Globals::dosha1 = (variableMap.count("nosha1") == 0);
	Globals::dosha512 = (variableMap.count("nosha512") == 0);
	Globals::domd5 = (variableMap.count("nomd5") == 0);
	Globals::doed2k = (variableMap.count("noed2k") == 0);
	Globals::dognunet070 = (variableMap.count("nognunet070") == 0);

	//Digest code
	if(variableMap.count("xsl") != 0)
	{
		Globals::xsl = variableMap["xsl"].as< std::string >();
		cerr << "Set XSLT to: \'" << Globals::xsl << "\'\n";
	}
	
 	if(Globals::noxsl)
 		Globals::xsl = "";

	if(variableMap.count("input-file") == 0)
	{
		cerr << "No input files given\nTry: " << argv[0] << " -h\n";
		return 1;
	}
	
	vector<string> inputs = variableMap["input-file"].as< vector<string> >();
	bool collect = variableMap.count("stdout") != 0;
	
	if(collect)
		Metalink::insertHeader(cout);
		
	_foreach(it, inputs)
	{
		
		//Silently skip metalink files
		std::string const metalinkExtension = ".metalinks.xml";
		if(it->size() >= metalinkExtension.size()
				&&  it->compare(
						it->size() - metalinkExtension.size(),
						metalinkExtension.size(),
						metalinkExtension
						) == 0
					)
		{
			//cerr << "Skipping '" << *it << "'\n";
			continue;
		}

		boost::filesystem::path targetFile(*it, boost::filesystem::native);

		if(!boost::filesystem::exists(targetFile))
		{
			cerr << "Can't find '" << *it << "'\n";
			continue;
		}
		

		if(boost::filesystem::is_directory( targetFile ))
		{
			cerr << "Skipping directory '" << *it << "'\n";
			continue;
		}
		
		//Generate the output filename
		std::string metalinkFilename = *it;
		for(std::string::size_type i = 0; i < metalinkFilename.size(); ++i)
			if(metalinkFilename[i] == '.')
				metalinkFilename[i] = '_';
		
		metalinkFilename += ".metalinks.xml";
		
		
		boost::filesystem::path targetMetafile(metalinkFilename, boost::filesystem::native);

		if(boost::filesystem::exists( targetMetafile ) && !collect)
		{
			cerr << "Skipping '" << *it << "' because a '.metalinks.xml' already exists\n";
			continue;
		}
		
		ifstream file(it->c_str(), ios::binary);
		if(!file.is_open())
		{
			cerr << "Unable to open '" << *it << "'\n";
			continue;
		}

		
		cerr << "Hashing '" << *it << "' ... ";
		
		Metalink m(*it);
		
		HashGNUnet gnunet;
		HashED2K ed2k;
		GCrypt md5(GCRY_MD_MD5);
		GCrypt sha1(GCRY_MD_SHA1);
		GCrypt sha512(GCRY_MD_SHA512);
		
		//Fill hashes
		static unsigned const blockSize(10240);
		char data[blockSize];
		unsigned read(0);
		char const * spinner = "\\|/\\|/-";
		unsigned spini(0), spinii(0);
		unsigned long long size(0);
		cerr << " ";	//Spinner space
		while(true)
		{
			file.read(&data[0], blockSize);
			read = file.gcount();
			
			if(read == 0)
				break;
			size += read;
			
			if(++spini % 300 == 0)
				cerr << "\b" << spinner[++spinii%7];
			
			if(Globals::doed2k)
				ed2k.update(&data[0], read);
			if(Globals::domd5)
				md5.update(&data[0], read);
			if(Globals::dosha1)
				sha1.update(&data[0], read);
			if(Globals::dosha512)
				sha512.update(&data[0], read);
			if(Globals::dognunet070)
				gnunet.update(&data[0], read);
			
		}
		cerr << "\b"; //Spinner removal
		m.setSize(size);
		if(Globals::doed2k)
			ed2k.finalize();
		if(Globals::domd5)
			md5.finalize();
		if(Globals::dosha1)
			sha1.finalize();
		if(Globals::dosha512)
			sha512.finalize();
		if(Globals::dognunet070)
			gnunet.finalize();

/*		
		if(variableMap.count("source"))
			m.addSource(variableMap["source"].as< std::string >());
		if(variableMap.count("publisher") != 0)
			m.publisher(variableMap["publisher"].as< std::string >());
		
		//Default dublin core terms
		if(variableMap.count("description"))
			m.setDC("description", variableMap["description"].as< std::string >());
		if(variableMap.count("rights"))
			m.setDC("rights", variableMap["rights"].as< std::string >());
		if(variableMap.count("format"))
			m.setDC("format", variableMap["format"].as< std::string >());
*/
			
		if(Globals::doed2k)
			m.addDigest(ed2k.name(), ed2k.value());
		if(Globals::dognunet070)
		{
			std::string value = gnunet.value();
			m.addDigest("gnunet070file", value.substr(0, value.find(".")), "gnunet070");
			m.addDigest("gnunet070query", value.substr(value.find(".") + 1), "gnunet070");
		}
		if(Globals::dosha1)
			m.addDigest(sha1.name(), sha1.value());
		if(Globals::dosha512)
			m.addDigest(sha512.name(), sha512.value());
		if(Globals::domd5)
			m.addDigest(md5.name(), md5.value());
		
		
		ofstream metalinkFile;
		if(!collect)
		{
			metalinkFile.open(metalinkFilename.c_str(), ios::trunc);
			if(!metalinkFile.is_open())
			{
				cerr << "Unable to open '" << metalinkFilename << "' for output.\n";
				continue;
			}
		}
			
		if(m.ok())
		{
			if(collect)
			{
				m.insertInto(cout);
				cerr << "done\n";
			}
			else
			{
				m.insertHeader(metalinkFile);
				m.insertInto(metalinkFile);
				m.insertFooter(metalinkFile);
				metalinkFile.close();
				cerr << " written to '" << metalinkFilename << "'\n";
			}
		}
		else
		{
			cerr << "failed: no hashes available (might be empty)\n";
		}
	}//Foreach
	
	if(collect)
		Metalink::insertFooter(cout);
		
	return 0;
}
catch(const std::exception &e)
{
	cerr << "Caught std::exception (" << typeid(e).name() << "): " << e.what() << endl;
}
