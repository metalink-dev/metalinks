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



#ifndef _HashGNUnet_HH_INCLUDED_
#define	_HashGNUnet_HH_INCLUDED_

#include <string>
#include <vector>

#include "SessionKey/SessionKey.hh"
namespace bneijt
{

class HashGNUnet: public Hash
{
		std::string d_value;
		
		struct CHK
		{
			unsigned char key[64];
  		unsigned char query[64];
		};
		
		
	public:
		unsigned const dBlockSize;//32768
		unsigned const ChkPerNode;//256
				
		HashGNUnet();
		~HashGNUnet();
		
		std::string name() const
		{
			return "gnunet";
		}
		
		void update(char const *bytes, unsigned numbytes);
		void finalize();
		
		std::string const &value() const;

		///\brief [0-9A-V] encoding of digest value.
		static std::string gnunettisch(unsigned char *digest);

		void pushChk(CHK const *chk, unsigned level);

		static void blockKeyAndQuery(char const *data, unsigned len, CHK *chk);
		static void blockKey(char const *data, unsigned len, CHK *chk);
		static int encryptBlock(char const *data, unsigned len, SessionKey *skey, char *out);
		
	private:
		char *d_data;
		unsigned d_read;

		class IBlock
		{
			public:
			unsigned size;
			CHK blocks[256];

				IBlock()
					:
					size(0)
				{}
		};

		std::vector<IBlock> d_iBlocks;

};
}//namespace
#endif
