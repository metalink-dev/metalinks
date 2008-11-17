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
	This code is based on code from the GNUnet project. See: www.gnunet.org
*/
#include "HashGNUnet.ih"

int HashGNUnet::encryptBlock(char const *data, unsigned len, SessionKey *skey, char *out)
{

  gcry_cipher_hd_t handle;
  int rc;
	gcry_error_t ret;
	
  rc = gcry_cipher_open(&handle,
			GCRY_CIPHER_AES256,
			GCRY_CIPHER_MODE_CFB,
			0);

  if (rc) {
    return -1;
  }

  ret = gcry_cipher_setkey(handle,
			  &skey->key[0],
			  256/8);	//TODO magic number
/*
  if (rc && ((char)rc != GPG_ERR_WEAK_KEY)) {
    gcry_cipher_close(handle);
    return -1;
  }
  */
  
  gcry_cipher_setiv(handle,
			  &skey->initVector[0],
			  256/8/2);	//TODO magic number
/*
	//TODO Handle weak keys??
  if (rc && ((char)rc != GPG_ERR_WEAK_KEY)) {
    gcry_cipher_close(handle);
    return -1;
  }
*/

	//gcry_error_t gcry_cipher_encrypt(gcry_cipher_hd_t h, unsigned char *out, size_t outsize, const unsigned char *in, size_t inlen)
  ret = gcry_cipher_encrypt(handle,
			   reinterpret_cast<unsigned char *>(out),
			   len,
			   reinterpret_cast<unsigned char const *>(data),
			   len);

  if (ret != 0) {
    gcry_cipher_close(handle);
    return -1;
  }
  
  gcry_cipher_close(handle);
  return len;
}
