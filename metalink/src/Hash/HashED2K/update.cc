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

#include "HashED2K.ih"

void HashED2K::update(char const *bytes, unsigned numbytes)
{
//ed2k links: MD4 hash of all MD4 parts in HEX string hashed
//Each part is "const unsigned int PARTSIZE = 9500*1024;" large
	unsigned int const blockSize = 9500*1024;
	assert(numbytes < blockSize);

	//Maximum of 441 blocks
	if(d_blockCount > 441)
		return;

	//Add bytes till d_count is equal to blockSize
	if(numbytes + d_count < blockSize)
	{
		d_md4.update(bytes, numbytes);
		d_count += numbytes;
	}
	else
	{
		//Write last part of blockSize, blockSize - d_count;
		unsigned head = blockSize - d_count;
		d_md4.update(bytes, head);
		d_md4.finalize();
		std::string value = d_md4.value();
//		transform(value.begin(), value.end(), value.begin(), ::toupper);
		_debugLevel2("Push " << value);
		d_hashlist.push_back(value);
		
		//Write rest to new MD4
		unsigned tail = numbytes - head;
		_debugLevel2("Overflow: " << tail);
		
		d_md4.update(bytes + head, tail);
		
		d_count = tail;
	}
}
