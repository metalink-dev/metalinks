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

void HashGNUnet::blockKeyAndQuery(char const *data, unsigned len, CHK *chk)
{
	blockKey(data, len, chk);
	SessionKey skey;
	skey.fromHash(&chk->key[0]);
	char *encrypted = new char[len];

	encryptBlock(data, len, &skey, encrypted);

	HashSHA512::from(encrypted, len, chk->query);
	
	delete[] encrypted;
}
/**
 * Get the query that will be used to query for
 * a certain block of data.
 *
 * @param db the block in plaintext
 
void fileBlockGetQuery(const DBlock * db,
		       unsigned int len,
		       HashCode512 * query) {
  char * tmp;
  const char * data;
  HashCode512 hc;
  SESSIONKEY skey;
  INITVECTOR iv;

  GNUNET_ASSERT(len >= sizeof(DBlock));
  data = (const char*) &db[1];
  len -= sizeof(DBlock);
  GNUNET_ASSERT(len < MAX_BUFFER_SIZE);
  hash(data, len, &hc);	///SHA512 van datablock (len - DBlock)
  hashToKey(&hc,
	    &skey,
	    &iv);
  tmp = MALLOC(len);
  GNUNET_ASSERT(len == encryptBlock(data,
				    len,
				    &skey,
				    &iv,
				    tmp));
  hash(tmp, len, query);
  FREE(tmp);
}

*/
