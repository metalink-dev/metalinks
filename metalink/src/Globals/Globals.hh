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

#ifndef _Globals_HH_INCLUDED_
#define	_Globals_HH_INCLUDED_

#include <string>
namespace bneijt
{
struct Globals
{
		static std::string const programName;
		static std::string const programDescription;
		static unsigned const version[3];
		
		static bool showDTD;
		static bool noxsl;

		static std::string xsl;
		static std::string stylesheet;
		static std::string metalinkExtension;
		
		static bool domd5;
		static bool dosha1;
		static bool dosha512;
		static bool doed2k;
		static bool dognunet070;
		};
}//namespace
#endif

