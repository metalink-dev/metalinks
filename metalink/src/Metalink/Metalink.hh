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

#ifndef _Metalink_HH_INCLUDED_
#define	_Metalink_HH_INCLUDED_


#include <string>
#include <utility>
#include <vector>
#include <map>
#include <iosfwd>

namespace bneijt
{
class Metalink
{
		std::string d_filename;
		std::string d_basename;
		std::string d_pub;
		
		unsigned long long d_size;
		std::vector< std::pair<std::string, std::string> > d_digests;
		std::vector<std::string> d_sources;
		std::map<std::string, std::string> d_dcAdditions;
		
	public:
		Metalink(std::string const &filename);
		
		std::string xmlSafe(std::string const &filename) const;
		std::string httpSafe(std::string const &filename) const;
		
		void setSize(unsigned long long size)
		{
			d_size = size;
		}
		bool ok() const;
		
		void addSource(std::string const &src)
		{
			if(src.size() > 0)
				d_sources.push_back(src + d_filename);
		}
		
		void addDigest(std::string const &type, std::string const &value, std::string encoding = "")
		{
			if(value.size() > 0)
			{
				std::string att = "dtype=\"" + type + "\"";
				if(encoding.size() > 0)
					att += " encoding=\"" + encoding + "\"";
				d_digests.push_back(make_pair(att, value));
			}
		}
		
		/** Set a Dublin Core term for this records
			\param term The term name (publischer, source, etc)
			\param value The value of the term
		*/
		void setDC(std::string const &term, std::string const &value)
		{
			d_dcAdditions[term] = value;
		}
		
		std::string const &publisher(std::string const &pub = "");
		
		void insertInto(std::ostream &str, std::string const &indent = "\t") const;
		static void insertHeader(std::ostream &str, std::string const &indent = "");
		static void insertFooter(std::ostream &str, std::string const &indent = "");
};
}//Namespace

#endif

