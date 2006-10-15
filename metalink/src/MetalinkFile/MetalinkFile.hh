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

#ifndef _MetalinkFile_HH_INCLUDED_
#define	_MetalinkFile_HH_INCLUDED_

#include <string>
#include <vector>
#include <sstream>

class MetalinkFile: public std::string
{
		std::string d_filename;
		std::vector<std::string> d_paths;
		unsigned long long d_size;

	public:
		
		MetalinkFile(std::string const &filename)
		:
			d_filename(filename)
		{}
		void setSize(unsigned long long s)
		{
			d_size = s;
		}
		void addPath(std::string const &path)
		{
			d_paths.push_back(path);
		}
		
		void finalize()
		{
			std::ostringstream record;
			record << "record";
			assign(record.str());
		}
};

#endif

