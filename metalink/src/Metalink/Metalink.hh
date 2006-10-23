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

#ifndef _Metalink_HH_INCLUDED_
#define	_Metalink_HH_INCLUDED_

#include <string>
#include <sstream>
#include "../MetalinkFile/MetalinkFile.hh"
#include "../Preprocessor/foreach.hh"

namespace bneijt
{
class Metalink
{
	public:
		static std::string from(std::vector< MetalinkFile > files)
		{
			std::ostringstream out;
			out << "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
			out << "<metalink version=\"3.0\" xmlns=\"http://www.metalinker.org/\" generator=\"http://metalinks.sourceforge.net/\">\n";

 
 			out << "<files>\n";
			_foreach(file, files)
			{
				file->finalize();
				out << *file;
				out << "\n";
			}
 			out << "</files>\n";
			out << "</metalink>\n";
			return out.str();
		}
	
};
}
#endif

