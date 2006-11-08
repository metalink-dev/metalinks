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
	
	//Check for MD5 ( starting point
	regex md5line("MD5 ?\\(([^)]+)\\) ?= ?([a-fA-F0-9]+)");
	cmatch match;
	if(regex_match(line.c_str(), match, md5line))
	{
		_debugLevel2("openssl line");
		val->first = match[2];
		val->second = match[1];
	}
	else
	{
		_debugLevel2("md5sum line");
		if(this->eof())
			return false;
		std::string::size_type sep = line.rfind(' ');
		if(sep == std::string::npos)
			return false;
		val->first = line.substr(0, sep -1);
		val->second = line.substr(sep +1, line.size());//double space for md5 sums
	}
	_debugLevel2("MD5 (" << val->second << ") '" << val->first << "'");
	if(val->first.length() != 32)
	{
		cerr << "Warning: Unsupported MD5 line: " << line << "\n";
		cerr << "Warning: MD5 sum scanning stopped\n";
		return false;
	}
	
	return true;
}
