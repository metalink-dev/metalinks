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



#include "SessionKey.ih"

void SessionKey::fromHash(unsigned char const*sha512hash)
{

	//Place part of hashcode in session key
  memcpy(key, sha512hash, keyLength);

	//CRC32 of HashKey
	//crc32 = HashCRC32::from(key, keyLength);

	//Copy SESSIONKEY_LEN/2 unsigned characters naar initvector
	// Begin at hc[SESSIONKEY_LEN] which is somewhere in the midle
	
	//Rest van hash naar initvector
  memcpy(initVector, &sha512hash[keyLength], initVectorLength);

}
