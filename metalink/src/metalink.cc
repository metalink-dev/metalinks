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
#include <utility>
#include <algorithm>
#include <vector>
#include <set>
#include <boost/program_options.hpp>
#include <boost/filesystem/operations.hpp>
#include <boost/filesystem/convenience.hpp>

#include "Mirror/Mirror.hh"
#include "MirrorList/MirrorList.hh"
#include "Metalink/Metalink.hh"
#include "MetalinkFile/MetalinkFile.hh"
#include "MD5File/MD5File.hh"
#include "HashList/HashList.hh"


#include "Hash/GCrypt/GCrypt.hh"
#include "Hash/HashED2K/HashED2K.hh"
#include "Hash/HashGNUnet/HashGNUnet.hh"

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
	bool allDigests(false), readMirrors(true);
	string baseUrl("");
/////////Program argument handling
	vector<string> inputFiles, md5Files;
	set<string> digests;
	
	try
	{
		//Parse options
		po::options_description generalOptions("General options");
		generalOptions.add_options()
			("help,h", "Produce a help message")
			("version", "Print out the name and version")
			("md5", po::value< vector<string> >(), "Generate metalink from md5sum file(s)")
			("baseurl", po::value< string >(),"Append a base url to the mirrors ('/' is not checked)")
			("nomirrors", "Don't read mirrors from stdin")
			;

		po::options_description digestOptions("Digest options");
		digestOptions.add_options()
			("digest,d", po::value< vector<string> >(), "Include given digest")
			("mindigests", "Include: md5 sha1")
			("somedigests", "Include: md5 sha1 ed2k gnunet")
			("alldigests", "Include all possible digests")
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
		cout << Globals::programName << " comes with ABSOLUTELY NO WARRANTY and is licensed under GPLv2\n";
		cout << "Usage:\n  " << Globals::programName << " [options] <input files | -md5> < <mirror paths> > <metalinkfile>\n";
		cout << helpOptions << "\n";
		cout << "Supported algorithms are (-d options):\n"
			<< "  md4 md5 sha1 sha256 sha384 sha512 rmd160 tiger crc32 ed2k gnunet"
			<< "\n";

		cout << "\nExample: http://example.com/ as a mirror:\n echo http http://example.com | "
				 << Globals::programName << " -d md5 -d sha1 *\n";
		cout << "Example: only P2P links:\n echo -n | "
				 << Globals::programName << " -d sha1 *\n";
			return 1;
		}
		if(variableMap.count("version"))
		{
			cout << Globals::programName << " version "
					<< Globals::version[0] << "."
					<< Globals::version[1] << "."
					<< Globals::version[2] << "\n";
			return 1;
		}		
		//Verify input files
		if(variableMap.count("input-file") == 0 && variableMap.count("md5") == 0)
		{
			cerr << "No input files or md5 flags given\nTry: " << argv[0] << " --help\n";
			return 1;
		} 




		//Store input files and digests for later use
		if(variableMap.count("input-file"))
		{
			vector<string> tmp = variableMap["input-file"].as< vector<string> >();
			_foreach(i, tmp)
				inputFiles.push_back(*i);
		}


		if(variableMap.count("md5"))
		{
			vector<string> ttmp = variableMap["md5"].as< vector<string> >();
			_foreach(i, ttmp)
				md5Files.push_back(*i);
		}

		if(variableMap.count("digest"))
		{
			vector<string> ttmp = variableMap["digest"].as< vector<string> >();
			_foreach(i, ttmp)
				digests.insert(*i);
		}
		if(variableMap.count("mindigests"))
		{
			digests.insert("md5");
			digests.insert("sha1");
		}
		if(variableMap.count("somedigests"))
		{
			digests.insert("md5");
			digests.insert("sha1");
			digests.insert("ed2k");
			digests.insert("gnunet");
		}

		if(variableMap.count("baseurl") > 0)
			baseUrl = variableMap["baseurl"].as< string >();
		
		//Simple boolean options
		allDigests = variableMap.count("alldigests") > 0;
		readMirrors = variableMap.count("nomirrors") == 0;
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
  
	//Read paths from stdin
	MirrorList mirl(cin);
	
	std::vector< pair<string,string> > paths;
	while(readMirrors)
	{
		string path;
		getline(cin, path);

		if(cin.eof())
			break;
		
		String first, second;
		string::size_type sep = path.find(' ');
		if(sep != string::npos && sep < 25)
		{
			first = path.substr(0, sep);
			second = path.substr(sep +1, path.size());
		}
		else
		{
			cerr << "Warning: No '<type> <path>' or type > 25 in mirror string, using default http type.\n";
			first = "http";
			second = path;
		}
		second.strip();
		if(not second.endsIn('/'))
			second += "/";
		//Add baseUrl
		second += baseUrl;
		paths.push_back(make_pair(first, second));
	}
	

	//Generate records
	std::vector< MetalinkFile > records;

	_foreach(md5, md5Files)
	{
		//Open and read the file
		MD5File file(*md5);
		
		pair<string, string> r;
		
		//Add the records for all paths
		while(file.record(&r))
		{
			MetalinkFile record(r.second);
			record.addVerification("md5", r.first);
			
			//Add remaining paths/mirrors
			//Remove preprended '/' and './' if needed, they should be in the mirror list
			_foreach(path, paths)
				record.addPath(path->first, path->second, r.second);

			records.push_back(record);
		}
		
		
	}

  //For each file, create a record from it and add it to records.
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
		//Known hashes: md4 md5
		if(allDigests || digests.count("md4") > 0)
			hl.push_back(new GCrypt(GCRY_MD_MD4));
		if(allDigests || digests.count("md5") > 0)
			hl.push_back(new GCrypt(GCRY_MD_MD5));

		//Known hashes: sha1 sha256 sha384 sha512
		if(allDigests || digests.count("sha1") > 0)
			hl.push_back(new GCrypt(GCRY_MD_SHA1));
		if(allDigests || digests.count("sha256") > 0)
			hl.push_back(new GCrypt(GCRY_MD_SHA256));
		if(allDigests || digests.count("sha384") > 0)
			hl.push_back(new GCrypt(GCRY_MD_SHA384));
		if(allDigests || digests.count("sha512") > 0)
			hl.push_back(new GCrypt(GCRY_MD_SHA512));

		//Known hashes: rmd160 tiger haval
		if(allDigests || digests.count("rmd160") > 0)
			hl.push_back(new GCrypt(GCRY_MD_RMD160));
		if(allDigests || digests.count("tiger") > 0)
			hl.push_back(new GCrypt(GCRY_MD_TIGER));

		//Known hashes: crc32
		if(allDigests || digests.count("crc32") > 0)
			hl.push_back(new GCrypt(GCRY_MD_CRC32));

		//Known hashes: ed2k
		if(allDigests || digests.count("ed2k") > 0)
			hl.push_back(new HashED2K());

		//Known hashes: gnunet
		if(allDigests || digests.count("gnunet") > 0)
			hl.push_back(new HashGNUnet());

		//Fill hashes
		static unsigned const blockSize(102400);
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
			
			if(++spini % 150 == 0)
				cerr << "\b" << spinner[++spinii%7];
				
			//Update hashes
			hl.update(&data[0], read);
		}
		cerr << "\b"; //Spinner removal
		
		record.setSize(size);
		
		//FINALIZE
		hl.finalize();
		//Add hashes and P2P paths
		_foreach(hp, hl)
		{
			//Only P2P link, not verify
			if((*hp)->name() == "gnunet")
			{
				record.addPath("gnunet", "gnunet://ecrs/chk/" + (*hp)->value() + "." + record.size());
				continue;
			}
			
			record.addVerification((*hp)->name(), (*hp)->value());
			
			//Add P2P specials
			if((*hp)->name() == "sha1")
				record.addPath("magnet", "magnet:?xt=urn:sha1:" + (*hp)->value() + "&amp;dn=" + filename.translated(' ', '+'));
			if((*hp)->name() == "ed2k")
				record.addPath("ed2k", "ed2k://|file|" + filename.translated('|', '_') + "|" + record.size() + "|" + (*hp)->value() + "|/");
		}
				
		//Add remaining paths/mirrors
		_foreach(path, paths)
			record.addPath(path->first, path->second, filename);
		
		records.push_back(record);
		hl.destroyMembers();
		cerr << "\n";
	}//Foreach
	
	cout << Metalink::from(records);
	
	return 0;
}
catch(const boost::program_options::unknown_option &e)
{
	cerr << e.what() << endl;
}
catch(const std::exception &e)
{
	cerr << "Caught std::exception (" << typeid(e).name() << "): " << e.what() << endl;
}
