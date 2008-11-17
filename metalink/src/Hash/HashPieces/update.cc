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


#include "HashPieces.ih"
void HashPieces::update(char const *bytes, unsigned int numbytes)
{
	//Check overflow
	//Update/finalize hash
	//Nexthash code
	if(numbytes == 0)
		return;
	
	assert(numbytes < d_size);

	//Add bytes till d_count is equal to blockSize
	if(numbytes + d_count <= d_size)
	{
		d_h->update(bytes, numbytes);
		d_count += numbytes;
	}
	else
	{
		//Write last part of blockSize, blockSize - d_count;
		unsigned int head = d_size - d_count;
		d_h->update(bytes, head);
		d_h->finalize();
		d_pieces.push_back(d_h);
		
		
		unsigned int tail = numbytes - head;
		_debugLevel2("Push with overflow " << tail);
		
		d_h = new GCrypt(GCRY_MD_SHA1);
		d_count = 0;
		this->update(bytes + head, tail);
	}
}
