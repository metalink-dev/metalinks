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



#include "Globals.ih"

std::string Globals::XMLSafe(std::string value)
{
	//Entities
	string froma[] = {
		"&",
		"<",
		">",
		""
	};
	
	string tob[] = {
		"&amp;",
		"&lt;",
		"&gt;"
	};
	
	
	for(unsigned i(0); froma[i].size(); ++i)
	{
		string const &from(froma[i]);
		string const &to(tob[i]);
		string::size_type offset(0);
		
		while(true)
		{
			string::size_type pos = value.find(from, offset);
			
			if(pos == string::npos)
				break;
			value = value.substr(0, pos) + to + value.substr(pos + from.size());
			offset += pos + to.size();
		}
	}
	return value;
}
