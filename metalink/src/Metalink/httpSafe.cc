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

#include "Metalink.ih"

std::string Metalink::httpSafe(std::string const &value) const
{
	//Return the HTTP safe version of a string
	
	/*Currently this is too strict, but it states:
		Space -> Plus
		[a-zA-Z0-9]	stay
		Anything else -> underscore
	*/
	std::string s(value);	//S is the safe value
	for(unsigned i = 0; i < s.size(); ++i)
	{
		if(s[i] >= 'A' && s[i] <= 'Z')
			continue;
		if(s[i] >= 'a' && s[i] <= 'z')
			continue;
		if(s[i] >= '0' && s[i] <= '9')
			continue;
		if(s[i] == ' ')
		{
			s[i] = '+';
			continue;
		}
		s[i] = '_';
	}
	return s;
}
