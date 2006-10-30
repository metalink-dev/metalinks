#include "MirrorList.ih"

MirrorList::MirrorList(std::istream &s, std::string const &baseUrl, bool run)
{	
	if(!run)
		return;
		
	//Mirror file contains: location preference type % path
	//Initialize from stream
	string line, word;
	unsigned int mlLine(0);
	_debugLevel1("BaseUrl: " << baseUrl);
	
	while(true)
	{
		//Getlnie
		getline(s, line);
		++mlLine;
		
		if(s.eof())
				break;

		istringstream lineStream(line);
		
		//Get attributes and path
		vector<string> arg;
		String path;
		while(true)
		{
			lineStream >> word;
			if(lineStream.eof())
				break;
			if(word == "%")
				getline(lineStream, path);
			else
				arg.push_back(word);
		}
		if(path.length() == 0)
		{
			path = line;
			cerr << "Warning: No ' % ' in mirror list line " << mlLine << ", using path: " << path << "\n";
		}
		
		path.strip();
		
		//Add slash if needed
		if(not path.endsIn('/'))
			path += "/";
		
		_debugLevel1("Path: " << path);
		_debugLevel2("Attr: " << (arg.size() > 0 ? arg[0] : ""));
		_debugLevel2("Attr: " << (arg.size() > 1 ? arg[1] : ""));
		_debugLevel2("Attr: " << (arg.size() > 2 ? arg[2] : ""));
		_debugLevel2("Attr: " << (arg.size() > 3 ? arg[3] : ""));
		_debugLevel2("Attr: " << (arg.size() > 4 ? arg[4] : ""));
		
		//Add type default if possible
		std::string type;
		if(arg.size() > 2)
			type = arg[2];
		else
		{
			//Get type from path
			string::size_type i = path.find(':');
			if(i != string::npos)
				type = path.substr(0, i);
			else
			{
				cerr << "Warning: can't determine type for mirror: " << path << "\n";
			}
		}
		//Add the whole mirror information
		//Mirror file contains: location preference type % path
		//(path, preference, location, type)
		add(path + baseUrl,
			(arg.size() > 1 ? arg[1] : ""),
			(arg.size() > 0 ? arg[0] : ""),
			type			
			);
	}
}
