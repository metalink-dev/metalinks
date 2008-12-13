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
namespace {
static char const * encTable("0123456789ABCDEFGHIJKLMNOPQRSTUV");
static unsigned char const * encTable__ = reinterpret_cast<unsigned char const *>(encTable);

}
std::string HashGNUnet::gnunettisch(unsigned char *digest)
{
  unsigned char result[104];
  unsigned char *block = digest;
  unsigned const sizeofHashCode512(64);
	unsigned int wpos = 0;
  unsigned int rpos = 0;
  unsigned int bits = 0;
  unsigned int vbit = 0;

  while ( (rpos < sizeofHashCode512) ||
	  (vbit > 0) ) {
    if ( (rpos < sizeofHashCode512) &&
	 				(vbit < 5) )
	 	{
      bits = (bits << 8) | (block)[rpos++]; /* eat 8 more bits */
      vbit += 8;
    }
    
    if (vbit < 5)
    {
      bits = bits << (5 - vbit); /* zero-padding */
      //GNUNET_ASSERT(vbit == 2); /* padding by 3: 512+3 mod 5 == 0 */
      vbit = 5;
    }
    
    //GNUNET_ASSERT(wpos < sizeof(EncName)-1);
    result[wpos++] = encTable__[(bits >> (vbit - 5)) & 31];
    vbit -= 5;
  }
  //GNUNET_ASSERT(wpos == sizeof(EncName)-1);
  //GNUNET_ASSERT(vbit == 0);
  result[wpos] = '\0';
  return std::string(reinterpret_cast<char const*>(&result[0]));
}
