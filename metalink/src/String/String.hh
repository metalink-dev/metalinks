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

#ifndef _String_HH_INCLUDED_
#define	_String_HH_INCLUDED_

#include <string>

class String: public std::string
{
	public:
		String(std::string const & string)
		:
			std::string(string)
		{}
		
		bool endsIn(String const &ending)
		{
			return this->size() >= ending.size()
				&&  this->compare(
					this->size() - ending.size(),
					ending.size(),
					ending
					) == 0;
		}
		std::string translated(char from, char to)
		{
			std::string copy(*this);
			_foreach(c, copy)
				if(*c == from)
					*c = to;
			return copy;
		}
};

#endif

