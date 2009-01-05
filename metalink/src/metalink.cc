/*
	This file is part of the metalink program
	Copyright (C) 2008  A. Bram Neijt <bneijt@gmail.com>

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
#include <glibmm/init.h>
#include <glibmm/optioncontext.h>
//#include <boost/program_options.hpp>
//#include <boost/filesystem/operations.hpp>
//#include <boost/filesystem/convenience.hpp>


#include "Options/Options.hh"
#include "Mirror/Mirror.hh"
#include "MirrorList/MirrorList.hh"
#include "Metalink/Metalink.hh"
#include "MetalinkFile/MetalinkFile.hh"
#include "MD5File/MD5File.hh"
#include "HashList/HashList.hh"

#include "Hash/GCrypt/GCrypt.hh"
#include "Hash/HashED2K/HashED2K.hh"
#include "Hash/HashGNUnet/HashGNUnet.hh"
#include "Hash/HashPieces/HashPieces.hh"

#include "Globals/Globals.hh"
#include "String/String.hh"
//#define DEBUGLEVEL 3
#include "Preprocessor/debug.hh"
#include "Preprocessor/os_win.hh"

#include <typeinfo>
#include <cassert>
#include <sys/stat.h>	//mkdir(2)
#include <sys/types.h> //mkdir(2)

using namespace std;
using namespace bneijt;
//namespace po = boost::program_options;

namespace {
unsigned long long file_size(std::string const &fname)
{
	struct stat info;

	if(stat(fname.c_str(),&info) == 0)
		return info.st_size;
	//Should through error	
	return 0;
}
}


int main(int argc, char *argv[])
try
{
//	po::variables_map variableMap;
	bool allDigests(false), readMirrors(true), hashList(false);
	vector<string> inputFiles, linkFiles;
	set<string> digests;

	//Program option handling
  Glib::init();
  Glib::OptionContext context;
  context.set_help_enabled(false);
  bneijt::Options options;
	Glib::OptionGroup::vecustrings &md5Files = options.opt.md5files;
	Glib::ustring &baseUrl = options.opt.addpath;
	Glib::ustring &headerFile = options.opt.headerfile;
	Glib::ustring &metalinkDescription = options.opt.desc;
	
  context.set_main_group(options);



  #ifdef GLIBMM_EXCEPTIONS_ENABLED
  try
  {
    context.parse(argc, argv);
  }
  catch(const Glib::Error& ex)
  {
    std::cout << "Exception: " << ex.what() << std::endl;
  }
  #else
  std::auto_ptr<Glib::Error> ex;
  context.parse(argc, argv, ex);
  if(ex.get())
  {
    std::cout << "Exception: " << ex->what() << std::endl;
  }
  #endif //GLIBMM_EXCEPTIONS_ENABLED


  //Input files
  for(int i = 1; i < argc; ++ i)
  	inputFiles.push_back(argv[i]);
  
		//Handle options
		if(options.opt.help)
		{
		cout << Globals::programName << " - " << Globals::programDescription << "\n";
		cout << "Version " << Globals::version[0] << "." << Globals::version[1] << "." << Globals::version[2];
		cout << ", Copyright (C) 2005 A. Bram Neijt <bneijt@gmail.com>\n";
		cout << Globals::programName << " comes with ABSOLUTELY NO WARRANTY and is licensed under GPLv3+\n";
		cout << "Usage:\n  " << Globals::programName << " [options] (input files or --md5) < (mirror list) > (metalinkfile)\n";
///TODO show help		cout << helpOptions << "\n";
    cout << context.get_help();
		cout << "Supported algorithms are (-d options):\n"
			<< "  md4 md5 sha1 sha256 sha384 sha512 rmd160 tiger crc32 ed2k gnunet sha1pieces"
			<< "\n";
		cout << "\nMirror lists are single line definitions according to:\n"
				 << " [location [preference] [type] % ] <mirror base url>\n";
		cout << "\nExamples:\n";
		cout << "http://example.com/ as a mirror:\n echo http://example.com | "
				 << Globals::programName << " -d md5 -d sha1 *\n";
		cout << "\nhttp://example.com/ as a mirror with preference and location:\n "
				 << "echo us 10 % http://example.com | " << Globals::programName << " -d md5 -d sha1 *\n";
		cout << "\nhttp://example.com/ as a mirror with preference only:\n "
				 << "echo 0 10 % http://example.com | " << Globals::programName << " -d md5 *\n";
		cout << "\nOnly P2P links:\n "
				 << Globals::programName << " --nomirrors -d sha1 -d ed2k -d gnunet *\n";
			return 1;
		}
		if(options.opt.version)
		{
			cout << Globals::programName << " version "
					<< Globals::version[0] << "."
					<< Globals::version[1] << "."
					<< Globals::version[2] << "\n";
			return 1;
		}		
		//Verify input files
		if(inputFiles.size() < 1 && md5Files.size() < 0)
		{
			cerr << "No input files or md5 flag given\nSee: " << argv[0] << " --help\n";
			return 1;
		}
		
		__foreach(i, options.opt.digests)
			digests.insert(*i);

		if(options.opt.mindigests)
		{
			digests.insert("md5");
			digests.insert("sha1");
		}
		if(options.opt.somedigests)
		{
			digests.insert("md5");
			digests.insert("sha1");
			digests.insert("ed2k");
		}
		allDigests = options.opt.alldigests;
		readMirrors = options.opt.nomirrors == false;
		
		//Simple boolean options
		hashList = options.opt.hashlist;
		if(hashList)
		{
			if(digests.size() < 1)
				cerr << "metalink: Warning: No digests given, you probably forgot the -d option." << endl;
			readMirrors = false;
		}
  

	//Read paths from stdin
	MirrorList const mirrorList(cin, baseUrl, readMirrors);
	
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
			MetalinkFile record(r.second, &mirrorList);
			record.addVerification("md5", r.first);
			records.push_back(record);
		}
		
	}

  //For each file, create a record from it and add it to records.
	_foreach(it, inputFiles)
	{
		String filename(*it);
#ifdef OS_WIN
    filename = filename.translated('\\', '/');
#endif
		//Silently skip metalink files
		if(filename.endsIn(Globals::metalinkExtension))
			continue;

		ifstream file(filename.c_str(), ios::binary);
		if(!file.is_open())
		{
			cerr << "Unable to open '" << filename << "'\n";
			continue;
		}

		_debugLevel2("\nstring------------------: " << targetFile.string()
	  	<< "\nnative_directory_string-: " << targetFile.native_directory_string()
  		<< "\nnative_file_string------: " << targetFile.native_file_string()
  		<< '\n');
  	
		MetalinkFile record(filename, &mirrorList);
		//Add matching links
		//foearch(links[filename], link) addpath basename(links)
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

		//Known hashes: pieces
		if(allDigests || digests.count("sha1pieces") > 0)
		{
			unsigned long long filesize = file_size(filename);
			
			//Small pieces => 256 kB in size.
			unsigned long long psize = 256*1024;
			
			//Larger file sizes typically have larger pieces.
			// For example, a 4.37-GB file may have a piece size of 4 MB (4096 kB)
			// To keep this while loop from going mad, we max at 16 loops
			unsigned i = 0; 
			while(filesize / psize > 255 && ++i < 16)
				psize += psize;

			hl.push_back(new HashPieces(psize));
		}
		
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
			if(hashList)
			{
				String h((*hp)->name());
				h.toUpper();
				if(h.endsIn(String("PIECES")))
				{
					//Try down cast, exceptions are just wrong, so no try block here to keep them fatal.
					HashPieces *pieces = dynamic_cast<HashPieces*>(*hp);
					cout << h << "_SIZE(" << filename << ")= " << pieces->size() << "\n";
				}
				cout << h << "(" << filename << ")= " << (*hp)->value() << "\n";
				continue;
			}
			//Only P2P link, not verify
			if((*hp)->name() == "gnunet")
			{
				record.addPath("gnunet", "gnunet://ecrs/chk/" + (*hp)->value() + "." + record.size());
				continue;
			}

			//Either make pieces a special name or add a new system for piece based hashing
			record.addVerification((*hp)->xml());
			
			//Add P2P specials
			if((*hp)->name() == "sha1")
				record.addPath("magnet", "magnet:?xt=urn:sha1:" + (*hp)->value() + "&dn=" + filename.translated(' ', '+'));
			if((*hp)->name() == "ed2k")
				record.addPath("ed2k", "ed2k://|file|" + filename.translated('|', '_') + "|" + record.size() + "|" + (*hp)->value() + "|/");
		}
				
		//Mirror list already added
		
		records.push_back(record);
		hl.destroyMembers();
		cerr << "\n";
	}//Foreach
	
	if(!hashList)
		cout << Metalink::from(records, headerFile, metalinkDescription);
	
	return 0;
}
catch(std::string const &e)
{
	cerr << "Exiting with ERRORS: " << e << endl;	
}
catch(const char*e)
{
	cerr << "Exiting with ERRORS: " << e << endl;	
}
catch(const std::exception &e)
{
	cerr << "Caught std::exception (" << typeid(e).name() << "): " << e.what() << endl;
}
