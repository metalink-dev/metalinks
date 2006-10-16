#include "RecordFile.ih"

std::pair<std::string, std::string> RecordFile::between(
			std::string const &a,
			std::string const &b,
			std::string const &c
		)
{
	string first, second;
	//Find the values between a-b-c
	skipTo(a);
	first = readTo(b);
	second = readTo(c);
	return make_pair(first, second);
}
