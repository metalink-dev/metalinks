/*
	This file is part of the metalinklinks program
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

/** \file The metalinkslinks program

	This is a "bare C++" implementation of simple Metalink uri extraction.
	
	Given a Metalink and a number of uri types, it generates a list of links
	on the stdout.
	
	Use this in combination with downloaders (like wget, gnunet-download and such) to generate
	a list of links.

	Only one link per identifier is created, so to create a list of the first http mirrors
	of the files in the Metalink, use: metalinklinks http http http http http http record.metalink
*/

#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

#include "RecordFile/RecordFile.hh"

using namespace std;
using namespace bneijt;

int main(int argc, char *argv[])
try
{
	cerr << "Warning: This program is not done yet, it will currently display all the links of all the files, not just the first x of a type.\n";
	
	if(argc < 3)
	{
		cerr << "Usage: " << argv[0] << " <type> [more types] <file.metalink>" << endl;
		return 1;
	}
	
	vector<string> types;
	string filename;

	for(int i = 0; i < argc; ++i)
		types.push_back(argv[i]);
	filename = types.back();
	types.pop_back();
	
	RecordFile metalink(filename);

	while(true)
	{
		if(metalink.eof())
			break;
			
		pair<string, string> url = metalink.between("<url type=\"", "\">", "</url>");
		if(count(types.begin(), types.end(), url.first))
			cout << url.second << endl;
	}
	
	return 0;
}
catch(const std::exception &e)
{
	cerr << "Caught std::exception (" << typeid(e).name() << "): " << e.what() << endl;
}
