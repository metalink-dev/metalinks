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

int HashCRC32::from(unsigned char const *data, unsigned len)
{
	int value;
	gcry_md_hash_buffer(GCRY_MD_CRC32, &value, data, len);
	return value;
}
//CryptoPP::HashTransformation::CalculateDigest(byte*, const byte*, unsigned
//   int)
