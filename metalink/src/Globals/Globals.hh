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



#ifndef _Globals_HH_INCLUDED_
#define	_Globals_HH_INCLUDED_

#include <string>
namespace bneijt
{
struct Globals
{
		static std::string const programName;
		static std::string const programDescription;
		static unsigned const version[3];
		
		static std::string metalinkExtension;
		static char const dirSep;

		//XML escape functions
		static std::string XMLSafe(std::string value);
		static std::string XMLQuotedSafe(std::string value);
};
}//namespace
#endif

