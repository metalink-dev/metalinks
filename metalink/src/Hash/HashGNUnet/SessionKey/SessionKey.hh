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

#ifndef _SessionKey_HH_INCLUDED_
#define	_SessionKey_HH_INCLUDED_

#include "../../HashSHA512/HashSHA512.hh"

namespace bneijt
{

static unsigned const keyLength(256/8);
static unsigned const initVectorLength(keyLength/2);

class SessionKey
{
	public:
		
		unsigned char key[keyLength];
  	//int crc32;
	  unsigned char initVector[initVectorLength];
	  
	  void fromHash(unsigned char const *sha512hash);
};
}
#endif

