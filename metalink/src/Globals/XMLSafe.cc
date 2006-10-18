#include "Globals.ih"

std::string Globals::XMLSafe(std::string value)
{
	//Entities
	char *froma[] = {
		"&",
		0
	};
	
	char *tob[] = {
		"&amp;",
	};
	
	for(unsigned i(0); froma[i]; ++i)
	{
		string const from(froma[i]);
		string const to(tob[i]);
		string::size_type offset(0);
		
		while(true)
		{
			string::size_type pos = value.find(from, offset);
			
			if(pos == string::npos)
				break;
			cout << static_cast<int>(pos) << " o" << from.size() << " s" << to.size() << endl;
			cout << " [" << value << "] ";
			value = value.substr(0, pos) + to + value.substr(pos + from.size());
			break;
			cout << " [" << value << "] ";
			offset += pos + to.size();
break;
		}
	}
	return value;
}
