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

#ifndef _MD5File_HH_INCLUDED_
#define	_MD5File_HH_INCLUDED_

#include <fstream>
#include <utility>
#include <string>

namespace bneijt
{
class MD5File: std::ifstream
{
	public:
		MD5File(std::string const &filename)
			:
			std::ifstream(filename.c_str())
		{}
		
		///Pop a record from the MD5File using: md5,filename
		bool record(std::pair<std::string, std::string> *val);
};
}
#endif

