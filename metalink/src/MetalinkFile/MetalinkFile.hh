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

#include <utility>
#include "../Globals/Globals.hh"
#include "../Preprocessor/foreach.hh"
/** The file segment of a metalink
*/
class MetalinkFile: public std::string
{
		std::string d_filename;
		std::vector< std::pair<std::string, std::string> > d_paths;
		bool d_sizeSet;
		unsigned long long d_size;
		std::vector< std::pair<std::string, std::string> > d_vers;
	public:
		
		MetalinkFile(std::string const &filename)
		:
			d_filename(filename),
			d_sizeSet(false),
			d_size(0)
		{}
		void setSize(unsigned long long s)
		{
			d_size = s;
			d_sizeSet = true;
		}
		std::string size() const
		{
			std::ostringstream s;
			s << d_size;
			return s.str();
		}
		void addVerification(std::string const &name, std::string const &value)
		{
			d_vers.push_back(std::make_pair(name, value));
		}
		
		///Add path of type to the uri list
		void addPath(std::string const &type, std::string const &value);
		
		///Add path and make sure to clean file from preprended slashes
		void addPath(std::string const &type, std::string const &base, std::string const & file);

		void finalize();
};

#endif

