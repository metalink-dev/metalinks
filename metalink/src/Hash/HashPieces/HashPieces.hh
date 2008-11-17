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
		HashPieces(unsigned long long size = 256*1024);
		
		~HashPieces()
		{
			_foreach(h, d_pieces)
				if(*h)
					delete *h;
			if(d_h)
				delete d_h;
		}
		
		unsigned long long size() const
		{
			return d_size;
		}
		
		virtual std::string name() const;

		virtual void update(char const *bytes, unsigned numbytes);
		
		virtual void finalize();
		
		std::string xml() const;
		
		virtual std::string const &value() const;
};
}//namespace

#endif

