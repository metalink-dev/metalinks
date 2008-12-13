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




#include "MetalinkFile.ih"

void MetalinkFile::finalize()
{

	std::ostringstream record;
	record << "\t<file name=\"" << Globals::XMLQuotedSafe(d_filename) << "\">\n";
	if(d_sizeSet)
		record << "\t\t<size>" << d_size << "</size>\n";
 	record << "\t\t<verification>\n";
 	_foreach(v, d_vers)
 	{
 		record << "\t\t\t<hash type=\"" << v->first << "\">"
 			<< v->second
 			<< "</hash>\n";
 	}
 	
 	_foreach(v, d_verificationLines)
 	{
 		record << "\t\t\t" << (*v) << "\n";
 	}
 	
  record << "\t\t</verification>\n";
  record << "\t\t<resources>\n";

  _foreach(mirror, *d_ml)
  	record << "\t\t\t" << mirror->asXMLWithFile(d_filename) << "\n";
 
  _foreach(p, d_paths)
  	record << "\t\t\t<url type=\"" << p->first << "\">" << Globals::XMLSafe(p->second) << "</url>\n";
 	record << "\t\t</resources>\n";
	record << "\t</file>";
	assign(record.str());
}
