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








#include "HashGNUnet.ih"

void HashGNUnet::update(char const *bytes, unsigned numbytes)
{
	assert(numbytes <= dBlockSize);
	
	unsigned offset = 0;

	//If we overflow
	if(numbytes + d_read > dBlockSize)
	{
		//Append data
		offset = dBlockSize - d_read;
		memcpy(&d_data[d_read], bytes, offset);
		
		//Block is now full, encrypt and push
		CHK blockchk;
		blockKeyAndQuery(d_data, dBlockSize, &blockchk);
		pushChk(&blockchk, 0);
		
		//Set the offset right, empty block
		d_read = 0;
	}

	memcpy(&d_data[d_read], &bytes[offset], numbytes - offset);

	d_read += numbytes - offset;


	//Collect blockSize data in memory
	//Push the block
	//Walk tree in finalize
}
