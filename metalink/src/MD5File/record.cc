#include "MD5File.ih"

//TODO Add support for different MD5Format:
/*
MD5 (INSTALL.i386) = 4b5397067b29d9f2659e8eb7d73bb1e1
MD5 (INSTALL.linux) = 34ab7e52e8b1ed96682349a2f0addcce
MD5 (base40.tgz) = 034057a203db7384d55eb2a01d9bcb9e
MD5 (bsd) = e8f67a2fd90f98d5b4edee9fe837c2fd	

Rewrite to detect by popping words of a line stream
*/

bool MD5File::record(std::pair<std::string, std::string> *val)
{
	std::string line;
	std::getline(*this, line);
	if(this->eof())
		return false;
	std::string::size_type sep = line.find(' ');
	if(sep == std::string::npos)
		return false;
	val->first = line.substr(0, sep);
	val->second = line.substr(sep +2, line.size());//double space for md5 sums
	return true;
}
