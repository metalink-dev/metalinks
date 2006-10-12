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
namespace {
unsigned char hex(char c)
{
	if (c >= '0' && c <= '9' ) //if 0 to 9
		return c - '0';            //convert to int
	
	if (c >= 'a' && c <= 'f') //if a to f
		return 10 + c -'a';
	
	if (c >= 'A' && c <= 'F') //if A to F
		return 10 + c - 'A';

	return 0;
}
void loadToFrom(unsigned char * data, std::string hash, unsigned size)
{
	for(unsigned i = 0; i < size; ++i)
	{
		data[i] = 16 * hex(hash[i*2]);
		data[i] += hex(hash[(i*2)+1]);
	}
}
}//anon namespace
//TODO optimize

void HashED2K::finalize()
{
	if(d_blockCount > 441)
		return;

	//Finalize hash
	d_md4.finalize();
	std::string value = d_md4.value();
//	transform(value.begin(), value.end(), value.begin(), toupper);
	_debugLevel2("Push" + value);
	d_hashlist.push_back(d_md4.value());
	
	//Hash the hashlist IF there are more then 1 element
	unsigned hashSize = d_hashlist[0].size() / 2;
	unsigned char hash[hashSize];
	if(d_hashlist.size() > 1)
	{
		for(unsigned i = 0; i < d_hashlist.size(); ++i)
		{
			_debugLevel2("Pop: " << d_hashlist[i] << " with size " << hashSize);
			loadToFrom(&hash[0], d_hashlist[i], hashSize);
	/*		std::cerr << "\t";
			for(unsigned i=0; i < hashSize; ++i)
				std::cerr << std::setfill('0') << std::setw(2) << std::hex << static_cast<int>(hash[i]);
			std::cerr << "\n\n";*/
			d_md4.update(reinterpret_cast<char *>(&hash[0]), hashSize);
		}
		d_md4.finalize();
		d_value = d_md4.value();
	}
	else
		d_value = d_hashlist[0];
}
