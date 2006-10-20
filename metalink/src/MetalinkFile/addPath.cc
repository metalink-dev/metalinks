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

