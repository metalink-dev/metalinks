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
COPYING
9E4MDN4VULE8KJG6U1C8FKH5HA8C5CHSJTILRTTPGK8MJ6VHORERHE68JU8Q0FDTOH1DGLUJ3NLE99N0ML0N9PIBAGKG7MNPBTT6UKG.
1I823C58O3LKS24LLI9KB384LH82LGF9GUQRJHACCUINSCQH36SI4NF88CMAET3T3BHI93D4S0M5CC6MVDL1K8GFKVBN69Q6T307U6O.17992
*/

#include "HashGNUnet.ih"

void HashGNUnet::finalize()
{
	CHK blockchk;

	//Loftover read data encrypt and push.
	if(d_read > 0)
	{
		//Zet de rest van het datablock op null
		blockKeyAndQuery(d_data, d_read, &blockchk);
		d_read = 0;
		pushChk(&blockchk, 0);
	}
	
	//Nothing read
	if(d_iBlocks.size() == 0)
		return;
		
	//Finalize hash
	///Walk the tree!!!!!!!!!!! :-)
	
	//Walk all but last
	for(unsigned i = 0; i < d_iBlocks.size() - 1; ++i)
	{
		if(d_iBlocks[i].size == 0)
			continue;

		blockKeyAndQuery(
				reinterpret_cast<char *>(&d_iBlocks[i].blocks[0]),
				d_iBlocks[i].size * sizeof(CHK),
				&blockchk
				);
		
		pushChk(&blockchk, i + 1);
	}
	
	//If the last block contains more then one hash, walk that one to.
	if(d_iBlocks.back().size > 1)
	{
		blockKeyAndQuery(
				reinterpret_cast<char *>(&d_iBlocks.back().blocks[0]),
				d_iBlocks.back().size * sizeof(CHK),
				&blockchk
				);
		
		pushChk(&blockchk, d_iBlocks.size());		
	}
	
	
	//The last iblock must be a newly created block.
	assert(d_iBlocks.back().size == 1);

	_debugLevel2("Top(" << (d_iBlocks.size() - 1) << ")   key: " << gnunettisch(&d_iBlocks.back().blocks[0].key[0]));
	_debugLevel2("Top(" << (d_iBlocks.size() - 1) << ") query: " << gnunettisch(&d_iBlocks.back().blocks[0].query[0]));
	
	//Store result
	d_value = gnunettisch(&d_iBlocks.back().blocks[0].key[0]) + "."
			+ gnunettisch(&d_iBlocks.back().blocks[0].query[0]);
}
