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
	//http://www.gtkmm.org/docs/glibmm-2.4/docs/reference/html/classGlib_1_1Regex.html
	//Check for MD5 ( starting point
	Glib::RefPtr<Glib::Regex> md5line = Glib::Regex::create("MD5 ?\\(([^)]+)\\) ?= ?([a-fA-F0-9]+)");
	if(md5line->match(line))
	{
		std::vector<std::string> tokens = md5line->split(line);
		val->first = tokens[2];
		val->second = tokens[1];
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
	
	if(val->first.length() != 32)
	{
		cerr << "Warning: Unsupported MD5 line: " << line << "\n";
		cerr << "Warning: MD5 sum scanning stopped\n";
		return false;
	}
	
	return true;
}
