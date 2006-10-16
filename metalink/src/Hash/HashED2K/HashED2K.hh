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

#ifndef _HashED2K_HH_INCLUDED_
#define	_HashED2K_HH_INCLUDED_

#include <string>
#include <vector>

#include "../Hash.hh"
#include "../HashMD4/HashMD4.hh"
namespace bneijt
{
class HashED2K: public Hash
{
	// 4GB network limit is:   4290048000
	// Blocksize = 9500*1024
	// Maximum of 441 blocks
		unsigned d_count;
		unsigned d_blockCount;
		std::string d_value;
		std::vector<std::string> d_hashlist;
		HashMD4 d_md4;

	public:
		HashED2K()
			:
			d_count(0),
			d_blockCount(0),
			d_value("")
		{}
	
		std::string name() const
		{
			return "ed2k";
		}
		
		void update(char const *bytes, unsigned numbytes);
		void finalize();
		
		std::string const &value() const;
};
}//namespace
#endif

