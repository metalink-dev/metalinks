#include "RecordFile.ih"

std::string RecordFile::readTo(std::string const &val)
{
	//Read but don't destroy what is read.
	unsigned int foundIdx(0);
	std::string read;
	while(true)
	{
	
		char c;
		this->get(c);
		
		if(this->eof())
			return "";

		read += c;

		if(c == val[foundIdx])
			++foundIdx;
		
		if(foundIdx == val.size())
			break;
	}
	return read.substr(0, read.size() - val.size());
}
