#include "RecordFile.ih"

bool RecordFile::skipTo(std::string const &val)
{
	unsigned int foundIdx(0);
	while(true)
	{
	
		char c;
		this->get(c);
		
		if(this->eof())
			return false;
		
		if(c == val[foundIdx])
			++foundIdx;
		
		if(foundIdx == val.size())
			break;
	}
	return true;
}
