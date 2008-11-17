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



#include "Metalink.ih"

std::string Metalink::from(std::vector< MetalinkFile > files, std::string const headerFile, std::string const desc)
{
	std::ostringstream out;
	//Root
	out << "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
	out << "<metalink version=\"3.0\"\n"
			<< "  xmlns=\"http://www.metalinker.org/\"\n"
			<< "  generator=\"http://metalinks.sourceforge.net/\"\n"
			<< "  >\n";
			
	//Header
	if(headerFile.size() > 0)
	{
		ifstream file(headerFile.c_str());
		file.unsetf(ios::skipws);
		if(file.is_open())
		{
			copy(istream_iterator<char>(file),
				istream_iterator<char>(),
				ostream_iterator<char>(out)
				);
			out << "\n";
		}
		else
		{
			cerr << "Warning: Could not open header file: " << headerFile << "\n";
			throw "Opening headerfile failed";
		}
	}
	
	if(desc.size() > 0)
		out << "\t<description>" << Globals::XMLSafe(desc) << "</description>\n";
	
	//Files section
	if(files.size() > 0)
	{
	 	out << "<files>\n";
		_foreach(file, files)
		{
			file->finalize();
			out << *file;
			out << "\n";
		}
 		out << "</files>\n";
	}
	out << "</metalink>\n";
	return out.str();
}
