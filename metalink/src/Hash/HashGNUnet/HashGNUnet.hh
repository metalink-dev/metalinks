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

	Algorithm implementation has been partially copied and restructured
	from the GNUnetd source tree, version 0.7.0.
	Due to the translation from C to C++, the code has been intermixed.
	Although lines of the original may remain, most has been rewritten.
	
	Among the GNUnet code used are the following:
	GNUnet-0.7.0/src/applications/fs/ecrs/uri.c
		Copyright (C) 2003, 2004, 2005 Christian Grothoff (and other contributing authors)
	GNUnet-0.7.0/src/applications/fs/ecrs/upload.c
		Copyright (C) 2003, 2004, 2005 Christian Grothoff (and other contributing authors)
	
	For information on other authors, please refer to: http://www.gnunet.org
*/
#ifndef _HashGNUnet_HH_INCLUDED_
#define	_HashGNUnet_HH_INCLUDED_

#include <string>
#include <vector>

#include "SessionKey/SessionKey.hh"
namespace bneijt
{

class HashGNUnet
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
		
		std::string name(){ return "gnunet070";}
		
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
