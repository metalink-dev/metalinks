
#ifndef _RecordFile_HH_INCLUDED_
#define	_RecordFile_HH_INCLUDED_

#include <fstream>
#include <string>
#include <utility>

namespace bneijt
{

class RecordFile: public std::ifstream
{
	public:
		RecordFile(std::string const &filename)
			:
			std::ifstream(filename.c_str())
		{}

		bool skipTo(std::string const &val);
		
		std::pair<std::string, std::string> between(
			std::string const &a,
			std::string const &b,
			std::string const &c
		);
		
		std::string readTo(std::string const &val);
};
}
#endif

