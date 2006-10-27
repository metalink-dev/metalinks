#include "Mirror.ih"

Mirror::Mirror(std::string const &path,
	std::string const &preference,
	std::string const &location,
	std::string const &type)
	:
	d_path(path),
	d_preference(0),
	d_location(location),
	d_type(type)
{
	try
	{
		d_preference = boost::lexical_cast<unsigned int>(preference);
	}
	catch(boost::bad_lexical_cast &)
	{
		//No preference found in string, keep at 0
	}
		
}
