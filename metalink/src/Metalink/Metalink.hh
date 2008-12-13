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





#ifndef _Metalink_HH_INCLUDED_
#define	_Metalink_HH_INCLUDED_

#include <string>
#include <vector>
#include "../MetalinkFile/MetalinkFile.hh"
#include "../Preprocessor/foreach.hh"

namespace bneijt
{

///Represents the full Metalink file, and is able to create one using it's static from member
class Metalink
{
	public:
		//Generate the Metalink XML from the given MetalinkFile s, the headerFile filename and the optional description
		static std::string from(std::vector< MetalinkFile > files,
				std::string const headerFile = "",
				std::string const desc = "");
};
}
#endif

