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

#include "Metalink.ih"

void Metalink::insertInto(std::ostream &str, std::string const &indent) const
{
	if(!ok())
		return;

	str << indent << "<metalink>\n";
	str << indent << "\t<filename>" << xmlSafe(d_filename) << "</filename>\n";
//	str << indent << "\t<filename type=\"http-safe\">" << httpSafe(d_filename) << "</filename>\n";
	str << indent << "\t<size>" << d_size << "</size>\n";

	//TODO Move to Dublin Core
	_foreach(src, d_sources)
		str << indent << "\t<dc:source>" << *src << "</dc:source>\n";
	if(!d_pub.empty())
		str << indent << "\t<dc:publisher>" << d_pub << "</dc:Publisher>\n";

	str << indent << "\t<digests>\n";
	_foreach(digest, d_digests)
	{
		str << indent << "\t\t<digest " << digest->first << ">";
		str << digest->second;
		str << "</digest>\n";
	}
	str << indent << "\t</digests>\n";
	str << indent << "</metalink>\n";
}
