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
	and then opens and handles all files.
	
	All hash classes are part of a vector created at the beginning.
	
	As the list of hashes used is still small, we'll just learn to live with it.
*/

#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>
#include <boost/program_options.hpp>
#include <boost/filesystem/operations.hpp>
#include <boost/filesystem/convenience.hpp>

#include "Metalink/Metalink.hh"
#include "MetalinkFile/MetalinkFile.hh"
#include "HashList/HashList.hh"


#include "Hash/GCrypt/GCrypt.hh"
/*
#include "Hash/HashMD5/HashMD5.hh"
#include "Hash/HashMD4/HashMD4.hh"
#include "Hash/HashED2K/HashED2K.hh"
#include "Hash/HashGNUnet/HashGNUnet.hh"
#include "Hash/HashSHA1/HashSHA1.hh"
#include "Hash/HashSHA512/HashSHA512.hh"
*/
#include "Globals/Globals.hh"
#include "String/String.hh"

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
	
/////////Program argument handling
	vector<string> inputFiles, digests;
	
	try
	{
		//Parse options
		po::options_description generalOptions("General options");
		generalOptions.add_options()
			("help,h", "Produce a help message")
			;

		po::options_description digestOptions("Digest options");
		digestOptions.add_options()
			("list", "List digest algorithms")
			("with", po::value< vector<string> >(), "Include the given digest")
			;

	  po::options_description hiddenOptions("Hidden options");
  	hiddenOptions.add_options()
    	("input-file", po::value< vector<string> >(), "Input file(s)")
	    ;
    
  	po::options_description helpOptions;
	  helpOptions.add(generalOptions).add(digestOptions);

  
	  po::options_description allOptions;
  	allOptions.add(generalOptions).add(digestOptions).add(hiddenOptions);
  
		po::positional_options_description positional;
		positional.add("input-file", -1);

		po::store(
			po::command_line_parser(argc, argv)
			.options(allOptions)
			.positional(positional)
			.run()
			,variableMap);

		po::notify(variableMap);
		
		//Handle options
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
			return 1;
		}
		
		//Verify input files
		if(variableMap.count("input-file") == 0)
		{
			cerr << "No input files given\nTry: " << argv[0] << " --help\n";
			return 1;
		} 




		//Store input files and digests for later use
		vector<string> tmp = variableMap["input-file"].as< vector<string> >();
		_foreach(i, tmp)
			inputFiles.push_back(*i);

		if(variableMap.count("with"))
		{
			vector<string> ttmp = variableMap["with"].as< vector<string> >();
			_foreach(i, ttmp)
				digests.push_back(*i);
		}


	}
  catch(exception& e)
  {
  	cerr << "error: " << e.what() << endl;
  	throw;
  }
  catch(...)
  {
  	cerr << "Exception of unknown type??" << endl;
		throw;
  }
  

  //For each file, create a record from it and add it to records.
	std::vector< MetalinkFile > records;
	_foreach(it, inputFiles)
	{
		String filename(*it);

		//Silently skip metalink files
		if(filename.endsIn(Globals::metalinkExtension))
			continue;

		boost::filesystem::path targetFile(filename, boost::filesystem::native);

		if(!boost::filesystem::exists(targetFile))
		{
			cerr << "Can't find '" << filename << "'\n";
			continue;
		}
		

		if(boost::filesystem::is_directory( targetFile ))
		{
			cerr << "Skipping directory '" << filename << "'\n";
			continue;
		}
		
		//Generate the output filename
		std::string metalinkFilename = *it;
		for(std::string::size_type i = 0; i < metalinkFilename.size(); ++i)
			if(metalinkFilename[i] == '.')
				metalinkFilename[i] = '_';
		
		metalinkFilename += Globals::metalinkExtension;
				
		boost::filesystem::path targetMetafile(metalinkFilename, boost::filesystem::native);

		if(boost::filesystem::exists( targetMetafile ))
		{
			cerr << "Skipping '" << filename << "' because a '" << Globals::metalinkExtension << "' already exists.\n";
			continue;
		}
		
		ifstream file(it->c_str(), ios::binary);
		if(!file.is_open())
		{
			cerr << "Unable to open '" << file << "'\n";
			continue;
		}

		MetalinkFile record(filename);
		cerr << "Hashing '" << filename << "' ... ";
		
		HashList hl;
		//Add needed hashes
		if(count(digests.begin(), digests.end(), "md5") > 0)
			hl.push_back(new GCrypt(GCRY_MD_MD5));

		
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
				
			//Update hashes
			hl.update(&data[0], read);
		}
		cerr << "\b"; //Spinner removal
		
		record.setSize(size);
		
		//FINALIZE
		hl.finalize();
		//Add hashes

		records.push_back(record);
		hl.destroyMembers();
		
	}//Foreach
	
	cout << Metalink::from(records);
	
	return 0;
}
catch(const std::exception &e)
{
	cerr << "Caught std::exception (" << typeid(e).name() << "): " << e.what() << endl;
}
