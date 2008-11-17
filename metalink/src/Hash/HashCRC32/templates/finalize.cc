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







#include "HashCRC32.ih"

void HashCRC32::finalize()
{
	//Finalize hash
	byte digest[d_hash.DigestSize()];
	d_hash.Final(&digest[0]);
	
	//Convert to hex
	std::ostringstream str("");
	for(unsigned i=0; i < d_hash.DigestSize(); ++i)
		str << std::setfill('0') << std::setw(2) << std::hex << static_cast<int>(digest[i]);
	
	//Store result
	d_value = str.str();
}
