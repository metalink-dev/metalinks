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
/*
	Should implement this:

	<pieces length="131072">
  <hash type="sha1" piece=”0”>example-sha1-hash</hash>
  <hash type="sha1" piece=”1”>example-sha1-hash</hash>
</pieces>

*/
#ifndef _HashPieces_HH_INCLUDED_
#define	_HashPieces_HH_INCLUDED_

#include <vector>
#include <string>

#include "../Hash.hh"

#include "../../Preprocessor/foreach.hh"

namespace bneijt
{
class HashPieces: public Hash
{
		unsigned long long d_size;
		unsigned int d_count;
		std::vector<Hash *> d_pieces;
		Hash * d_h;
		std::string d_value;
	public:
		HashPieces(unsigned int size = 131072);
		
		~HashPieces()
		{
			_foreach(h, d_pieces)
				if(*h)
					delete *h;
			if(d_h)
				delete d_h;
		}
		
		virtual std::string name() const
		{return "pieces";}
		
		virtual void update(char const *bytes, unsigned numbytes);
		
		virtual void finalize();
		
		std::string xml() const;
		
		virtual std::string const &value() const;
};
}//namespace

#endif

