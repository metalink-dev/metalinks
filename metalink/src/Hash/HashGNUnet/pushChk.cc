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

#include "HashGNUnet.ih"

void HashGNUnet::pushChk(CHK const *chk, unsigned level)
{

	if(level >= d_iBlocks.size())
	{
		_debugLevel1("Extending tree at " << d_iBlocks.size());
		d_iBlocks.push_back(IBlock());
	}

	_debugLevel3("Pushing CHK from " << chk << " at level " << level);
	_debugLevel4("d_iBlocks.size() == " << d_iBlocks.size());
	
	_debugLevel4("Level containing " << d_iBlocks[level].size << " blocks");
	 
	unsigned present = d_iBlocks[level].size;
	if(present >= ChkPerNode)
	{
		//Encode iblock
		//encode iblock and push to next level
		CHK blockchk;
		blockKeyAndQuery(
				reinterpret_cast<char *>(&d_iBlocks[level].blocks[0]),
				d_iBlocks[level].size * sizeof(CHK),
				&blockchk
				);
		
		//Push to next level
		pushChk(&blockchk, level + 1);
		
		present = 0;
	}
	memcpy(&d_iBlocks[level].blocks[present], chk, sizeof(CHK));
	d_iBlocks[level].size = ++present;
}
