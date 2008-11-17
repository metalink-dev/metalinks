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

void MetalinkFile::addPath(std::string const &type, std::string const &value)
{
	d_paths.push_back(std::make_pair(type, value));
}

void MetalinkFile::addPath(std::string const &type, std::string const &base, std::string const &file)
{
	//TODO Use boost_filesystem for portability here.
	std::string cfile(file);	//Clean file
	if(cfile[0] == '.' && cfile[1] == Globals::dirSep)
		cfile = cfile.substr(1);	//The slash will be eaten below
	if(cfile[0] == Globals::dirSep)
		cfile = cfile.substr(1);
	
	d_paths.push_back(std::make_pair(type, base + cfile));
}

